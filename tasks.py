from contextlib import contextmanager
import csv
import datetime
import errno
import glob
import os
import sys
import zipfile

import fitparse
from invoke import run, task

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'data')

@contextmanager
def ensure_data_dir(data_dir=DEFAULT_DATA_DIR):
    try:
        os.makedirs(data_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    yield


def get_unzip_directory(path):
    bits = os.path.split(path)
    return bits[-1].replace('.zip', '')

@task
def unzip_fit_files(files, data_dir=DEFAULT_DATA_DIR):
    with ensure_data_dir(data_dir):
        for filename in glob.glob(files):
            unzip_dirname = get_unzip_directory(filename)
            unzip_path = os.path.join(data_dir, unzip_dirname)
            try:
                zf = zipfile.ZipFile(filename)
                zf.extractall(unzip_path)
            except zipfile.BadZipFile as e:
                sys.stderr.write(
                    "Could not unzip file {0}. File is not a zip file.\n".format(
                        filename))

# Timestamp fit files are seconds since December 31, 1989, which has
# this timestamp:
ORIGIN_TIMESTAMP = 631065600
UTC_OFFSET = 5

def datetime_to_timestamp(dt):
    """Convert a dateitme object to the raw timestamp value in the FIT file"""
    return dt.timestamp() - ORIGIN_TIMESTAMP 

def timestamp_to_datetime(ts):
    """Convert a timestamp from a FIT file to a datetime object"""
    return datetime.datetime.utcfromtimestamp(ORIGIN_TIMESTAMP + ts)

def get_full_timestamp(base_ts, ts16):
    """Get a full timestamp based for a 16-bit timestamp"""
    # See https://www.thisisant.com/forum/viewthread/6374/#6904
    # Swap last 16 bits of base_ts with ts16
    first_16 = base_ts & 0xffff0000
    last_16 = base_ts & 0xffff

    return first_16 | ts16


@task
def parse_heart_rate_data(files=None):
    """Parse heart rate data from FIT files"""
    if files is None:
        files = os.path.join(DEFAULT_DATA_DIR, '**/*.fit')

    fieldnames = ['date', 'time', 'heart_rate']
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)    
    writer.writeheader()

    for filename in glob.glob(files):
        fitfile = fitparse.FitFile(filename)
        last_timestamp = None

        for record in fitfile.get_messages():
            if record.name != 'monitoring':
                continue

            # Go through all the data entries in this record
            for record_data in record:
                # You can find the data message names and codes in the Excel
                # spreadsheet included with the ANT SDK
                if record_data.name == "timestamp":
                    # Record is a full timestamp.  Save this because we'll need
                    # it for calculating the full timestamp from the 16-bit
                    # ones that go with the heart rate readings
                    last_time = record_data.value
                    last_timestamp = datetime_to_timestamp(last_time)
                elif record_data.name == "unknown_26":
                    # Record is a 16-bit timestamp
                    # Try converting it to a full timestamp using the last
                    # full timestamp.
                    # Unfortunately, this doesn't always work.  Punting
                    # on this for now.
                    record_timestamp = get_full_timestamp(int(last_timestamp),
                        int(record_data.value))
                    record_time = timestamp_to_datetime(record_timestamp)
                elif record_data.name == "unknown_27":
                    # Record is heart rate (in BPM)
                    # HACK: Just use the last full timestamp value since the
                    # 16-bit timestamps are being hella weird

                    # All times in the FIT file art UTC.  Convert it to local
                    # time
                    record_time = last_time -  datetime.timedelta(hours=UTC_OFFSET)
                    writer.writerow({
                        'date': record_time.date(),
                        'time': record_time.time(),
                        'heart_rate': record_data.value,
                    })

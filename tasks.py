from contextlib import contextmanager
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

@task
def load_fit_files(files=None):
    if files is None:
        files = os.path.join(DEFAULT_DATA_DIR, '**/*.fit')

    for filename in glob.glob(files):
        fitfile = fitparse.FitFile(filename)

        for record in fitfile.get_messages():
            # Go through all the data entries in this record
            for record_data in record:
                # TODO: get only heart rate and sleep data and better understand
                # .fit file format
                # Print the records name and value (and units if it has any)
                if record_data.units:
                    print(" * {0}: {1} {2}".format(
                        record_data.name, record_data.value, record_data.units,
                        ))
                else:
                    print(" * {0}: {1}".format(record_data.name,
                        record_data.value))

Personal coffee consumption data analysis
=========================================

Analysis of my personal coffee consumption and effect on heart rate and sleep patterns for the 2016 Grown Up Science Fair.

Assumptions
-----------

* Python 3.4+

Installation
------------

    git clone https://github.com/ghing/coffee-science-fair-data.git
    mkvirtualenv coffee-science-fair-data
    cd coffee-science-fair-data
    pip install -r requirements.txt


Data pipeline
-------------

Download the zipped .fit files from the Garmin Connect website.

Extract the FIT files from the zip archives:

    inv unzip_fit_files --files='/Users/ghing/Dropbox/grown_up_science_fair/data/*.zip'

Parse heart rate data from the FIT files:

    parse_heart_rate_data --files=./data/**/*.fit > heart_rate.csv

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

Install wxPython, which *might* be needed by `matplotlib`.

    pip install --upgrade --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix

I use `matplotlib` for some exploratory charting.  The `notebook` backend shouldn't require `wxPython`, but it gives me errors when I try to use it.  So, I just installed wxPython.  Only the development version of wxPython works with Python 3, and is easily installable using pip in a virtualenv, so I used the above command to install it. wxPython might have some system-level requirements that you'll have to install with Homebrew.


Data pipeline
-------------

Download the zipped .fit files from the Garmin Connect website.

Extract the FIT files from the zip archives:

    inv unzip_fit_files --files='/Users/ghing/Dropbox/grown_up_science_fair/data/*.zip'

Parse heart rate data from the FIT files:

    parse_heart_rate_data --files=./data/**/*.fit > heart_rate.csv

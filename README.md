SponsorScrape
=====

## Author

**Elliot Miller** | *bitoffdev*

Contact me at [bitoffdev.com](http://www.bitoffdev.com/#contact) if you have
any questions about this script.

## Setup

This script was created with Python 2.7

You must have the python modules `bs4` and `requests` installed. You can get
them using pip:

    $ pip install bs4 requests

You also must make sure you have `sqlite3` installed. This should come
installed if you are on MacOS X. On Ubuntu, you can install using:

    $ apt-get insall sqlite3

## Usage

This script can scrape sponsors from Devpost to create a list of companies to
contact when trying to run a hackathon. Running the program will create a local
database that contains all the sponsors found.

## Examples

**Search Devpost's upcoming/incomplete hackathon list:**

    $ python main.py --devpost

**Search Bing for Devpost hackathon urls:** *You can get a SUBSCRIPTION_KEY
[here](https://azure.microsoft.com/try/cognitive-services/?api=bing-web-search-api).*

    $ python main.py --bing=SUBSCRIPTION_KEY

**Possible output:**

    Scraped  examplehackathon successfully
    Skipping examplehackathon -- The hackathon "examplehackathon" already exists.
    ...
    ...
    Scraped  anotherhackathon
    Scraped  andanotherhack
    ================================================================================
    TOP SPONSORS (179 hackathons analyzed)
    ================================================================================
      1. 19 sponsored by CompanyA
      2. 11 sponsored by CompanyB
      3.  9 sponsored by CompanyC
      4.  5 sponsored by CompanyD
      #.  ...
      #.  ...
     39.  2 sponsored by CompanyE
     40.  2 sponsored by CompanyF

## Intent

This repository and all its contents are intended for education value. Before
using any scripts contained within, make sure that you abide by all rules in
your relevant jurisdiction. Please be considerate of any and all third parties
that may be impacted by your use of this software.

## License

MIT License

Copyright (c) 2017 Elliot Miller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

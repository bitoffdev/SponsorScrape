#!/usr/bin/python
"""
Grab devpost urls from any iterator such as a Bing search, and then scan each
Devpost url for sponsors. Unfortunately, not all Devpost pages list their
sponsors, but this will help provide a general list of hackathon sponsors.

NOTICE: DO NOT ABUSE THIS SCRIPT! PLEASE DO NOT CAUSE AN UNDUE BURDEN ON
DEVPOST'S SERVERS, OR ANY OTHER SERVERS. MAKE SURE THAT ALL USE OF THIS SCRIPT
CONFORMS TO THE TERMS OF SERVICE LAYED OUT BY DEVPOST AND BING.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

:author: Elliot Miller
:docformat: reStructuredText
"""
from __future__ import print_function
from bs4 import BeautifulSoup
from urlparse import urlparse
import requests, sqlite3, sys, re, traceback

class SponsorDB(): 
    """
    Provides a decoupled database interface that allows the rest of the program
    to ignore the database functionality, potentially permitting a change in
    database further down the road.

    Implements a context manager. Use the `with` keyword when using this class.
    """
    def __init__(self):
        """ Sets up the database, creating a new database if necessary """
        self.DATABASE_PATH = "SponsorData.db"
        with self as db:
            db.query_db("""
            CREATE TABLE IF NOT EXISTS hackathons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devpost VARCHAR(255) UNIQUE
            );""")
            db.query_db("""
            CREATE TABLE IF NOT EXISTS sponsorship(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sponsor VARCHAR(255),
                hackathon INTEGER,
                FOREIGN KEY(hackathon) REFERENCES hackathons(id)
            );""")

    def __enter__(self):
        self.conn = sqlite3.connect(self.DATABASE_PATH)
        return self

    def __exit__(self, *args):
        self.conn.commit()
        self.conn.close()

    def query_db(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
        except sqlite3.OperationalError as err:
            print("Query Failed:", query, "--", err.message, file=sys.stderr)
            raise Exception("Query Failed:", query, "--", err.message)
        return cursor

    def hackathon_exists(self, name):
        TEMPLATE = "SELECT ID FROM hackathons WHERE devpost=\"{}\""
        if self.query_db(TEMPLATE.format(name)).fetchone():
            return True
        return False

    def sponsorship_exists(self, hackathon_pk, sponsor):
        TEMPLATE = "SELECT ID FROM sponsorship WHERE hackathon={} AND sponsor=\"{}\""
        if self.query_db(TEMPLATE.format(hackathon_pk, sponsor)).fetchone():
            return True
        return False

    def create_hackathon(self, name):
        assert (not self.hackathon_exists(name)), \
                "The hackathon \"{}\" already exists.".format(name)
        PK_QUERY = "SELECT ID FROM hackathons WHERE devpost=\"{}\""
        INSERT_QUERY = "INSERT INTO hackathons (devpost) VALUES (\"{}\")"
        self.query_db(INSERT_QUERY.format(name))
        return self.query_db(PK_QUERY.format(name)).fetchone()[0]

    def create_sponsorship(self, hackathon_pk, sponsor):
        assert not self.sponsorship_exists(hackathon_pk, sponsor), \
               "Sponsorship already exists for \"{}\" and hackathon #{}" \
               .format(sponsor, hackathon_pk)
        TEMPLATE = "INSERT INTO sponsorship (sponsor, hackathon) VALUES \
                    (\"{}\", {})"
        self.query_db(TEMPLATE.format(sponsor, hackathon_pk))

    def hackathon_count(self):
        QUERY = "SELECT count(*) FROM hackathons;"
        return self.query_db(QUERY).fetchone()[0]

    def list_top(self, limit=None):
        QUERY = "SELECT sponsor, COUNT(sponsor) AS cnt FROM sponsorship \
        GROUP BY sponsor ORDER BY cnt DESC;"
        cursor = self.query_db(QUERY)
        i=1
        for row in cursor:
            print("{:3d}.{:3d} sponsored by {}".format(i, row[1], row[0]))
            if limit and i >= limit:
                return
            i += 1

def scrape_devpost_sponsors(devpost_name):
    """
    Scrape the sponsors from a devpost page

    :param devpost_name: host of devpost url
    :return: list of sponsor names
    """
    # Get the sponsors from the url
    url = "https://{}.devpost.com/".format(devpost_name)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sponsor_images = soup.find_all("img", attrs={"class": "sponsor_logo_img"})
    sponsors = []
    for img in sponsor_images:
        if "alt" in img.attrs:
            sponsors.append(img["alt"])
    # Return the sponsors
    return sponsors

def main(devpost_names):
    """
    Runs through a collection of devpost names and tries to scrape the devpost
    page for each, creating a database entry for each one.

    :param devpost_names: Iterator object that yields devpost names
    :return: None
    """
    with SponsorDB() as db:
        for devpost_name in devpost_names:
            try:
                hackathon_pk = db.create_hackathon(devpost_name)
                for s in scrape_devpost_sponsors(devpost_name):
                    db.create_sponsorship(hackathon_pk, s)
                print("Scraped ", devpost_name, "successfully", file=sys.stderr)
            except AssertionError as err:
                print("Skipping", devpost_name, "--", err.message, file=sys.stderr)
            except Exception as err:
                print("Error w/", devpost_name, "--", err.message, file=sys.stderr)
                traceback.print_exc()
            sys.stderr.flush()
        print("="*80, "TOP SPONSORS ({} hackathons analyzed)" \
              .format(db.hackathon_count()), "="*80, sep="\n")
        db.list_top()

def devpost_generator():
    """
    Scrapes hackathon names from devposts incomplete hackathon list

    :return: Iterator that yields string devpost names
    """
    PAGE_TEMPLATE = "https://devpost.com/hackathons?page={:d}"
    for i in range(5):
        response = requests.get(PAGE_TEMPLATE.format(i))
        soup = BeautifulSoup(response.text, 'html.parser')
        hackathons = soup.find_all("a", attrs={"href":
                                re.compile("^https?:\/\/.*\.devpost\.com.*$")})
        for anchor in hackathons:
            components = urlparse(anchor["href"])
            devpost_name = components.netloc.split(".")[0]
            if not devpost_name in ["secure", "help", "info", "post"]:
                yield devpost_name

def bing_generator(subkey, limit=150, start=0):
    """
    Uses the Bing search API to get all crawled Devpost urls. This should be
    around 700 in total as of summer 2017.

    :param subkey: Bing Web Search subscription key
    :param limit: Cap the number of devpost names
    :param start: What offset to start at in the Bing search results
    :return: Iterator that yields string devpost names
    """
    PAGE_TEMPLATE = "https://api.cognitive.microsoft.com/bing/v5.0/search"
    pages_read = 0
    page_size = 50
    total_matches = 100 # Arbitrary number bigger than page size
    while pages_read * page_size < min(total_matches, limit):
        response = requests.get(PAGE_TEMPLATE, params={"q": "site:devpost.com",
                                "count": page_size,
                                "offset": start + pages_read * page_size,
                                "responseFilter": "Webpages"}, headers={
                                "Ocp-Apim-Subscription-Key": subkey })
        json = response.json()
        total_matches = json["webPages"]["totalEstimatedMatches"]
        for page in json["webPages"]["value"]:
            url = page["displayUrl"]
            components = urlparse(page["displayUrl"])
            devpost_name = components.netloc.split(".")[0]
            if not devpost_name in ["devpost","secure","help","info","post"]:
                yield devpost_name
        pages_read += 1

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main([])
    elif len(sys.argv) == 2 and sys.argv[1] == "--devpost":
        main(devpost_generator())
    elif len(sys.argv) == 2 and sys.argv[1][:7] == "--bing=":
        main(bing_generator(sys.argv[1][7:]))
    else:
        print("usage: $ python main.py [--devpost] [--bing=XXXXXXXXXXXXXXXXX"+\
              "XXXXXXXXXXXXXXX]")

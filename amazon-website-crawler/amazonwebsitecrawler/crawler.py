#!/usr/bin/python

"""
Created on Feb 19, 2014

@author: nay

This small crawler visits and saves product web pages from the Amazon Website
which can later be parsed to extract all sorts of interesting information.

As someone else stated on their own crawler: I provide you the tool to
download the product data, not the right to download it. You have to
respect Amazon’s rights on its own data. Do not release the data you 
download without Amazon’s consent.

USAGE:
./crawler.py --start START_URL [--todir DIRECTORY]

DESCRIPTION:
In order to call this script you need to pass it a valid url in which to start
The START_URL is valid if it has the following properties:
- It starts with 'http://www.amazon.com'
- And includes '/dp/' followed by the product ID
  Example: 'http://www.amazon.com/Nintendo-3DS-XL-Black/dp/B00E1A1SP6'

Subsequent urls to be visited follow the same pattern.

The script will automatically download a copy of every page that it visits.
By default the pages will be saved to the current directory, you can specify 
the download path by passing the arguments: '--todir <DIRECTORY>' to the 
script. The pages will be named the same as the product ID they belong to.

Examples:

./crawler.py --start http://www.amazon.com/The-Legend-Zelda-Between-nintendo\
-3ds/dp/B00GANWVJE/

./crawler.py --start http://www.amazon.com/dp/B00GANWVJE --todir archive
"""

import sys
import re
import os
import robotparser
import urllib2
from urlparse import urljoin
from HTMLParser import HTMLParser
from HTMLParser import HTMLParseError
from crawlerdb import ProductDb

SITE_NAME = 'http://www.amazon.com'
# make sure we follow the robots exclusion standard
# http://en.wikipedia.org/wiki/Robots_Exclusion_Standard
ROBOTS_FILE = 'https://www.amazon.com/robots.txt'

class MyHTMLParser(HTMLParser):
    """Creates an HTMLParser subclass and overrides the handler methods."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.pattern = re.compile('/.+/dp/(.+)')
        self.urls = {}

    def handle_starttag(self, tag, attrs):
        """Searches for urls that follow the pattern described at the
           beginning of this module.
         """
        if tag == 'a':
            for name, val in attrs:
                if name == 'href':
                    match = self.pattern.match(val)
                    if match:
                        self.urls[match.group(1)] = urljoin(SITE_NAME, val)

    def get_urls(self):
        """Returns the found urls."""
        return self.urls.items()

    def reset_urls(self):
        """Deletes the urls found in the previous call to parser.feed."""
        self.urls = {}


def crawl(start, path):
    """Crawls Amazon product web pages."""

    # initialize html parser
    parser = MyHTMLParser()

    # initialize ProductDB database structure
    crawler_db = ProductDb()
    crawler_db.enqueue(start)

    # initialize robotparser
    robot_parser = robotparser.RobotFileParser()
    robot_parser.set_url(ROBOTS_FILE)
    robot_parser.read()

    # it will continue crawling while there are
    # pages in the database that have not been visited
    # use crawler_db.urls_visited() < N to limit the
    # number of pages that can be visited
    while not crawler_db.empty() and crawler_db.urls_visited() < 10:
        #get next url to crawl
        (product_id, url) = crawler_db.dequeue()
        print 'url: ', url

        # check if the url is allowed to be fetched in the robots.txt
        if not robot_parser.can_fetch('*', url.encode('ascii', 'replace')):
            print 'Disallowed url: ', url
            continue

        # initialize url request
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'crawler 1.0')

        # fetch url and check for exceptions
        # if exceptions occur fetch next url
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError as err:
            print 'Exception at: ', url
            if hasattr(err, 'reason'):
                print 'Reason: ', err.reason
            elif hasattr(err, 'code'):
                print 'Error code: ', err.code
            continue
        data = response.read()

        # parse the html source of the recently fetched url
        try:
            parser.feed(data.decode('utf-8', 'replace'))
        except HTMLParseError as err:
            print 'Exception at: ', url
            print err
            continue

        # save on disk the html source of the web page
        with open(os.path.join(path, product_id), 'w') as flocal:
            flocal.write(data)
            flocal.close()

        # add to the database the product urls found in the html
        for url_data in parser.get_urls():
            crawler_db.enqueue(url_data)
        parser.reset_urls()

def get_path(todir):
    """Returns directory todir absolute path."""
    path = os.path.abspath(todir)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path

def main():

    # check for program arguments
    usage = 'usage: --start url [--todir dir]'
    args = sys.argv[1:]
    if not args:
        print usage
        sys.exit(1)

    # get product url argument to start the crawler
    url = ''
    if args[0] == '--start':
        if len(args) < 2:
            print usage
            sys.exit(1)
        url = args[1]
        del args[0:2]

    # get directory to save the visited web pages
    todir = '.'
    if len(args) > 0 and args[0] == '--todir':
        if len(args) < 2:
            print usage
            sys.exit(1)
        todir = args[1]
        del args[0:2]

    # check exact number of arguments
    if len(args):
        print "error: wrong arguments"
        print usage
        sys.exit(1)

    # get product id of the starting product url
    path = get_path(todir)
    match = re.match(SITE_NAME + '(.*?)/dp/(.+?)(/|$)', url)

    if match:
        start = (match.group(2), url)
        try:
            # start the crawler
            crawl(start, path)
        except KeyboardInterrupt:
            print 'Stopped (KeyboardInterrupt)'
            sys.exit(1)
        except Exception as err:
            print err
    else:
        print "error: invalid url"
        print usage
        sys.exit(1)

if __name__ == '__main__':
    main()

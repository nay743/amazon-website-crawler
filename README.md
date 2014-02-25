amazon-website-crawler
======================

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

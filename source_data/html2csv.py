#!/usr/bin/env python3
"""
Extract the first HTML document from a project light web-page as CSV.

Usage:
    h2ml2csv.py (-h | --help)
    h2ml2csv.py [--output=FILE] <input>

Options:

    --output=FILE, -o=FILE      Write output to FILE. If "-", use standard output. [default: -]

"""
import csv
import sys

import bs4
import docopt


def main():
    # Parse command line options
    opts = docopt.docopt(__doc__)

    # Load HTML file
    with open(opts['<input>']) as f:
        soup = bs4.BeautifulSoup(f, 'html5lib')

    # Find table
    table = soup.find('div', class_='content').find('table')

    if opts['--output'] is None or opts['--output'] == '-':
        write_table(table, sys.stdout)
    else:
        with open(opts['--output'], 'w') as f:
            write_table(table, f)


def write_table(table, fobj):
    writer = csv.writer(fobj)

    writer.writerow(th.text for th in table.find('thead').find_all('th'))
    writer.writerows(
        (td.text.strip() for td in tr.find_all('td'))
        for tr in table.find('tbody').find_all('tr')
    )


if __name__ == '__main__':
    main()

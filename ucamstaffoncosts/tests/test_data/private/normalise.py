#!/usr/bin/env python3
"""
Normalise data read from standard input as a TSB into a CSV file on standard
output.

The following normalisation is used:

    1. Blank lines are skipped
    2. Whitespace characters surrounding cell entries is stripped
    3. Commas are stripped
    4. Leading zeros are stripped

"""

import csv
import sys


def normalise(cell):
    return cell.strip().replace(',', '').lstrip('0')


def main():
    reader = csv.reader(sys.stdin, dialect='excel-tab')
    writer = csv.writer(sys.stdout)
    writer.writerows([normalise(cell) for cell in row] for row in reader if len(row) > 0)


if __name__ == '__main__':
    main()

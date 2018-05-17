#!/usr/bin/env python3
"""
Extract salary spine from spine Excel sheet.
"""
import csv
import re
import sys


def main():
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout)

    writer.writerow(['Scale point', 'Salary (£)'])

    for row in reader:
        # Extract values
        try:
            spine_point_1, spine_point_2 = row[2], row[-3]
            base_salary = row[-1]
        except IndexError:
            continue

        # We detect salary rows becausse the spine point is repeated...
        if spine_point_1 != spine_point_2:
            continue

        # ...and it is numeric
        if not re.match('^[0-9]+$', spine_point_1):
            continue

        # Strip characters from salary
        base_salary = base_salary.replace(',', '')
        base_salary = base_salary.replace('£', '')

        writer.writerow([spine_point_1, base_salary])


if __name__ == '__main__':
    main()

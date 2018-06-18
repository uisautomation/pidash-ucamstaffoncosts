#!/usr/bin/env python3
"""
Merge clinical salary scales into the salary scales file

Usage:
    ./clinical_scales.py (-h | --help)
    ./clinical_scales.py [--output=FILE]

Options:

    --output=FILE, -o=FILE      Write output to FILE. If "-", use standard output. [default: -]

"""
import csv
import datetime
import sys

import docopt
import yaml


CLINICAL_NODAL_POINTS = 'clinical-nodal-points.csv'

CLINICAL_CONSULTANT_POINTS = 'clinical-consultants.csv'

CLINICAL_RA_AND_LECTURER_POINTS = 'clinical-research-associates-and-clinical-lecturers.csv'

EFFECTIVE_DATE = datetime.date(2017, 4, 1)


def main():
    opts = docopt.docopt(__doc__)

    points = {}
    grades = []

    with open(CLINICAL_NODAL_POINTS) as fobj:
        reader = csv.reader(fobj)

        # Sanity check headings
        headings = next(reader)
        assert headings[1] == 'Salary (£)'

        scale = []
        for point, salary_txt in reader:
            salary = int(salary_txt.replace(',', ''))
            point_name = f'NODE_{point}'
            points[point_name] = salary
            scale.append({'isContribution': True, 'name': point_name, 'point': point_name})
        grades.append({'name': 'CLINICAL_NODAL', 'scale': scale})

    with open(CLINICAL_CONSULTANT_POINTS) as fobj:
        reader = csv.reader(fobj)

        # Sanity check headings
        headings = next(reader)
        assert headings[3].startswith('Basic salary at April ' + str(EFFECTIVE_DATE.year))

        scale = []
        prev_threshold = ''
        for this_threshold, years, _, salary_txt, _ in reader:
            if this_threshold == '':
                threshold = prev_threshold
            else:
                threshold = this_threshold
            salary = int(salary_txt.replace(',', ''))
            point_name = f'CONSULTANT_THRESH_{threshold}_YEAR_{years}'
            points[point_name] = salary
            scale.append({'isContribution': True, 'name': point_name, 'point': point_name})
            prev_threshold = threshold
        grades.append({'name': 'CLINICAL_CONSULTANT', 'scale': scale})

    with open(CLINICAL_RA_AND_LECTURER_POINTS) as fobj:
        reader = csv.reader(fobj)

        # Sanity check headings
        headings = next(reader)
        assert headings[1] == 'Salary (£)'

        scale = []
        for point, salary_txt in reader:
            salary = int(salary_txt.replace(',', ''))
            point_name = f'RA_LECTURER_{point}'
            points[point_name] = salary
            scale.append({'isContribution': True, 'name': point_name, 'point': point_name})
            prev_threshold = threshold
        grades.append({'name': 'CLINICAL_RA_AND_LECTURER', 'scale': scale})

    data = {
        'grades': grades,
        'salaries': [
            {
                'effectiveDate': EFFECTIVE_DATE,
                'mapping': points,
            },
        ],
    }

    output = yaml.dump(data)
    if opts['--output'] is None or opts['--output'] == '-':
        sys.stdout.write(output)
    else:
        with open(opts['--output'], 'w') as fobj:
            fobj.write(output)


if __name__ == '__main__':
    main()

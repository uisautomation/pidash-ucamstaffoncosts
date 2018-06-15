import csv
import hashlib
import io
import os
import unittest.mock as mock

import nose.tools

import ucamstaffoncosts.costs as costs


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),  'test_data')
PUBLIC_DATA_DIR = os.path.join(TEST_DATA_DIR, 'public')
PRIVATE_DATA_DIR = os.path.join(TEST_DATA_DIR, 'private')


# Load the SHA256 hashes of the correct tables from the private data directory. A dictionary keyed
# by original file name giving the hash of the correct file.
PRIVATE_DATA_HASHES = dict(
    line.split()[::-1] for line in open(os.path.join(PRIVATE_DATA_DIR, 'on-costs-hashes.txt'))
)


def test_not_implemented_scheme():
    """Check NotImplementedError is raised if the scheme is unknown."""

    with nose.tools.assert_raises(NotImplementedError):
        # Bad year
        costs.calculate_cost(100, -1000, costs.Scheme.USS)

    with nose.tools.assert_raises(NotImplementedError):
        # Bad year
        costs.calculate_cost(100, 2018, 'this-is-not-a-pension-scheme')


def test_no_scheme_2018():
    """Check on-costs if employee has no pension scheme."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.NONE, 2018),
        'no_scheme_2018.csv', with_exchange_column=True)


def test_uss_2018():
    """Check on-costs if employee has a USS scheme."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.USS, 2018),
        'uss_2018.csv')


def test_uss_2018_exchange():
    """Check on-costs if employee has a USS scheme with salary exchange."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.USS_EXCHANGE, 2018),
        'uss_exchange_2018.csv', with_exchange_column=True)


def test_cps_hybrid_2018():
    """Check on-costs if employee has a CPS hybrid scheme."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.CPS_HYBRID, 2018),
        'cps_hybrid_2018.csv', with_exchange_column=True)


def test_cps_hybrid_2018_exchange():
    """Check on-costs if employee has a CPS hybrid scheme with salary exchange."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.CPS_HYBRID_EXCHANGE, 2018),
        'cps_hybrid_exchange_2018.csv', with_exchange_column=True)


def test_nhs_2018():
    """Check on-costs if employee has a NHS scheme."""
    assert_generator_matches_table(
        lambda s: costs.calculate_cost(s, costs.Scheme.NHS, 2018),
        'nhs_2018.csv', with_exchange_column=True)


def test_mrc_2018():
    """Check on-costs are returned for MRC."""
    # We have no ground truth for MRC unfortunately so we check that NotImplementedError is not
    # raised and a result is returned.
    result = costs.calculate_cost(40000, costs.Scheme.MRC, 2018)
    nose.tools.assert_equal(result.salary, 40000)
    nose.tools.assert_greater(result.total, result.salary)


def test_default_scheme():
    """Check on-costs for default scheme and year"""
    with mock.patch('ucamstaffoncosts.costs._LATEST_TAX_YEAR', 2018):
        assert_generator_matches_table(
            lambda s: costs.calculate_cost(s, costs.Scheme.NHS),
            'nhs_2018.csv', with_exchange_column=True)


def assert_generator_matches_table(on_cost_generator, table_filename, with_exchange_column=False):
    """
    Take a generator callable which returns an OnCost from a base salary and check that its output
    matches a HR table. *table_filename* should be the HR table filename and *with_exchange_column*
    indicates if that table has an Exchange column.

    """
    headings, spine_rows = read_spine_points()

    if with_exchange_column:
        headings.append('Exchange (£)')

    headings.extend([
        'Pension (£)', 'NI (£)', 'Apprenticeship Levy (£)', 'Total (£)'
    ])

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headings)

    for point, base_salary in spine_rows:
        on_cost = on_cost_generator(int(base_salary))

        row = [point, base_salary]

        if with_exchange_column:
            row.append(blank_if_zero(on_cost.exchange))

        row.extend([
            blank_if_zero(on_cost.employer_pension),
            blank_if_zero(on_cost.employer_nic),
            blank_if_zero(on_cost.apprenticeship_levy),
            blank_if_zero(on_cost.total),
        ])

        writer.writerow(row)

    assert_tables_match(out.getvalue().encode('utf8'), table_filename)


def assert_tables_match(table_contents, filename):
    """
    Assert that a generate table matches the one specified by filename. *table* must be a bytes
    object.

    """
    expected_hash, expected_table_contents = read_table(filename)

    # If we have the expected table, compare it directly.
    if expected_table_contents is not None:
        # Compare line-wise
        for line, expected_line in zip(table_contents.decode('utf8').splitlines(),
                                       expected_table_contents.decode('utf8').splitlines()):
            nose.tools.assert_equal(line, expected_line)

        # Compare byte-wise
        nose.tools.assert_equal(table_contents, expected_table_contents)

    # Compare the hashes
    table_hash = hashlib.sha256(table_contents).hexdigest()
    nose.tools.assert_equal(table_hash, expected_hash)


def read_spine_points():
    """
    Return table header and a sequence of rows from the spine points table.

    """
    with open(os.path.join(PUBLIC_DATA_DIR, 'spine_points_august_2017.csv')) as f:
        reader = csv.reader(f)
        headings = next(reader)
        return headings, list(reader)


def read_table(filename):
    """
    Return the hash of the filename and its contents if present in the TEST_DATA_DIR directory. If
    the file is not present, the contents are returned as None.

    The file itself may not be present as the contents are private.

    """
    hash_value = PRIVATE_DATA_HASHES[filename]
    abs_path = os.path.join(PRIVATE_DATA_DIR, filename)

    # Return hash file contents if the file can be read, otherwise return hash and None.
    try:
        with open(abs_path, 'rb') as f:
            return hash_value, f.read()
    except IOError:
        return hash_value, None


def blank_if_zero(value):
    """
    Helper function to return the string representation of a value or the blank string if the
    value is zero.

    """
    return str(value) if value != 0 else ''

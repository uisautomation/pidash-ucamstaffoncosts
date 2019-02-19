import fractions
import math

from . import rates


def _make_nic_calculator(boundaries):
    """
    Return a NIC calculator which implements the usual method of calculation where NICs are
    calculated on different salary bands with differing rates.

    Returns a function which takes a base salary as input and returns the employer NIC.

    """
    def calculate(base_salary):
        # Make sure base salary is rational
        base_salary = fractions.Fraction(base_salary)

        # Keep track of bottom of current boundary
        boundary_bottom = fractions.Fraction(0)

        # Keep track of total NIC
        contribution = fractions.Fraction(0)

        for boundary_top, rate in boundaries:
            # Note: boundary_top being None signals "infinity"

            if boundary_top is not None and base_salary >= boundary_top:
                # Salary entirely encompasses this entire range
                contribution += (boundary_top-boundary_bottom) * rate
            elif base_salary > boundary_bottom and (boundary_top is None
                                                    or base_salary < boundary_top):
                # Salary is in top-most range
                contribution += (base_salary-boundary_bottom) * rate

            boundary_bottom = boundary_top

        return contribution

    return calculate


#: Table A employer NICs keyed by tax year.
#: https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2018-to-2019#paye-tax-and-class-1-national-insurance-contributions # noqa: E501
TABLE_A_EMPLOYER_NIC = {
    2018: _make_nic_calculator((
        (6032, 0),
        (8424, 0),
        (46350, fractions.Fraction(138, 1000)),
        (None, fractions.Fraction(138, 1000)),
    )),
    2019: _make_nic_calculator((
        (6136, 0),
        (8632, 0),
        (50000, fractions.Fraction(138, 1000)),
        (None, fractions.Fraction(138, 1000)),
    )),
}


def standard_apprenticeship_levy(base_salary):
    """
    Return the standard Apprenticeship Levy assuming no special circumstances. Note that HR round
    this figure *down* in on-costs tables.

    """
    return math.floor(base_salary * rates.APPRENTICESHIP_LEVY_RATE)

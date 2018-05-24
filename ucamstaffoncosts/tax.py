import fractions
import math

from . import rates


def _make_nic_calculator(boundaries):
    """
    Return a NIC calculator which implements the usual method of calculation where NICs are
    calculated on different salary bands with differing rates.

    Returns a function which takes a gross salary as input and returns the employer NIC.

    """
    def calculate(gross_salary):
        # Make sure gross salary is rational
        gross_salary = fractions.Fraction(gross_salary)

        # Keep track of bottom of current boundary
        boundary_bottom = fractions.Fraction(0)

        # Keep track of total NIC
        contribution = fractions.Fraction(0)

        for boundary_top, rate in boundaries:
            # Note: boundary_top being None signals "infinity"

            if boundary_top is not None and gross_salary >= boundary_top:
                # Salary entirely encompasses this entire range
                contribution += (boundary_top-boundary_bottom) * rate
            elif gross_salary > boundary_bottom and (boundary_top is None
                                                     or gross_salary < boundary_top):
                # Salary is in top-most range
                contribution += (gross_salary-boundary_bottom) * rate

            boundary_bottom = boundary_top

        return contribution

    return calculate


#: Table A employer NICs keyed by tax year.
TABLE_A_EMPLOYER_NIC = {
    2018: _make_nic_calculator((
        (6032, 0),
        (8424, 0),
        (46350, fractions.Fraction(138, 1000)),
        (None, fractions.Fraction(138, 1000)),
    )),
}


def standard_apprenticeship_levy(gross_salary):
    """
    Return the standard Apprenticeship Levy assuming no special circumstances. Note that HR round
    this figure *down* in on-costs tables.

    """
    return math.floor(gross_salary * rates.APPRENTICESHIP_LEVY_RATE)

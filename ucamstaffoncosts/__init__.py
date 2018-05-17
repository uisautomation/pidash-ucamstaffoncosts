import collections
import enum
import fractions
import math

from . import tax
from . import pension

_OnCost = collections.namedtuple(
    'OnCost',
    'salary exchange employer_pension employer_nic apprenticeship_levy total'
)


class OnCost(_OnCost):
    """An individual on-costs calculation for a gross salary.

    .. note::

        These values are all rounded to the nearest pound and so total may not be the sum of all
        the other fields.

    .. py:attribute:: salary

        Gross salary for the employee.

    .. py:attribute:: exchange

        Amount of gross salary exchanged as part of a salary exchange pension. By convention, this
        value is negative if non-zero.

    .. py:attribute:: employer_pension

        Employer pension contribution including any salary exchange amount.

    .. py:attribute:: employer_nic

        Employer National Insurance contribution

    .. py:attribute:: apprenticeship_levy

        Share of Apprenticeship Levy from this employee

    .. py:attribute:: total

        Total on-cost of employing this employee. See note above about situations where this value
        may not be the sum of the others.

    """


class Scheme(enum.Enum):
    """
    Possible pension schemes an employee can be a member of.

    """

    #: No pension scheme.
    NONE = 'none'

    #: CPS hybrid
    CPS_HYBRID = 'cps_hybrid'

    #: CPS hybrid with salary exchange
    CPS_HYBRID_EXCHANGE = 'cps_hybrid_exchange'

    #: USS
    USS = 'uss'

    #: USS with salary exchange
    USS_EXCHANGE = 'uss_exchange'

    #: NHS
    NHS = 'nhs'


#: Special value to pass to :py:func:`~.on_cost` to represent the latest tax year which has an
#: implementation.
LATEST = 'LATEST'


def on_cost(gross_salary, scheme, year=LATEST):
    """
    Return a :py:class:`OnCost` instance given a tax year, pension scheme and gross salary.

    :param int year: tax year
    :param Scheme scheme: pension scheme
    :param int gross_salary: gross salary of employee

    :raises NotImplementedError: if there is not an implementation for the specified tax year and
        pension scheme.

    """
    year = _LATEST_TAX_YEAR if year is LATEST else year

    try:
        calculator = _ON_COST_CALCULATORS[year][scheme]
    except KeyError:
        raise NotImplementedError()

    return calculator(gross_salary)


def _on_cost_calculator(employer_nic_cb,
                        employer_pension_cb=lambda _: 0,
                        exchange_cb=lambda _: 0,
                        apprenticeship_levy_cb=tax.standard_apprenticeship_levy):
    """
    Return a callable which will calculate an OnCost entry from a gross salary. Arguments which are
    callables each take a single argument which is a :py:class:`fractions.Fraction` instance
    representing the gross salary of the employee. They should return a
    :py:class:`fractions.Fraction` instance.

    :param employer_pension_cb: callable which gives employer pension contribution from gross
        salary.
    :param employer_nic_cb: callable which gives employer National Insurance contribution from
        gross salary.
    :param exchange_cb: callable which gives amount of salary sacrificed in a salary exchange
        scheme from gross salary.
    :param apprenticeship_levy_cb: callable which calculates the Apprenticeship Levy from gross
        salary.

    """
    def on_cost(gross_salary):
        # Ensure gross salary is a rational
        gross_salary = fractions.Fraction(gross_salary)

        # We use the convention that the salary exchange value is negative to match the exchange
        # column in HR tables.
        exchange = -exchange_cb(gross_salary)

        # The employer pension contribution is the contribution based on gross salary along with
        # the employee contribution sacrificed from their salary.
        employer_pension = employer_pension_cb(gross_salary) - exchange

        # the taxable salary is the gross less the amount sacrificed. HR would appear to round the
        # sacrifice first
        taxable_salary = gross_salary + _excel_round(exchange)

        # The employer's NIC is calculated on the taxable salary.
        employer_nic = employer_nic_cb(taxable_salary)

        # The Apprenticeship Levy is calculated on the taxable salary.
        apprenticeship_levy = apprenticeship_levy_cb(taxable_salary)

        # The total is calculated using the rounded values.
        total = (
            _excel_round(gross_salary)
            + _excel_round(exchange)
            + _excel_round(employer_pension)
            + _excel_round(employer_nic)
            + _excel_round(apprenticeship_levy)
        )

        # Round all of the values. Note the odd rounding for exchange. This matters since the
        # tables HR generate seem to include -_excel_round(-exchange) even though the total column
        # is calculated using _excel_round(exchange). Since Excel always rounds halves up, this
        # means that _excel_round(exchange) does not, in general, equal -_excel_round(-exchange) as
        # you might expect. Caveat programmer!

        return OnCost(
            salary=_excel_round(gross_salary),
            exchange=-_excel_round(-exchange),
            employer_pension=_excel_round(employer_pension),
            employer_nic=_excel_round(employer_nic),
            apprenticeship_levy=_excel_round(apprenticeship_levy),
            total=_excel_round(total),
        )

    return on_cost


def _excel_round(n):
    """
    A version of round() which applies the Excel rule that halves rounds *up* rather than the
    conventional wisdom that they round to the nearest even.

    """
    # Ensure input is a rational
    n = fractions.Fraction(n)
    if n.denominator == 2:
        # always round up halves
        return math.ceil(n)
    return round(n)


#: On cost calculators keyed initially by year and then by scheme identifier.
_ON_COST_CALCULATORS = {
    2018: {
        # An employee with no scheme in tax year 2018/19
        Scheme.NONE: _on_cost_calculator(
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with USS in tax year 2018/19
        Scheme.USS: _on_cost_calculator(
            employer_pension_cb=pension.uss_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with USS and salary exchange in tax year 2018/19
        Scheme.USS_EXCHANGE: _on_cost_calculator(
            employer_pension_cb=pension.uss_employer_contribution,
            exchange_cb=pension.uss_employee_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with CPS in tax year 2018/19
        Scheme.CPS_HYBRID: _on_cost_calculator(
            employer_pension_cb=pension.cps_hybrid_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with CPS and salary exchange in tax year 2018/19
        Scheme.CPS_HYBRID_EXCHANGE: _on_cost_calculator(
            employer_pension_cb=pension.cps_hybrid_employer_contribution,
            exchange_cb=pension.cps_hybrid_employee_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee on the NHS scheme in tax year 2018/19
        Scheme.NHS: _on_cost_calculator(
            employer_pension_cb=pension.nhs_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),
    },
}

_LATEST_TAX_YEAR = max(_ON_COST_CALCULATORS.keys())

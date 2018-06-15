"""
Costs calculation
=================

The :py:mod:`~ucamstaffoncosts.costs` module provides support for calculating the total cost to
employ a staff member. The functionality of the module is exposed through a single function,
:py:func:`~ucamstaffoncosts.costs.cost`, which takes a tax year, pension scheme and base salary and
returns an :py:class:`~ucamstaffoncosts.Cost` object representing the on-costs for that employee:

.. testsetup::

    from ucamstaffoncosts.costs import *
    import datetime

>>> calculate_cost(
...     base_salary=25000, scheme=Scheme.USS, year=2018
... ) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
Cost(salary=25000, exchange=0, employer_pension=4500,
     employer_nic=2287, apprenticeship_levy=125, total=31912, tax_year=...)

The :py:attr:`~ucamstaffoncosts.Cost.total` attribute from the return value
can be used to forecast total expenditure for an employee in a given tax year.

If *year* is omitted, then the latest tax year which has any calculators
implemented is used. This behaviour can also be signalled by using the special
value :py:const:`~ucamstaffoncosts.LATEST`:

>>> latest_cost = calculate_cost(base_salary=25000, scheme=Scheme.USS, year=LATEST)
>>> latest_cost == calculate_cost(base_salary=25000, scheme=Scheme.USS)
True

We can get a detailed breakdown of costs for each tax year using the :py:func:`.costs_by_tax_year`
function. Our example employee will be a grade 2 whose next employment anniversary is on the 1st
June 2016. The employee on on the USS salary exchange pension scheme and has a first date of
non-employment of 1st October 2020:

>>> from ucamstaffoncosts import Grade
>>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
>>> initial_grade = Grade.GRADE_2
>>> initial_point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(initial_grade)
>>> next_anniversary_date = datetime.date(2016, 6, 1)
>>> scheme = Scheme.USS_EXCHANGE
>>> until_date = datetime.date(2020, 10, 1)

We can calculate the total cost of employment by passing these values to :

>>> costs = list(costs_by_tax_year(
...     2016, initial_grade, initial_point, scheme,
...     next_anniversary_date=next_anniversary_date,
...     until_date=until_date, scale_table=EXAMPLE_SALARY_SCALES))

We can print out details of these costs to fully explain the cost calculation:

>>> from ucamstaffoncosts.util import pprinttable
>>> for year, cost, salaries in costs:
...     print('=' * 60)
...     print('TAX YEAR: {}/{}'.format(year, year+1))
...     print('\\nSalaries\\n--------\\n')
...     pprinttable(salaries)
...     print('\\nCosts\\n-----')
...     if cost.tax_year != year:
...         print('(approximated using tax tables for {})'.format(cost.tax_year))
...     print('\\n')
...     pprinttable([cost])
...     print('\\n') # doctest: +NORMALIZE_WHITESPACE
============================================================
TAX YEAR: 2016/2017
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                      | grade         | point | base_salary | mapping_table_date
-----------+-----------------------------+---------------+-------+-------------+-------------------
2016-04-06 | start of tax year           | Grade.GRADE_2 | P3    | 14539       | 2015-08-01
2016-06-01 | anniversary: point P3 to P4 | Grade.GRADE_2 | P4    | 14818       | 2015-08-01
2016-08-01 | new salary table            | Grade.GRADE_2 | P4    | 15052       | 2016-08-01
2017-04-06 | end of tax year             | Grade.GRADE_2 | P4    | 15052       | 2016-08-01
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2018)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
14934  | -1195    | 3883             | 733          | 68                  | 18423 | 2018
<BLANKLINE>
<BLANKLINE>
============================================================
TAX YEAR: 2017/2018
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                      | grade         | point | base_salary | mapping_table_date
-----------+-----------------------------+---------------+-------+-------------+-------------------
2017-04-06 | start of tax year           | Grade.GRADE_2 | P4    | 15052       | 2016-08-01
2017-06-01 | anniversary: point P4 to P5 | Grade.GRADE_2 | P5    | 15356       | 2016-08-01
2017-08-01 | new salary table            | Grade.GRADE_2 | P5    | 15721       | 2017-08-01
2018-04-06 | end of tax year             | Grade.GRADE_2 | P5    | 15721       | 2017-08-01
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2018)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
15557  | -1245    | 4045             | 813          | 71                  | 19241 | 2018
<BLANKLINE>
<BLANKLINE>
============================================================
TAX YEAR: 2018/2019
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                         | grade         | point | base_salary | mapping_table_date
-----------+--------------------------------+---------------+-------+-------------+-------------------
2018-04-06 | start of tax year              | Grade.GRADE_2 | P5    | 15721       | 2017-08-01
2018-08-01 | new salary table (approximate) | Grade.GRADE_2 | P5    | 16035       | 2018-08-01
2019-04-06 | end of tax year                | Grade.GRADE_2 | P5    | 16035       | 2018-08-01
<BLANKLINE>
Costs
-----
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
15934  | -1275    | 4143             | 860          | 73                  | 19735 | 2018
<BLANKLINE>
<BLANKLINE>
============================================================
TAX YEAR: 2019/2020
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                         | grade         | point | base_salary | mapping_table_date
-----------+--------------------------------+---------------+-------+-------------+-------------------
2019-04-06 | start of tax year              | Grade.GRADE_2 | P5    | 16035       | 2018-08-01
2019-08-01 | new salary table (approximate) | Grade.GRADE_2 | P5    | 16356       | 2019-08-01
2020-04-06 | end of tax year                | Grade.GRADE_2 | P5    | 16356       | 2019-08-01
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2018)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
16253  | -1300    | 4226             | 901          | 74                  | 20154 | 2018
<BLANKLINE>
<BLANKLINE>
============================================================
TAX YEAR: 2020/2021
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                         | grade         | point | base_salary | mapping_table_date
-----------+--------------------------------+---------------+-------+-------------+-------------------
2020-04-06 | start of tax year              | Grade.GRADE_2 | P5    | 16356       | 2019-08-01
2020-08-01 | new salary table (approximate) | Grade.GRADE_2 | P5    | 16683       | 2020-08-01
2020-10-01 | end of employment              | Grade.GRADE_2 | P5    | 16683       | 2020-08-01
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2018)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
8031   | -642     | 2088             | 0            | 36                  | 9513  | 2018
<BLANKLINE>
<BLANKLINE>


"""  # noqa: E501
import collections
import datetime
import enum
import fractions
import itertools
import math

from . import tax
from . import pension
from .salary import progression


@enum.unique
class Scheme(enum.Enum):
    """
    Possible pension schemes an employee can be a member of.

    """

    #: No pension scheme.
    NONE = enum.auto()

    #: CPS hybrid
    CPS_HYBRID = enum.auto()

    #: CPS hybrid with salary exchange
    CPS_HYBRID_EXCHANGE = enum.auto()

    #: USS
    USS = enum.auto()

    #: USS with salary exchange
    USS_EXCHANGE = enum.auto()

    #: NHS
    NHS = enum.auto()


_Cost = collections.namedtuple(
    'Cost',
    'salary exchange employer_pension employer_nic apprenticeship_levy total tax_year'
)


class Cost(_Cost):
    """An individual on-costs calculation for a base salary.

    .. note::

        These values are all rounded to the nearest pound and so total may not be the sum of all
        the other fields.

    .. py:attribute:: salary

        Base salary for the employee.

    .. py:attribute:: exchange

        Amount of base salary exchanged as part of a salary exchange pension. By convention, this
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

    .. py:attribute:: tax_year

        Which year's table was used to calculate these costs.

    """


#: Special value to pass to :py:func:`~.cost` to represent the latest tax year which has an
#: implementation.
LATEST = 'LATEST'


def calculate_cost(base_salary, scheme, year=LATEST):
    """
    Return a :py:class:`Cost` instance given a tax year, pension scheme and base salary.

    :param int year: tax year
    :param Scheme scheme: pension scheme
    :param int base_salary: base salary of employee

    :raises NotImplementedError: if there is not an implementation for the specified tax year and
        pension scheme.

    """
    year = _LATEST_TAX_YEAR if year is LATEST else year

    try:
        calculator = _ON_COST_CALCULATORS[year][scheme]
    except KeyError:
        raise NotImplementedError()

    return calculator(base_salary)


def costs_by_tax_year(from_year, initial_grade, initial_point, scheme,
                      occupancy=1, start_date=None, next_anniversary_date=None,
                      tax_year_start_month=4, tax_year_start_day=6,
                      until_date=None, **kwargs):
    """
    Calculate total employment costs for each tax year for an employee who initially is at a
    particular grade and point. Keyword parameters are passed to
    :py:func:`ucamstaffoncosts.salary.progression.salary_progression`.

    :param from_year: tax year to start from
    :param initial_grade: grade of employee at start of tax year
    :param initial_point: salary spine point of employee at start of tax year
    :param scheme: pension scheme of employee
    :param start_date: date of employment start. If None, it is assumed the employee has been
        employed since before the start of the tax year
    :param until_date: if None, employee is no longer employed on and after this date

    >>> from ucamstaffoncosts import Grade
    >>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
    >>> initial_grade = Grade.GRADE_2
    >>> initial_point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(initial_grade)
    >>> next_anniversary_date = datetime.date(2016, 6, 1)
    >>> until_date = datetime.date(2018, 5, 1)
    >>> costs = list(costs_by_tax_year(
    ...     2016, initial_grade, initial_point, Scheme.USS_EXCHANGE,
    ...     next_anniversary_date=next_anniversary_date,
    ...     until_date=until_date, scale_table=EXAMPLE_SALARY_SCALES))

    Each row returns the tax year, cost and salary record:

    >>> costs[0][0]
    2016
    >>> costs[0][1] # doctest: +NORMALIZE_WHITESPACE
    Cost(salary=14934, exchange=-1195, employer_pension=3883, employer_nic=733,
         apprenticeship_levy=68, total=18423, tax_year=2018)
    >>> len(costs[0][2])
    4
    >>> costs[0][2][0] # doctest: +NORMALIZE_WHITESPACE
    SalaryRecord(date=datetime.date(2016, 4, 6), reason='start of tax year',
                 grade=<Grade.GRADE_2: 3>, point='P3', base_salary=14539,
                 mapping_table_date=datetime.date(2015, 8, 1))

    If *until_date* is before the start of *from_year* tax year, no results are returned
    >>> list(costs_by_tax_year(
    ...     2016, initial_grade, initial_point, Scheme.USS_EXCHANGE,
    ...     next_anniversary_date=next_anniversary_date,
    ...     until_date=datetime.date(2016, 3, 1), scale_table=EXAMPLE_SALARY_SCALES))
    []

    """
    occupancy_fraction = fractions.Fraction(occupancy)

    for year in itertools.count(from_year):
        from_date = datetime.date(year, tax_year_start_month, tax_year_start_day)
        to_date = datetime.date(year+1, tax_year_start_month, tax_year_start_day)

        if start_date is not None and start_date >= from_date and start_date < to_date:
            # Employee start date is within this tax year
            initial_date = start_date
            initial_reason = 'employee start'
        else:
            initial_date = from_date
            initial_reason = 'start of tax year'

        if until_date is not None and initial_date >= until_date:
            # we're done
            return

        # Total number of days in year
        tax_year_days = (to_date - from_date).days

        if until_date is not None and until_date <= to_date:
            to_date = until_date
            ends_on_tax_year = False
        else:
            ends_on_tax_year = True

        # If we have an anniversary date which precedes this tax year, advance it by years until it
        # is within this tax year
        anniversary_date = next_anniversary_date
        if anniversary_date is not None:
            while anniversary_date < from_date:
                anniversary_date = datetime.date(
                    anniversary_date.year+1, anniversary_date.month, anniversary_date.day)

        salaries = list(progression.salary_progression(
            initial_date, initial_grade, initial_point, initial_reason=initial_reason,
            until_date=to_date, next_anniversary_date=anniversary_date, **kwargs
        ))

        # Update initial grade and point for start of next year
        end_salary = salaries[-1]
        initial_grade, initial_point = end_salary.grade, end_salary.point

        # Add an "end of tax year" salary record which is a copy of the last salary change record
        salaries.append(progression.SalaryRecord(
            date=to_date,
            reason='end of tax year' if ends_on_tax_year else 'end of employment',
            grade=end_salary.grade, point=end_salary.point,
            base_salary=end_salary.base_salary,
            mapping_table_date=end_salary.mapping_table_date
        ))

        # Sum up per-day salaries
        total_salary = fractions.Fraction(0, 1)
        for start, end in zip(salaries, salaries[1:]):
            # how many days in this range?
            days = (end.date - start.date).days
            total_salary += fractions.Fraction(days * start.base_salary, tax_year_days)

        # Compute total salary earned this year taking into account occupancy
        total_salary = round(total_salary * occupancy_fraction)

        # Attempt to use this tax year for on-cost calculation, falling back to LATEST
        try:
            calculated_cost = calculate_cost(total_salary, scheme, year)
        except NotImplementedError:
            calculated_cost = calculate_cost(total_salary, scheme, LATEST)

        yield year, calculated_cost, salaries


def _cost_calculator(tax_year, employer_nic_cb,
                     employer_pension_cb=lambda _: 0,
                     exchange_cb=lambda _: 0,
                     apprenticeship_levy_cb=tax.standard_apprenticeship_levy):
    """
    Return a callable which will calculate an Cost entry from a base salary. Arguments which are
    callables each take a single argument which is a :py:class:`fractions.Fraction` instance
    representing the base salary of the employee. They should return a
    :py:class:`fractions.Fraction` instance.

    :param employer_pension_cb: callable which gives employer pension contribution from base
        salary.
    :param employer_nic_cb: callable which gives employer National Insurance contribution from
        base salary.
    :param exchange_cb: callable which gives amount of salary sacrificed in a salary exchange
        scheme from base salary.
    :param apprenticeship_levy_cb: callable which calculates the Apprenticeship Levy from base
        salary.

    """
    def _calculate(base_salary):
        # Ensure base salary is a rational
        base_salary = fractions.Fraction(base_salary)

        # We use the convention that the salary exchange value is negative to match the exchange
        # column in HR tables.
        exchange = -exchange_cb(base_salary)

        # The employer pension contribution is the contribution based on base salary along with
        # the employee contribution sacrificed from their salary.
        employer_pension = employer_pension_cb(base_salary) - exchange

        # the taxable salary is the base less the amount sacrificed. HR would appear to round the
        # sacrifice first
        taxable_salary = base_salary + _excel_round(exchange)

        # The employer's NIC is calculated on the taxable salary.
        employer_nic = employer_nic_cb(taxable_salary)

        # The Apprenticeship Levy is calculated on the taxable salary.
        apprenticeship_levy = apprenticeship_levy_cb(taxable_salary)

        # The total is calculated using the rounded values.
        total = (
            _excel_round(base_salary)
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

        return Cost(
            salary=_excel_round(base_salary),
            exchange=-_excel_round(-exchange),
            employer_pension=_excel_round(employer_pension),
            employer_nic=_excel_round(employer_nic),
            apprenticeship_levy=_excel_round(apprenticeship_levy),
            total=_excel_round(total),
            tax_year=tax_year,
        )

    return _calculate


def _excel_round(n):
    """
    A version of round() which applies the Excel rule that halves rounds *up* rather than the
    conventional wisdom that they round to the nearest even.

    (The jury is out about whether Excel really rounds away from zero or up but rounding up matches
    the tables produced by HR.)

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
        Scheme.NONE: _cost_calculator(
            tax_year=2018,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with USS in tax year 2018/19
        Scheme.USS: _cost_calculator(
            tax_year=2018,
            employer_pension_cb=pension.uss_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with USS and salary exchange in tax year 2018/19
        Scheme.USS_EXCHANGE: _cost_calculator(
            tax_year=2018,
            employer_pension_cb=pension.uss_employer_contribution,
            exchange_cb=pension.uss_employee_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with CPS in tax year 2018/19
        Scheme.CPS_HYBRID: _cost_calculator(
            tax_year=2018,
            employer_pension_cb=pension.cps_hybrid_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee with CPS and salary exchange in tax year 2018/19
        Scheme.CPS_HYBRID_EXCHANGE: _cost_calculator(
            tax_year=2018,
            employer_pension_cb=pension.cps_hybrid_employer_contribution,
            exchange_cb=pension.cps_hybrid_employee_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),

        # An employee on the NHS scheme in tax year 2018/19
        Scheme.NHS: _cost_calculator(
            tax_year=2018,
            employer_pension_cb=pension.nhs_employer_contribution,
            employer_nic_cb=tax.TABLE_A_EMPLOYER_NIC[2018],
        ),
    },
}

_LATEST_TAX_YEAR = max(_ON_COST_CALCULATORS.keys())

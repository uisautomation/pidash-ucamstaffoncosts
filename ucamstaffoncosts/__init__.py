"""
.. testsetup::

    from ucamstaffoncosts import *
    import datetime

"""
import collections
import datetime
import fractions

from . import costs

from .costs import Scheme, Cost
from .salary.progression import SalaryRecord
from .salary.scales import Grade


__all__ = [
    'employment_expenditure_and_commitments', 'CommitmentExplanation', 'Scheme', 'Grade', 'Cost',
    'SalaryRecord'
]


def employment_expenditure_and_commitments(until_date, initial_grade, initial_point, scheme,
                                           start_date=None, from_date=None, occupancy=1,
                                           tax_year_start_month=4, tax_year_start_day=6, **kwargs):
    """
    Calculate the existing expenditure and remaining commitments for an employee's contract.
    Returns a pair giving the total commitment and a list of :py:class:`CommitmentExplanation`
    tuples explaining the calculation.

    :param from_date: date at which to differentiate between expenditure and commitments. If
        ``None``, today's date is used.
    :param start_date: date at which employee started. Results will be returned from this date. If
        ``None``, the "from date" is used.
    :param occupancy: proportion of full-time this employee works
    :type occupancy: :py:class:`numbers.Rational`

    Remaining keyword arguments are passed to :py:func:`costs_by_tax_year`.

    >>> from ucamstaffoncosts import Grade, Scheme
    >>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
    >>> initial_grade = Grade.GRADE_2
    >>> initial_point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(initial_grade)
    >>> scheme = Scheme.USS_EXCHANGE
    >>> next_anniversary_date = datetime.date(2016, 6, 1)
    >>> from_date = next_anniversary_date - datetime.timedelta(days=400)
    >>> until_date = from_date + datetime.timedelta(days=1000)

    >>> expenditure, commitments, _ = employment_expenditure_and_commitments(
    ...     until_date, initial_grade, initial_point, scheme,
    ...     from_date=from_date, next_anniversary_date=next_anniversary_date,
    ...     scale_table=EXAMPLE_SALARY_SCALES)
    >>> expenditure
    0
    >>> commitments
    50146

    The *occupancy* parameter allows one to specify what proportion of full time this person works:

    >>> import fractions
    >>> _, half_time_commitments, _ = employment_expenditure_and_commitments(
    ...     until_date, initial_grade, initial_point, scheme,
    ...     occupancy=fractions.Fraction(50, 100),
    ...     from_date=from_date, next_anniversary_date=next_anniversary_date,
    ...     scale_table=EXAMPLE_SALARY_SCALES)
    >>> half_time_commitments
    24221

    Notice that this value is not half of the full-time commitments since employer costs do not
    scale linearly!

    The first tax year returned will contain the *from_date*:

    >>> from_date = datetime.date(2016, 1, 1)
    >>> _, _, explanations = employment_expenditure_and_commitments(
    ...     until_date, initial_grade, initial_point, scheme,
    ...     from_date=from_date, next_anniversary_date=next_anniversary_date,
    ...     scale_table=EXAMPLE_SALARY_SCALES)
    >>> explanations[0].tax_year
    2016

    """
    occupancy_fraction = fractions.Fraction(occupancy)

    from_date = from_date if from_date is not None else datetime.datetime.now().date()
    start_date = start_date if start_date is not None else from_date

    start_year = start_date.year
    if datetime.date(start_year, tax_year_start_month, tax_year_start_day) > start_date:
        start_year -= 1

    # Calculate costs
    all_costs = costs.costs_by_tax_year(
        start_year, initial_grade, initial_point, scheme,
        occupancy=occupancy_fraction,
        start_date=start_date, tax_year_start_month=tax_year_start_month,
        tax_year_start_day=tax_year_start_day,
        until_date=until_date, **kwargs)

    explanations = []

    total_expenditure, total_commitment = 0, 0
    for year, cost, salaries in all_costs:
        # What range of dates does this cover?
        start_date = salaries[0].date
        end_date = salaries[-1].date

        tax_year_start_date = datetime.date(
            year, tax_year_start_month, tax_year_start_day)
        tax_year_end_date = datetime.date(
            year+1, tax_year_start_month, tax_year_start_day)
        tax_year_days = (tax_year_end_date - tax_year_start_date).days

        # Should never get salary records after until_date
        assert end_date <= until_date

        # Compute total earnings earned *after or on* the from_date.
        earnings_after_from_date = fractions.Fraction(0, 1)
        for salary_start, salary_end in zip(salaries, salaries[1:]):
            salary_start_date = max(salary_start.date, from_date)
            salary_end_date = max(salary_start_date, salary_end.date)

            # how many days in this range?
            days = (salary_end_date - salary_start_date).days
            earnings_after_from_date += fractions.Fraction(
                days * salary_start.base_salary, tax_year_days) * occupancy_fraction
        earnings_after_from_date = round(earnings_after_from_date)
        assert earnings_after_from_date >= 0
        assert earnings_after_from_date <= cost.salary

        # commitment is share of total cost weighted by the ratio of earnings after from date to
        # total earnings for that year
        commitment = round(fractions.Fraction(earnings_after_from_date, cost.salary) * cost.total)
        expenditure = cost.total - commitment

        explanations.append(CommitmentExplanation(
            tax_year=start_date.year, salary=cost.salary,
            salary_to_come=earnings_after_from_date,
            expenditure=expenditure, commitment=commitment,
            salaries=salaries, cost=cost
        ))

        total_expenditure += expenditure
        total_commitment += commitment

    return total_expenditure, total_commitment, explanations


_CommitmentExplanation = collections.namedtuple(
    'CommitmentExplanation',
    'tax_year salary salary_to_come expenditure commitment salaries cost')


class CommitmentExplanation(_CommitmentExplanation):
    """
    An explanation of the commitment calculation for a given tax year.

    .. py:attribute:: tax_year

        Integer giving the calendar year when the tax year started

    .. py:attribute:: salary

        Total base salary for the tax year

    .. py:attribute:: salary_to_come

        Salary which is yet to come. I.e. the salary which has not yet been earned as of the "from"
        date.

    .. py:attribute:: expenditure

        The expenditure for this tax year. I.e. the amount of total cost of employment which has
        already been spent.

    .. py:attribute:: commitment

        The commitment for this tax year. This is the total cost of employment minus the
        expenditure.

    .. py:attribute:: salaries

        A list of :py:class:`~.SalaryRecord` tuples which
        explain why the employee's salary is what it is during the tax year.

    .. py:attribute:: cost

        A :py:class:`~.Cost` tuple explaining the total cost of employment for the tax year.
    """

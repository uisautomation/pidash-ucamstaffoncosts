"""
Modelling salary progression
============================

The :py:mod:`.progression` module provides tool to model an employee's salary change over time
given a grade, point and date to start modelling from. (We call this the "from date" in this
documentation.)

.. testsetup::

    from ucamstaffoncosts.salary.progression import *
    import datetime

In our example, we'll start modelling an employee's salary from the 1st January 2016.

>>> from_date = datetime.date(2016, 1, 1)

To illustrate the use of the module, we'll make use of the example salary scale table from the
:py:mod:`~ucamstaffoncosts.salary.scales` module documentation. When we start modelling, the
employee is on the lowest point of grade 2:

>>> from ucamstaffoncosts import Grade
>>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
>>> initial_grade = Grade.GRADE_2
>>> initial_point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(initial_grade)

Their next employment anniversary is the 1st June 2016:

>>> next_anniversary_date = datetime.date(2016, 6, 1)

We want to show their salary progression up until the 1st January 2023:

>>> until_date = datetime.date(2023, 1, 1)

The :py:func:`salary_progression` function will return an iterable given these parameters which
will represent the expected salary progression:

>>> progression = salary_progression(
...     from_date, initial_grade, initial_point, next_anniversary_date=next_anniversary_date,
...     until_date=until_date, scale_table=EXAMPLE_SALARY_SCALES)

The iterable returned from :py:func:`salary_progression` yields :py:class:`~SalaryRecord` tuples.
We'll use a format string to nicely present the progression in a table:

>>> fmt_str = ('{date!s: <12} | {reason: <35} | {grade!s: <16} | {point!s: <5} | '
...            '{base_salary: >8,d}')
>>> for row in progression:
...     print(fmt_str.format(**row._asdict()))
2016-01-01   | set salary                          | Grade.GRADE_2    | P3    |   14,539
2016-06-01   | anniversary: point P3 to P4         | Grade.GRADE_2    | P4    |   14,818
2016-08-01   | new salary table                    | Grade.GRADE_2    | P4    |   15,052
2017-06-01   | anniversary: point P4 to P5         | Grade.GRADE_2    | P5    |   15,356
2017-08-01   | new salary table                    | Grade.GRADE_2    | P5    |   15,721
2018-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,035
2019-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,356
2020-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,683
2021-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   17,017
2022-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   17,357

The 1st August salary changes are approximated if the mapping table is not known. In this example,
the actual tables for 2016 and 2017 were used but approximations were used for the remaining
tables. Note that once the maximum anniversary increment point has been reached, no new increments
are made on the employment anniversary.

"""
import collections
import datetime
import fractions
import heapq
import itertools

from . import scales


_SalaryRecord = collections.namedtuple(
    'SalaryRecord', 'date reason grade point base_salary mapping_table_date')


class SalaryRecord(_SalaryRecord):
    """
    A :py:class:`collections.namedtuple` subclass which represents a salary history record.

    .. py:attribute:: date

        :py:class:`datetime.date` at which this new salary takes effect.

    .. py:attribute:: reason

        Human-readable string describing the reason for this change

    .. py:attribute:: grade

        :py:class:`~ucamstaffoncosts.Grade` representing the initial grade of the employee

    .. py:attribute:: point

        string giving the name of this employee's spine point

    .. py:attribute:: base_salary

        base salary of the employee in pounds sterling

    .. py:attribute:: mapping_table_date

        :py:class:`datetime.date` giving the "effective from" date for the grade and point to base
        salary mapping table used

    """


def salary_progression(from_date, initial_grade, initial_point, initial_reason=None,
                       next_anniversary_date=None, until_date=None,
                       scale_table=scales.SALARY_SCALES,
                       approximate_negotiated_annual_change=None,
                       negotiated_annual_change_month=None, negotiated_annual_change_day=None,
                       elide_null_changes=True):
    """
    Return an iterable of :py:class:`~SalaryRecord` tuples describing the salary
    progression of an employee.

    :param from_date: start returning results from this date
    :type from_date: :py:class:`datetime.date`
    :param initial_grade: initial grade for employee
    :type initial_grade: :py:class:`~ucamstaffoncosts.Grade`
    :param initial_point: initial spine point for employee
    :type initial_point: str
    :param initial_reason: reason passed to :py:func:`set_salary`
    :param next_anniversary_date: next anniversary increment date or ``None`` if there is none
    :type next_anniversary_date: :py:class:`datetime.date`
    :param until_date: it not ``None``, stop returning results on or after this date
    :type until_date: :py:class:`datetime.date`
    :param scale_table: salary scale table to use
    :type scale_table: :py:class:`~ucamstaffoncosts.scales.SalaryScaleTable`
    :param approximate_negotiated_annual_change: passed to :py:func:`salary_mapping_tables`
    :param negotiated_annual_change_month: passed to :py:func:`salary_mapping_tables`
    :param negotiated_annual_change_day: passed to :py:func:`salary_mapping_tables`
    :param elide_null_changes: passed to :py:func:`fold`

    """
    changes = [set_salary(
        from_date, grade=initial_grade, point=initial_point, reason=initial_reason
    )]

    if next_anniversary_date is not None:
        changes.append(anniversary_increments(next_anniversary_date, table=scale_table))

    progression_iterable = map_grade_and_points(
        compose_changes(*changes),
        salary_mapping_tables_kwargs={'table': scale_table})

    if until_date is not None:
        progression_iterable = until(until_date, progression_iterable)

    return fold(progression_iterable, elide_null_changes=elide_null_changes)


_Salary = collections.namedtuple('Salary', 'grade point base_per_annum as_of_date')


class Salary(_Salary):
    """
    A :py:class:`collections.namedtuple` subclass which represents a salary for an employee. The
    :py:attr:`.grade` and :py:attr:`.point` attributes must be set to represent a salary whereas
    the :py:attr:`base_per_annum` may be `None` if this object does not represent a particular
    per-annum base salary for that grade and point.

    The :py:attr:`base_per_annum` and :py:attr:`as_of_date` attributes are optional and will
    default to `None`:

    >>> from ucamstaffoncosts.salary.scales import Grade
    >>> import datetime
    >>> Salary(Grade.GRADE_2, 'POINT_X')
    Salary(grade=<Grade.GRADE_2: 3>, point='POINT_X', base_per_annum=None, as_of_date=None)
    >>> Salary(Grade.GRADE_2, 'POINT_X', 10000,
    ...        datetime.date(2017, 8, 1)) # doctest: +NORMALIZE_WHITESPACE
    Salary(grade=<Grade.GRADE_2: 3>, point='POINT_X', base_per_annum=10000,
           as_of_date=datetime.date(2017, 8, 1))

    .. py:attribute:: grade

        A :py:class:`~ucamstaffoncosts.Grade` representing the grade of the employee.

    .. py:attribute:: point

        A string giving the name of the salary spine point within the grade of the employee.

    .. py:attribute:: base_per_annum

        If this salary has been converted to a per annum base salary, this is the per annum salary
        in pounds sterling. Otherwise, it is `None`.

    .. py:attribute:: as_of_date

        If this salary has been converted to a per annum base salary, this is the effective date of
        the mapping table used.

    """
    def __new__(cls, grade, point, base_per_annum=None, as_of_date=None):
        return super().__new__(cls, grade, point, base_per_annum, as_of_date)

    def with_base(self, base_per_annum, as_of_date):
        """
        Return a copy of this salary with the :py:attr:`base_per_annum` and :py:attr:`as_of_date`
        modified.

        >>> from ucamstaffoncosts.salary.scales import Grade
        >>> import datetime
        >>> s1 = Salary(Grade.GRADE_2, 'POINT_X')
        >>> s1
        Salary(grade=<Grade.GRADE_2: 3>, point='POINT_X', base_per_annum=None, as_of_date=None)
        >>> s2 = s1.with_base(10000, datetime.date(2017, 8, 1))
        >>> s2 # doctest: +NORMALIZE_WHITESPACE
        Salary(grade=<Grade.GRADE_2: 3>, point='POINT_X', base_per_annum=10000,
               as_of_date=datetime.date(2017, 8, 1))


        """
        return Salary(grade=self.grade, point=self.point, base_per_annum=base_per_annum,
                      as_of_date=as_of_date)


_SalaryChange = collections.namedtuple('SalaryChange', 'date update_salary')


class SalaryChange(_SalaryChange):
    """
    A :py:class:`collections.namedtuple` subclass which represents a change of salary for an
    employee on a particular date.

    .. py:attribute:: date

        A :py:class:`datetime.date` on which the salary change happened.

    .. py:attribute:: update_salary

        A callable which takes a :py:class:`Salary` object and returns a (new :py:class:`Salary`,
        reason) pair with the updated salary. The reason is a human-readable string describing the
        reason for the change.

    """


def fold(changes, initial_salary=None, elide_null_changes=True):
    """
    We will use the following list of :py:class:`SalaryChange` tuples as examples:

    >>> from ucamstaffoncosts.salary.scales import Grade
    >>> changes = [
    ...     SalaryChange(date=datetime.date(2017, 1, 1),
    ...                  update_salary=lambda s: (s, 'pass through salary')),
    ...     SalaryChange(date=datetime.date(2017, 1, 1),
    ...                  update_salary=lambda _: (Salary(grade=Grade.GRADE_1, point='P1'),
    ...                                           'set grade and point')),
    ...     SalaryChange(date=datetime.date(2017, 2, 1),
    ...                  update_salary=lambda _: (Salary(grade=Grade.GRADE_1, point='P1'),
    ...                                           'null change')),
    ...     SalaryChange(date=datetime.date(2017, 3, 1),
    ...                  update_salary=lambda _: (Salary(grade=Grade.GRADE_1, point='P2'),
    ...                                           'point -> P2')),
    ...     SalaryChange(date=datetime.date(2017, 4, 1),
    ...                  update_salary=lambda _: (Salary(grade=Grade.GRADE_2, point='P2'),
    ...                                           'grade -> G2')),
    ... ]

    If *elide_null_changes* is False, changes which do not change the salary are still reported:

    >>> fmt_str = '{date!s: <12} | {reason: <20} | {grade!s: <16} | {point!s: <5}'
    >>> for row in fold(changes, elide_null_changes=False):
    ...     print(fmt_str.format(**row._asdict())) # doctest: +NORMALIZE_WHITESPACE
    2017-01-01   | pass through salary  | None             | None
    2017-01-01   | set grade and point  | Grade.GRADE_1    | P1
    2017-02-01   | null change          | Grade.GRADE_1    | P1
    2017-03-01   | point -> P2          | Grade.GRADE_1    | P2
    2017-04-01   | grade -> G2          | Grade.GRADE_2    | P2

    The default is for *elide_null_changes* to be ``True`` which means that changes which do not
    change the salary are swallowed:

    >>> for row in fold(changes):
    ...     print(fmt_str.format(**row._asdict())) # doctest: +NORMALIZE_WHITESPACE
    2017-01-01   | set grade and point  | Grade.GRADE_1    | P1
    2017-03-01   | point -> P2          | Grade.GRADE_1    | P2
    2017-04-01   | grade -> G2          | Grade.GRADE_2    | P2

    Note that the default grade and point are ``None``. An initial salary can be set via
    *initial_salary*:

    >>> initial_salary = Salary(grade=Grade.GRADE_2, point='P5')
    >>> for row in fold(changes, initial_salary=initial_salary, elide_null_changes=False):
    ...     print(fmt_str.format(**row._asdict())) # doctest: +NORMALIZE_WHITESPACE
    2017-01-01   | pass through salary  | Grade.GRADE_2    | P5
    2017-01-01   | set grade and point  | Grade.GRADE_1    | P1
    2017-02-01   | null change          | Grade.GRADE_1    | P1
    2017-03-01   | point -> P2          | Grade.GRADE_1    | P2
    2017-04-01   | grade -> G2          | Grade.GRADE_2    | P2

    """
    current_salary = initial_salary or Salary(grade=None, point=None)
    for change in iter(changes):
        previous_salary = current_salary
        current_salary, reason = change.update_salary(previous_salary)
        if elide_null_changes and (current_salary == previous_salary):
            continue
        yield SalaryRecord(
            change.date, reason, current_salary.grade, current_salary.point,
            current_salary.base_per_annum, current_salary.as_of_date
        )


def map_grade_and_points(changes, salary_mapping_tables_kwargs={}):
    """
    Take an iterable yielding :py:class:`~.SalaryChange` or callable objects and map the grade and
    point of each :py:class:`~.Salary` to the base per annum salary.

    :param changes: iterable yielding salary changes
    :param salary_mapping_tables_kwargs: additional kwargs to pass to
        :py:func:`salary_mapping_tables`.

    To illustrate functionality, we'll make use of the same example table as used in the
    :py:mod:`ucamstaffoncosts.salary.scales` documentation.  We can model a Grade 2 employee
    starting on the lowest point in the following way:

    >>> from ucamstaffoncosts import Grade
    >>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
    >>> grade = Grade.GRADE_2
    >>> point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(grade)
    >>> start_date = datetime.date(2017, 3, 5) # start date on contract
    >>> next_anniversary_date = datetime.date(2017, 6, 1)
    >>> increments = anniversary_increments(next_anniversary_date, table=EXAMPLE_SALARY_SCALES)
    >>> salaries = map_grade_and_points(compose_changes(
    ...     set_salary(start_date, grade, point),
    ...     increments
    ... ), salary_mapping_tables_kwargs={'table': EXAMPLE_SALARY_SCALES})
    >>> fmt_str = ('{date!s: <12} | {reason: <35} | {grade!s: <16} | {point!s: <5} | '
    ...            '{base_salary: >8,d}')
    >>> for row in fold(until(datetime.date(2023, 1, 1), salaries), elide_null_changes=False):
    ...     print(fmt_str.format(**row._asdict()))
    2017-03-05   | set salary                          | Grade.GRADE_2    | P3    |   14,767
    2017-06-01   | anniversary: point P3 to P4         | Grade.GRADE_2    | P4    |   15,052
    2017-08-01   | new salary table                    | Grade.GRADE_2    | P4    |   15,417
    2018-06-01   | anniversary: point P4 to P5         | Grade.GRADE_2    | P5    |   15,721
    2018-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,035
    2019-06-01   | anniversary: no increment           | Grade.GRADE_2    | P5    |   16,035
    2019-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,356
    2020-06-01   | anniversary: no increment           | Grade.GRADE_2    | P5    |   16,356
    2020-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   16,683
    2021-06-01   | anniversary: no increment           | Grade.GRADE_2    | P5    |   16,683
    2021-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   17,017
    2022-06-01   | anniversary: no increment           | Grade.GRADE_2    | P5    |   17,017
    2022-08-01   | new salary table (approximate)      | Grade.GRADE_2    | P5    |   17,357

    Passing an empty iterable works as you'd expect:

    >>> list(map_grade_and_points([]))
    []

    """
    changes = iter(changes)

    # Peek ahead at the first change. If StopIteration is raised, it is bubbled back up to the
    # caller.
    first_change = next(changes)

    # Use this value's from date to determine when we're interested in mapping tables
    from_date = first_change[0]
    mapping_tables = salary_mapping_tables(from_date, **salary_mapping_tables_kwargs)

    # Use the merge_priority_iterables() function to walk through, updating our mapping table as
    # we go. To do this we form a list of iterables as shown in that functions documentation. Each
    # iterable returns (date, value) pairs. Since merge_priority_iterables() passes us the index,
    # we can use it to differentiate between a new table and a new change.
    changes_iterable = (
        # Map changes into a (date, change) pair suitable for merge_priority_iterables. Note that
        # we chain() the first change we peeked at back on the iterable.
        (change.date, change) for change in itertools.chain([first_change], changes)
    )

    # Note: we have mapping_tables first here because we want to guarantee that we know about a
    # change of mapping before any change which may need it on the same day.
    events = merge_priority_iterables([mapping_tables, changes_iterable])

    current_mapping, current_mapping_date, current_salary = None, None, None
    for event in events:
        date, index = event[:2]
        if index == 0:
            # This was a new mapping table
            current_mapping, is_approximate = event[2:]
            current_mapping_date = date

            reason = 'new salary table'
            if is_approximate:
                reason += ' (approximate)'
        elif index == 1:
            salary_change = event[2]

            # Update the current salary
            current_salary, reason = salary_change.update_salary(current_salary)
        else:
            assert False, 'should not be reached'  # pragma: no cover

        if current_salary is not None:
            yield SalaryChange(date=date, update_salary=(
                lambda _: (
                    current_salary.with_base(
                        current_mapping[current_salary.point], current_mapping_date
                    ), reason
                )
            ))


def compose_changes(*change_iterables):
    """
    Compose a several iterables yielding :py:class:`SalaryChange` tuples into a single iterable
    which yields the changes in ascending date order.

    """
    mapped_change_iterables = [
        ((change.date, change) for change in iterable)
        for iterable in change_iterables
    ]
    for _, _, change in merge_priority_iterables(mapped_change_iterables):
        yield change


def until(end_date, changes):
    """
    Keep iterating over the salary changes in *changes* until the first date which is greater than
    *or equal* to *end_date*.

    >>> start_date = datetime.date(2018, 6, 1)
    >>> end_date = datetime.date(2022, 5, 1)
    >>> increments = anniversary_increments(start_date)
    >>> for change in until(end_date, increments):
    ...     print(change.date)
    2018-06-01
    2019-06-01
    2020-06-01
    2021-06-01

    If *end_date* is not a :py:class:`datetime.date`, a :py:exc:`TypeError` is raised:

    >>> list(until('2022-05-01', anniversary_increments(start_date)))
    Traceback (most recent call last):
        ...
    TypeError: until must be passed a date object

    """
    if not isinstance(end_date, datetime.date):
        raise TypeError('until must be passed a date object')

    return itertools.takewhile(lambda c: c.date < end_date, changes)


def anniversary_increments(next_anniversary_date, table=scales.SALARY_SCALES):
    """
    Return an iterable of :py:class:`SalaryChange` tuples representing the increments which happen
    on the anniversary of employment starting from *next_anniversary_date*.

    >>> increments = anniversary_increments(datetime.date(2017, 5, 1))
    >>> next(increments).date
    datetime.date(2017, 5, 1)
    >>> next(increments).date
    datetime.date(2018, 5, 1)
    >>> next(increments).date
    datetime.date(2019, 5, 1)

    If *next_anniversary_date* is not a :py:class:`datetime.date`, a :py:exc:`TypeError` is raised:

    >>> next(anniversary_increments('2017-05-01'))
    Traceback (most recent call last):
        ...
    TypeError: anniversary_increments must be passed a date object

    """
    if not isinstance(next_anniversary_date, datetime.date):
        raise TypeError('anniversary_increments must be passed a date object')

    month, day = next_anniversary_date.month, next_anniversary_date.day

    for year in itertools.count(next_anniversary_date.year):
        def update_salary(previous_salary):
            grade, point = previous_salary.grade, previous_salary.point
            new_point = table.increment(grade, point)
            if new_point == point:
                return (previous_salary, 'anniversary: no increment')
            return (Salary(grade, new_point),
                    'anniversary: point {} to {}'.format(
                        point, new_point))
        yield SalaryChange(date=datetime.date(year, month, day), update_salary=update_salary)


def set_salary(from_date, grade, point, reason=None):
    """
    Return an iterable which represents a change in grade and/or point.

    >>> from ucamstaffoncosts import Grade
    >>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
    >>> grade = Grade.GRADE_2
    >>> point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(grade)
    >>> next(set_salary(datetime.date(2017, 1, 1), grade, point)) # doctest: +ELLIPSIS
    SalaryChange(date=datetime.date(2017, 1, 1), update_salary=...)

    If *from_date* is not a :py:class:`datetime.date`, a :py:exc:`TypeError` is raised:

    >>> set_salary('2017-01-01', grade, point)
    Traceback (most recent call last):
        ...
    TypeError: set_salary must be passed a date object

    """
    if not isinstance(from_date, datetime.date):
        raise TypeError('set_salary must be passed a date object')
    salary_and_reason = (Salary(grade, point), reason if reason is not None else 'set salary')
    return iter([SalaryChange(date=from_date, update_salary=lambda _: salary_and_reason)])


def merge_priority_iterables(iterables):
    """
    Return a priority queue over *iterables* which is itself iterable. Each iterable which forms
    part of the queue must return objects of the form (deadline, ...). As the queue is iterated
    over, the item with the *smallest* deadline from all of the iterators is selected and
    (deadline, index, value) is yielded where "index" is the 0-based index of the iterable which
    yielded the value in *iterables*.

    If two iterables are yielding values with the same deadline at the same time, the one which was
    earlier in the *iterables* sequence is yielded first.

    It is envisaged that all iterables passed to the function will themselves yield values with
    monotonically increasing deadline. The implementation does not attempt to enforce this.

    As an example, use two lists as iterables which specify deadlines in terms of date objects:

    >>> it0 = [
    ...     (datetime.date(2018, 3, 31), 'it0_0'),
    ...     (datetime.date(2018, 4, 5), 'it0_1'),
    ...     (datetime.date(2018, 6, 1), 'it0_2'),
    ...     (datetime.date(2018, 6, 1), 'it0_3')
    ... ]
    >>> it1 = [
    ...     (datetime.date(2018, 1, 1), 'it1_0'),
    ...     (datetime.date(2018, 3, 31), 'it1_1'),
    ...     (datetime.date(2018, 4, 7), 'it1_2'),
    ...     (datetime.date(2018, 6, 2), 'it1_3')
    ... ]
    >>> q = merge_priority_iterables([it0, it1])
    >>> list(q)  # doctest: +NORMALIZE_WHITESPACE
    [(datetime.date(2018, 1, 1), 1, 'it1_0'), (datetime.date(2018, 3, 31), 0, 'it0_0'),
    (datetime.date(2018, 3, 31), 1, 'it1_1'), (datetime.date(2018, 4, 5), 0, 'it0_1'),
    (datetime.date(2018, 4, 7), 1, 'it1_2'), (datetime.date(2018, 6, 1), 0, 'it0_2'),
    (datetime.date(2018, 6, 1), 0, 'it0_3'), (datetime.date(2018, 6, 2), 1, 'it1_3')]

    Infinite iterables are also supported:

    >>> import itertools
    >>> it3 = map(
    ...     lambda o: (datetime.date(2018, 1, 1) + datetime.timedelta(days=30*o), f'it3_{o}'),
    ...     itertools.count()
    ... )
    >>> q = merge_priority_iterables([it0, it1, it3])
    >>> list(itertools.takewhile(
    ...     lambda v: v[0] < datetime.date(2018, 8, 1), q))  # doctest: +NORMALIZE_WHITESPACE
    [(datetime.date(2018, 1, 1), 1, 'it1_0'), (datetime.date(2018, 1, 1), 2, 'it3_0'),
    (datetime.date(2018, 1, 31), 2, 'it3_1'), (datetime.date(2018, 3, 2), 2, 'it3_2'),
    (datetime.date(2018, 3, 31), 0, 'it0_0'), (datetime.date(2018, 3, 31), 1, 'it1_1'),
    (datetime.date(2018, 4, 1), 2, 'it3_3'), (datetime.date(2018, 4, 5), 0, 'it0_1'),
    (datetime.date(2018, 4, 7), 1, 'it1_2'), (datetime.date(2018, 5, 1), 2, 'it3_4'),
    (datetime.date(2018, 5, 31), 2, 'it3_5'), (datetime.date(2018, 6, 1), 0, 'it0_2'),
    (datetime.date(2018, 6, 1), 0, 'it0_3'), (datetime.date(2018, 6, 2), 1, 'it1_3'),
    (datetime.date(2018, 6, 30), 2, 'it3_6'), (datetime.date(2018, 7, 30), 2, 'it3_7')]

    """
    # The implementation is a thin wrapper around heapq.merge() which nearly does everything we
    # need. We modify the iterables' values to be (deadline, iterable index, value) We insert
    # "iterable index" here as a tie-break value to ensure that the ordering of values with equal
    # deadline is deterministic and follows the documentation above. This also means that the
    # values need not be comparable since the tuple comparison will stop at the iterable index.
    return heapq.merge(*[
        # note: the idx=idx is necessary because lambdas capture by *reference*, not value
        map(lambda v, idx=idx: (v[0], idx) + v[1:], iter(it))
        for idx, it in enumerate(iterables)
    ])


def salary_mapping_tables(from_date, table=scales.SALARY_SCALES,
                          approximate_negotiated_annual_change=fractions.Fraction(102, 100),
                          negotiated_annual_change_month=None, negotiated_annual_change_day=None):
    """
    Return an iterable which yields (date, mapping, is_approximate) tuples. The date in each tuple
    refers to an effective-from date for a point to salary mapping and the mapping is a dict
    mapping point names to pounds sterling full-time equivalent salaries. The first date returned
    is guaranteed to be before or equal to *from_date*.

    :param from_date: date from which mappings are required
    :type from_date: :py:class:`date.datetime`
    :param table: salary scale table to use
    :type table: :py:class:`~ucamstaffoncosts.salary.scales.SalaryScaleTable`
    :param approximate_negotiated_annual_change: multiplier to use for annual negotiated salary
        change for years when a point table is unavailable

    Where present, actual mapping tables are used. For these tables, *is_approximate* will be
    ``False``. For annual negotiated changes where the table is not available, an approximation is
    used: the previous year's salaries are multiplied by *approximate_negotiated_annual_change*.
    These approximations are always made relative to the latest actual salaries available even if
    one is required to approximate into the past. For these tables, *is_approximate* will be
    ``True``.

    The date at which this change happens is taken from the *latest* actual change recorded in the
    salary table. It can be overridden via the *negotiated_annual_change_month* and
    *negotiated_annual_change_day* parameters. These parameters are 1-based day and month indices
    as accepted by :py:class:`datetime.date`.

    To illustrate, we will use the example table from the :py:mod:`~ucamstaffoncosts.salary.scales`
    module.

    >>> import pkg_resources
    >>> import yaml
    >>> from ucamstaffoncosts.salary.scales import SalaryScaleTable
    >>> table = SalaryScaleTable(yaml.load(pkg_resources.resource_string(
    ...    'ucamstaffoncosts', 'data/example_salary_scales.yaml')))
    >>> from_date = datetime.date(2017, 5, 1)
    >>> mappings = salary_mapping_tables(from_date, table=table)

    The first date returned will be before *from_date* since it is the effective-from date of the
    appropriate salary mapping table:

    >>> date, mapping1, is_approximate = next(mappings)
    >>> is_approximate
    False
    >>> date < from_date
    True
    >>> date
    datetime.date(2016, 8, 1)
    >>> _, expected_mapping = table.point_to_salary_map_for_date(date)
    >>> mapping1 == expected_mapping
    True

    The mapping returned for the next date will also match the one from the table as the table has
    an exact salary map:

    >>> date, mapping2, is_approximate = next(mappings)
    >>> is_approximate
    False
    >>> date
    datetime.date(2017, 8, 1)
    >>> mapping1 == mapping2
    False
    >>> _, expected_mapping = table.point_to_salary_map_for_date(date)
    >>> mapping2 == expected_mapping
    True

    However, the third date will be a new approximated mapping which is not present in the original
    table:

    >>> date, mapping3, is_approximate = next(mappings)
    >>> is_approximate
    True
    >>> date
    datetime.date(2018, 8, 1)
    >>> mapping2 == mapping3
    False
    >>> _, non_extrapolated_mapping = table.point_to_salary_map_for_date(date)
    >>> mapping3 == non_extrapolated_mapping
    False

    This approximation should be a 2% rise over the previous value (although it is rounded to the
    nearest integer):

    >>> mapping2 == {
    ...     'P1': 14304, 'P2': 14675, 'P3': 15126, 'P4': 15417, 'P5': 15721, 'P6': 16035,
    ...     'P7': 16341, 'P8': 16654}
    True
    >>> [abs((mapping3[k]/v) - 1.02) < 1e-4 for k, v in mapping2.items()]
    [True, True, True, True, True, True, True, True]

    Finally, the fourth date's mapping should be an approximation which is a further 2% rise:

    >>> date, mapping4, is_approximate = next(mappings)
    >>> is_approximate
    True
    >>> date
    datetime.date(2019, 8, 1)
    >>> mapping3 == mapping4
    False
    >>> [abs((mapping4[k]/v) - 1.02) < 1e-4 for k, v in mapping3.items()]
    [True, True, True, True, True, True, True, True]

    """
    # Find the dates for which we have an exact mapping from point to salary.
    exact_dates = set(table.point_to_salary_map_effective_dates())

    # And the latest date from those
    latest_exact_date = max(exact_dates)
    _, latest_exact_mapping = table.point_to_salary_map_for_date(latest_exact_date)

    # Determine the month and day of increments
    negotiated_annual_change_month = (
        negotiated_annual_change_month if negotiated_annual_change_month is not None
        else latest_exact_date.month
    )
    negotiated_annual_change_day = (
        negotiated_annual_change_day if negotiated_annual_change_day is not None
        else latest_exact_date.day
    )

    # Which year should we start from?
    start_year = from_date.year
    if datetime.date(start_year, negotiated_annual_change_month,
                     negotiated_annual_change_day) > from_date:
        start_year -= 1

    # Assert the invariant promised in the documentation
    assert datetime.date(start_year, negotiated_annual_change_month,
                         negotiated_annual_change_day) <= from_date

    # Start iterating over all years
    for year in itertools.count(start_year):
        change_date = datetime.date(year, negotiated_annual_change_month,
                                    negotiated_annual_change_day)

        # Is this year one for which we have an exact mapping? If so, use that
        if change_date in exact_dates:
            _, mapping = table.point_to_salary_map_for_date(change_date)
            yield change_date, mapping, False
            continue

        # Otherwise, we need to interpolate. Determine the multiplier for this year:
        year_delta = year - latest_exact_date.year
        multiplier = approximate_negotiated_annual_change ** year_delta

        # Yield an approximate table. Note that we round all approximate salaries.
        yield change_date, {
            point: int(round(salary * multiplier))
            for point, salary in latest_exact_mapping.items()
        }, True

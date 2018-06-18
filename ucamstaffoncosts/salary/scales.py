"""
Salary scales
=============

The :py:mod:`ucamstaffoncosts.salary.scales` module provides a mapping from grade and salary scale
point to an annual full-time equivalent salary in pounds sterling. Optionally, this may include a
date for which this mapping is required and the salary table will return the result from the latest
table which has an effective-from date before or equal to that one.

In this documentation, we shall use a subset of the full salary table. The YAML source for this
table is as follows:

.. literalinclude:: ../ucamstaffoncosts/data/example_salary_scales.yaml

.. testsetup::

    from ucamstaffoncosts.salary.scales import *
    import datetime
    import yaml

The table is available via the :py:data:`ucamstaffoncosts.salary.scales.EXAMPLE_SALARY_SCALES`
constant:

>>> isinstance(EXAMPLE_SALARY_SCALES, SalaryScaleTable)
True

For real data, you would want to use the :py:data:`.SALARY_SCALES` constant which is a
pre-initialised table using the most recent data available. For all calls which take a table
parameter, this table is the default.

>>> isinstance(SALARY_SCALES, SalaryScaleTable)
True

There are various clinical scales which are not represented in this table. For those, you would
want to use the :py:data:`.CLINICAL_SCALES` constant

>>> isinstance(CLINICAL_SCALES, SalaryScaleTable)
True

Using the table, one can find, as an example, the starting salary for grade 2 as of the 1st January
2017:

>>> effective_from_date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(
...     datetime.date(2017, 1, 1))
>>> effective_from_date
datetime.date(2016, 8, 1)
>>> mapping[EXAMPLE_SALARY_SCALES.scale_for_grade(Grade.GRADE_2)[0].point]
14767

Or, what their salary will be after their second anniversary:

>>> grade = Grade.GRADE_2
>>> point = EXAMPLE_SALARY_SCALES.scale_for_grade(Grade.GRADE_2)[0].point
>>> point = EXAMPLE_SALARY_SCALES.increment(grade, point) # first anniversary
>>> point = EXAMPLE_SALARY_SCALES.increment(grade, point) # second anniversary
>>> date = datetime.date(2019, 1, 1) # note: two years after start date
>>> effective_from_date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(date)
>>> effective_from_date
datetime.date(2017, 8, 1)
>>> second_anniversary_salary = mapping[point]
>>> second_anniversary_salary
15721

Note that the salary table is from the 2017 negotiated increment. No attempt is made to predict
negotiated increments into the future from this table.

On the next anniversary, the employee does not proceed to the next spine point since the employee
is now at the top non-contribution points for the grade. Hence, the salary will be the same:

>>> point = EXAMPLE_SALARY_SCALES.increment(grade, point) # third anniversary
>>> date = datetime.date(2019, 1, 1) # note: three years after start date
>>> effective_from_date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(date)
>>> effective_from_date
datetime.date(2017, 8, 1)
>>> mapping[point] == second_anniversary_salary
True

"""
import enum
import collections
import datetime

import pkg_resources
import yaml


@enum.unique
class Grade(enum.Enum):
    """
    Possible grades an employee can be employed at.

    """

    #: "T" grade
    T_GRADE = enum.auto()

    #: Grade 1
    GRADE_1 = enum.auto()

    #: Grade 2
    GRADE_2 = enum.auto()

    #: Grade 3
    GRADE_3 = enum.auto()

    #: Grade 4
    GRADE_4 = enum.auto()

    #: Grade 5
    GRADE_5 = enum.auto()

    #: Grade 6
    GRADE_6 = enum.auto()

    #: Grade 7
    GRADE_7 = enum.auto()

    #: Grade 8
    GRADE_8 = enum.auto()

    #: Grade 9
    GRADE_9 = enum.auto()

    #: Grade 10
    GRADE_10 = enum.auto()

    #: Grade 11
    GRADE_11 = enum.auto()

    #: Grade 12 band 1
    GRADE_12_BAND_1 = enum.auto()

    #: Grade 12 band 2
    GRADE_12_BAND_2 = enum.auto()

    #: Grade 12 band 3
    GRADE_12_BAND_3 = enum.auto()

    #: Grade 12 band 4
    GRADE_12_BAND_4 = enum.auto()

    #: Clinical nodal points
    CLINICAL_NODAL = enum.auto()

    #: Clinical consultant
    CLINICAL_CONSULTANT = enum.auto()

    #: Clinical research associate or lecturer
    CLINICAL_RA_AND_LECTURER = enum.auto()


class SalaryScaleTable:
    """
    An encapsulation of the `salary scale table
    <https://www.hr.admin.cam.ac.uk/pay-benefits/salary-scales>`_ available on the HR website.

    :param data: a data table whose format is epitomised by the :download:`example
        <../ucamstaffoncosts/data/example_salary_scales.yaml>` used in this documentation.
    :type data: dict

    """

    _ScaleRow = collections.namedtuple('ScaleRow', 'name point is_contribution')

    class ScaleRow(_ScaleRow):
        """
        A :py:class:`collections.namedtuple` subclass which represents a row from the salary scale
        for a particular grade.

        .. py:attribute:: name

            The name of this point on the salary scale

        .. py:attribute:: point

            The name of this point on the spine. This is the name used in the table returned by
            :py:meth:`~.point_to_salary_map_for_date`.

        .. py:attribute:: is_contribution

            Boolean indicating if this is a contribution point and not subject to annual
            increments.

        """

    def __init__(self, data):
        self._data = data

        def to_row(item):
            return SalaryScaleTable.ScaleRow(
                name=item['name'], point=item['point'], is_contribution=item['isContribution']
            )

        # Construct a dictionary mapping Grade values into lists of ScaleRows.
        self._scales_by_grade = {
            getattr(Grade, item['name']): [to_row(row) for row in item['scale']]
            for item in self._data['grades']
        }

        # Mappings are sorted by *descending* date
        self._mappings = sorted(
            self._data['salaries'], key=lambda item: item['effectiveDate'], reverse=True
        )

    def increment(self, grade, point):
        """
        Return the salary scale point which is the next annual increment from the specified grade
        and point. If there is no further increment, return the value of *point*. Note that *point*
        is the *spine point*, name as used by the table returned by
        :py:meth:`~.point_to_salary_map_for_date`.

        :param grade: grade of employee
        :type grade: :py:class:`ucamstaffoncosts.Grade`
        :param point: existing spine point for employee
        :type point: str

        Let's look at the scale for grade 1:

        >>> EXAMPLE_SALARY_SCALES.scale_for_grade(Grade.GRADE_1) # doctest: +NORMALIZE_WHITESPACE
        [ScaleRow(name='X1', point='P1', is_contribution=False),
        ScaleRow(name='X2', point='P2', is_contribution=False),
        ScaleRow(name='X3', point='P3', is_contribution=False),
        ScaleRow(name='X4', point='P4', is_contribution=True)]

        Normal increments will return the next point:

        >>> EXAMPLE_SALARY_SCALES.increment(Grade.GRADE_1, 'P1')
        'P2'

        Increments do not move to contribution points:

        >>> EXAMPLE_SALARY_SCALES.increment(Grade.GRADE_1, 'P3')
        'P3'

        Contribution points also do not increment:

        >>> EXAMPLE_SALARY_SCALES.increment(Grade.GRADE_1, 'P4')
        'P4'

        Note that the spine point must be in the salary progression for the grade otherwise an
        exception is raised:

        >>> EXAMPLE_SALARY_SCALES.increment(Grade.GRADE_1, 'P5')
        Traceback (most recent call last):
            ...
        ValueError: point "P5" is not part of grade "Grade.GRADE_1"

        """
        # Get salary scale for grade
        scale = self.scale_for_grade(grade)

        # Find index of the specified point in the grade
        index, current_row = next(
            ((i, row) for i, row in enumerate(scale) if row.point == point), (None, None)
        )
        if index is None:
            raise ValueError(f'point "{point!s}" is not part of grade "{grade!s}"')

        # If this is the last point on the scale, or if this is a contribution point, there is no
        # increment
        if index == len(scale) - 1 or current_row.is_contribution:
            return point

        # Otherwise, find the next row
        next_row = scale[index + 1]

        # If *this* is a contribution point then the employee does not automatically advance
        if next_row.is_contribution:
            return point

        # Otherwise, return the next point
        return next_row.point

    def scale_for_grade(self, grade):
        """
        Return the salary scale for a given grade. The scale is ordered in increasing order of
        spine point so that they represent the progression through spine points from annual
        increments.

        :param grade: grade whose scale should be returned
        :type grade: :py:class:`ucamstaffoncosts.Grade`

        >>> EXAMPLE_SALARY_SCALES.scale_for_grade(Grade.GRADE_1) # doctest: +NORMALIZE_WHITESPACE
        [ScaleRow(name='X1', point='P1', is_contribution=False),
        ScaleRow(name='X2', point='P2', is_contribution=False),
        ScaleRow(name='X3', point='P3', is_contribution=False),
        ScaleRow(name='X4', point='P4', is_contribution=True)]

        Note that the grade *must* be a :py:class:`~ucamstaffoncosts.Grade`:

        >>> EXAMPLE_SALARY_SCALES.scale_for_grade('GRADE_1') # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        KeyError: ...

        """
        return self._scales_by_grade[grade]

    def starting_point_for_grade(self, grade):
        """Convenience wrapper around :py:meth:`~.scale_for_grade` which returns the name of the
        first point on the scale for a given grade.

        >>> EXAMPLE_SALARY_SCALES.starting_point_for_grade(Grade.GRADE_2)
        'P3'

        """
        return self.scale_for_grade(grade)[0].point

    def point_to_salary_map_effective_dates(self):
        """
        Return a list of effective-from dates for each point to salary mapping we know about. These
        are ordered in *descending* order of dates.

        >>> EXAMPLE_SALARY_SCALES.point_to_salary_map_effective_dates()
        [datetime.date(2017, 8, 1), datetime.date(2016, 8, 1)]

        """
        return [mapping['effectiveDate'] for mapping in self._mappings]

    def point_to_salary_map_for_date(self, date=None):
        """
        Return a salary table mapping for a given date. The mapping table is a dictionary which
        maps point names to full-time equivalent salaries. The return value is an (effective date,
        table) pair giving the table and the date from which it became effective.

        :param date: date for which mapping is required. If ``None``, use today's date
        :type date: :py:class:`datetime.date`

        The exact mapping is selected based upon the date:

        >>> date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(
        ...     datetime.date(2017, 5, 1))
        >>> mapping == {
        ... 'P1': 13965, 'P2': 14327, 'P3': 14767, 'P4': 15052, 'P5': 15356, 'P6': 15670,
        ... 'P7': 15976, 'P8': 16289}
        True
        >>> date == datetime.date(2016, 8, 1)
        True
        >>> date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(
        ...     datetime.date(2018, 5, 1))
        >>> mapping == {
        ... 'P1': 14304, 'P2': 14675, 'P3': 15126, 'P4': 15417, 'P5': 15721, 'P6': 16035,
        ... 'P7': 16341, 'P8': 16654}
        True
        >>> date == datetime.date(2017, 8, 1)
        True

        If no date is specified, today's date is used as a default:

        >>> d1, m1 = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date()
        >>> d2, m2 = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(
        ...     datetime.datetime.now().date())
        >>> d1 == d2
        True
        >>> m1 == m2
        True

        If a date matches the effective from date, it returns the corresponding mapping:

        >>> date, mapping = EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(
        ...     datetime.date(2016, 8, 1))
        >>> mapping == {
        ... 'P1': 13965, 'P2': 14327, 'P3': 14767, 'P4': 15052, 'P5': 15356, 'P6': 15670,
        ... 'P7': 15976, 'P8': 16289}
        True
        >>> date == datetime.date(2016, 8, 1)
        True

        If a date is specified which is too far in the future, a :py:exc:`ValueError` is raised:

        >>> EXAMPLE_SALARY_SCALES.point_to_salary_map_for_date(datetime.date(2016, 7, 31))
        Traceback (most recent call last):
            ...
        ValueError: date is too far in the past

        """
        if date is None:
            date = datetime.datetime.now().date()

        # Iterate through mapping tables until we find the first table whose effective date is on
        # or before the target date. Since the mapping table is sorted by descending date, this
        # will be the most recent table for that date. We iterate through in reverse order like
        # this so that the common case (give me the most recent one) is efficient.
        for mapping in self._mappings:
            if mapping['effectiveDate'] <= date:
                return mapping['effectiveDate'], mapping['mapping']

        # If no mapping was found, complain.
        raise ValueError('date is too far in the past')


EXAMPLE_SALARY_SCALES = SalaryScaleTable(yaml.load(pkg_resources.resource_string(
    'ucamstaffoncosts', 'data/example_salary_scales.yaml')))


SALARY_SCALES = SalaryScaleTable(
    yaml.load(pkg_resources.resource_string('ucamstaffoncosts', 'data/salary_scales.yaml')))

CLINICAL_SCALES = SalaryScaleTable(
    yaml.load(pkg_resources.resource_string('ucamstaffoncosts', 'data/clinical_scales.yaml')))

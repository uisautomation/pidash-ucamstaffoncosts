University of Cambridge Staff On-costs Calculator
=================================================

.. toctree::
    :hidden:

The ``ucamstaffoncosts`` module calculates total on-costs associated with
employing staff members in the University of Cambridge. The total on-costs value
calculated by this module reflects the expenditure which will result from
employing a staff member on a grant.

The aim is to replicate the `information
<https://www.hr.admin.cam.ac.uk/Salaries/242>`_ available on the University HR's
website using only the publicly available rates.

Installation
------------

Installation is best done via pip:

.. code:: console

    $ pip install git+https://github.com/uisautomation/pidash-ucamstaffoncosts

Example
-------

Our example employee will have the following attributes:

- They are currently at the bottom of grade 2:

    >>> from ucamstaffoncosts.salary.scales import EXAMPLE_SALARY_SCALES
    >>> initial_grade = Grade.GRADE_2
    >>> initial_point = EXAMPLE_SALARY_SCALES.starting_point_for_grade(initial_grade)

- Their next employment anniversary is on the 1st June 2016:

    >>> next_anniversary_date = datetime.date(2016, 6, 1)

- They are on the USS salary exchange pension scheme:

    >>> scheme = Scheme.USS_EXCHANGE

- Their contract started on 1st April 2015:

    >>> start_date = datetime.date(2015, 4, 1)

- Their contract ends on 30th September and so they are no-longer employed from
  the 1st October:

    >>> until_date = datetime.date(2020, 10, 1)

- The date from which we want to calculate the commitments is the 1st February
  2016:

    >>> from_date = datetime.date(2016, 2, 1)

We can use the :py:func:`~.employment_expenditure_and_commitments` function to
calculate the total commitment for employing this staff member as of
*from_date*:

>>> import ucamstaffoncosts
>>> expenditure, commitments, explanations = ucamstaffoncosts.employment_expenditure_and_commitments(
...     until_date, initial_grade, initial_point, scheme, start_date=start_date,
...     from_date=from_date, next_anniversary_date=next_anniversary_date,
...     scale_table=EXAMPLE_SALARY_SCALES)
>>> expenditure
14814
>>> commitments
90153

This number seems a little arbitrary so we can use the provided list of
explanations to explain the calculation:

>>> from ucamstaffoncosts.util import pprinttable
>>> def print_explanations(explanations):
...     running_commitment = 0
...     for explanation in explanations:
...         print('=' * 60)
...         print('TAX YEAR: {}/{}'.format(explanation.tax_year, explanation.tax_year+1))
...         print('\nSalaries\n--------\n')
...         pprinttable(explanation.salaries)
...         print('\nCosts\n-----')
...         if explanation.cost.tax_year != explanation.tax_year:
...             print('(approximated using tax tables for {})'.format(explanation.cost.tax_year))
...         print('\n')
...         pprinttable([explanation.cost])
...         print('\nSalary for year: {}'.format(explanation.salary))
...         print('Salary earned after {}: {}'.format(from_date, explanation.salary_to_come))
...         print('Expenditure until {}: {}'.format(from_date, explanation.expenditure))
...         print('Commitment from {}: {}'.format(from_date, explanation.commitment))
...         running_commitment += explanation.commitment
...         print('Running total commitment: {}'.format(running_commitment))
...         print('\n')
>>> print_explanations(explanations) # doctest: +NORMALIZE_WHITESPACE
============================================================
TAX YEAR: 2015/2016
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason          | grade         | point | base_salary | mapping_table_date
-----------+-----------------+---------------+-------+-------------+-------------------
2015-04-01 | employee start  | Grade.GRADE_2 | P3    | 14254       | 2014-08-01        
2015-04-06 | end of tax year | Grade.GRADE_2 | P3    | 14254       | 2014-08-01        
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2019)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
195    | -16      | 51               | 0            | 0                   | 230   | 2019    
<BLANKLINE>
Salary for year: 195
Salary earned after 2016-02-01: 0
Expenditure until 2016-02-01: 230
Commitment from 2016-02-01: 0
Running total commitment: 0
<BLANKLINE>
<BLANKLINE>
============================================================
TAX YEAR: 2015/2016
<BLANKLINE>
Salaries
--------
<BLANKLINE>
date       | reason                         | grade         | point | base_salary | mapping_table_date
-----------+--------------------------------+---------------+-------+-------------+-------------------
2015-04-06 | start of tax year              | Grade.GRADE_2 | P3    | 14254       | 2014-08-01        
2015-08-01 | new salary table (approximate) | Grade.GRADE_2 | P3    | 14539       | 2015-08-01        
2016-04-06 | end of tax year                | Grade.GRADE_2 | P3    | 14539       | 2015-08-01        
<BLANKLINE>
Costs
-----
(approximated using tax tables for 2019)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
14448  | -1156    | 3756             | 643          | 66                  | 17757 | 2019    
<BLANKLINE>
Salary for year: 14448
Salary earned after 2016-02-01: 2582
Expenditure until 2016-02-01: 14584
Commitment from 2016-02-01: 3173
Running total commitment: 3173
<BLANKLINE>
<BLANKLINE>
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
(approximated using tax tables for 2019)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
14934  | -1195    | 3883             | 705          | 68                  | 18395 | 2019    
<BLANKLINE>
Salary for year: 14934
Salary earned after 2016-02-01: 14934
Expenditure until 2016-02-01: 0
Commitment from 2016-02-01: 18395
Running total commitment: 21568
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
(approximated using tax tables for 2019)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
15557  | -1245    | 4045             | 784          | 71                  | 19212 | 2019    
<BLANKLINE>
Salary for year: 15557
Salary earned after 2016-02-01: 15557
Expenditure until 2016-02-01: 0
Commitment from 2016-02-01: 19212
Running total commitment: 40780
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
Salary for year: 15934
Salary earned after 2016-02-01: 15934
Expenditure until 2016-02-01: 0
Commitment from 2016-02-01: 19735
Running total commitment: 60515
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
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
16253  | -1300    | 4226             | 872          | 74                  | 20125 | 2019    
<BLANKLINE>
Salary for year: 16253
Salary earned after 2016-02-01: 16253
Expenditure until 2016-02-01: 0
Commitment from 2016-02-01: 20125
Running total commitment: 80640
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
(approximated using tax tables for 2019)
<BLANKLINE>
<BLANKLINE>
salary | exchange | employer_pension | employer_nic | apprenticeship_levy | total | tax_year
-------+----------+------------------+--------------+---------------------+-------+---------
8031   | -642     | 2088             | 0            | 36                  | 9513  | 2019    
<BLANKLINE>
Salary for year: 8031
Salary earned after 2016-02-01: 8031
Expenditure until 2016-02-01: 0
Commitment from 2016-02-01: 9513
Running total commitment: 90153
<BLANKLINE>
<BLANKLINE>

If *initial_grade* is ``None``, the mapping table will still be used but annual
increments will not be processed which means that the total expenditure and
commitments will be lower:

>>> expenditure, commitments, explanations = ucamstaffoncosts.employment_expenditure_and_commitments(
...     until_date, None, initial_point, scheme, start_date=start_date,
...     from_date=from_date, next_anniversary_date=next_anniversary_date,
...     scale_table=EXAMPLE_SALARY_SCALES)
>>> expenditure
14814
>>> commitments
87166


Reference
---------

.. automodule:: ucamstaffoncosts
    :members:
    :member-order: bysource

.. automodule:: ucamstaffoncosts.costs
    :members:
    :member-order: bysource
    :exclude-members: Scheme, Cost

.. automodule:: ucamstaffoncosts.salary.progression
    :members:
    :member-order: bysource
    :exclude-members: SalaryRecord

.. automodule:: ucamstaffoncosts.salary.scales
    :members:
    :member-order: bysource
    :exclude-members: Grade

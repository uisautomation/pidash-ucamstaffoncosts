University of Cambridge Staff On-costs Calculator
=================================================

.. toctree::
    :maxdepth: 2
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

The functionality of the module is exposed through a single function,
:py:func:`~ucamstaffoncosts.on_cost`, which takes a tax year, pension scheme and
base salary and returns an :py:class:`~ucamstaffoncosts.OnCost` object
representing the on-costs for that employee:

.. doctest::
    :options: +NORMALIZE_WHITESPACE

    >>> import ucamstaffoncosts
    >>> ucamstaffoncosts.on_cost(base_salary=25000,
    ...                          scheme=ucamstaffoncosts.Scheme.USS, year=2018)
    OnCost(salary=25000, exchange=0, employer_pension=4500,
           employer_nic=2287, apprenticeship_levy=125, total=31912)

The :py:attr:`~ucamstaffoncosts.OnCost.total` attribute from the return value
can be used to forecast total expenditure for an employee in a given tax year.

If *year* is omitted, then the latest tax year which has any calculators
implemented is used. This behaviour can also be signalled by using the special
value :py:const:`~ucamstaffoncosts.LATEST`:

.. doctest::
    :options: +NORMALIZE_WHITESPACE

    >>> import ucamstaffoncosts
    >>> ucamstaffoncosts.on_cost(base_salary=25000,
    ...                          scheme=ucamstaffoncosts.Scheme.USS,
    ...                          year=ucamstaffoncosts.LATEST)
    OnCost(salary=25000, exchange=0, employer_pension=4500,
           employer_nic=2287, apprenticeship_levy=125, total=31912)
    >>> ucamstaffoncosts.on_cost(base_salary=25000,
    ...                          scheme=ucamstaffoncosts.Scheme.USS)
    OnCost(salary=25000, exchange=0, employer_pension=4500,
           employer_nic=2287, apprenticeship_levy=125, total=31912)


Reference
---------

.. automodule:: ucamstaffoncosts
    :members:

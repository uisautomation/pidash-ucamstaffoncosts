# University of Cambridge Salary On-cost Calculation

[![CircleCI](https://circleci.com/gh/uisautomation/pidash-ucamstaffoncosts.svg?style=svg)](https://circleci.com/gh/uisautomation/pidash-ucamstaffoncosts)

This repository contains a Python module which calculates total on-costs
associated with employing staff members in the University of Cambridge. The
total on-costs value calculated by this module reflects the expenditure which
will result from employing a staff member on a grant.

The aim is to replicate the
[information](https://www.hr.admin.cam.ac.uk/Salaries/242) available on the
University HR's website using only the publicly available rates.

[Documentation](https://uisautomation.github.io/pidash-ucamstaffoncosts/) is
available on this repository's GitHub pages.

## Example

The functionality of the module is exposed through a single function,
``on_cost()``, which takes a tax year, pension scheme and gross salary and
returns an ``OnCost`` object representing the on-costs for that employee:

```python
>>> import ucamstaffoncosts
>>> ucamstaffoncosts.on_cost(gross_salary=25000,
...                          scheme=ucamstaffoncosts.Scheme.USS, year=2018)
OnCost(salary=25000, exchange=0, employer_pension=4500,
       employer_nic=2287, apprenticeship_levy=125, total=31912)
```

## Configuring CircleCI

The CircleCI workflow includes automatically building and pushing documentation
to GitHub pages whenever there is a commit to the master branch. In order to
enable this, a personal access token for a robot user must be generated and
added to the CircleCI configuration as the ``GITHUB_TOKEN`` environment
variable.

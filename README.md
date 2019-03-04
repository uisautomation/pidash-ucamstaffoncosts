# University of Cambridge Salary On-cost Calculation

> **This repository has been moved to https://gitlab.developers.cam.ac.uk/uis/devops/research-dashboard/ucamstaffoncosts/**

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

## Configuring CircleCI

The CircleCI workflow includes automatically building and pushing documentation
to GitHub pages whenever there is a commit to the master branch. In order to
enable this, a personal access token for a robot user must be generated and
added to the CircleCI configuration as the ``GITHUB_TOKEN`` environment
variable.

## Running JupyterLab

A [docker-compose configuration](jupyter.yml) for running
[JupyterLab](http://jupyterlab.readthedocs.io/en/stable/index.html) is included.
Start the server using the ``docker-compose`` command:

```bash
$ docker-compose -f jupyter.yml up
```

Follow the http://localhost:8888/ link printed to the console. This repository
is mounted read-only at ``~/repo/`` and a persistent volume is mounted to the
workspace at ``~/work``. The ``ucamstaffoncosts`` module is pre-installed into
the JupyterLab environment.

Source data used by ucamstaffoncosts
====================================

The following files and scripts are used to generate the data in the [data
folder](../ucamstaffoncosts/data) used by ``ucamstaffoncosts``.

Salary scales
-------------

The [source
data](https://www.hr.admin.cam.ac.uk/files/single_salary_spine_as_at_1_august_2017_.xlsx)
was downloaded from the Cambridge HR [salary scales
site](https://www.hr.admin.cam.ac.uk/pay-benefits/salary-scales) and then
written to the data folder using the following command:

```bash
$ ./parsesalarytable.py \
	--output ../ucamstaffoncosts/data/salary_scales.yaml \
	single_salary_spine_as_at_1_august_2017_.xlsx
```

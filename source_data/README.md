Source data used by ucamstaffoncosts
====================================

The following files and scripts are used to generate the data in the [data
folder](../ucamstaffoncosts/data) used by ``ucamstaffoncosts``.

Cambridge Salary Scales
-----------------------

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

Clinical Salary Scales
----------------------

The source data comes from the following sources:

* https://www.hr.admin.cam.ac.uk/pay-benefits/salary-scales/clinical-nodal-points
* https://www.hr.admin.cam.ac.uk/pay-benefits/salary-scales/clinical-research-associates-and-clinical-lecturers
* https://www.hr.admin.cam.ac.uk/pay-benefits/salary-scales/clinical-consultants

Copies of these have been saved to files with matching filenames ending in
``.html``. These have then been run through [html2csv.py](html2csv.py) to
generate matching CSV files.

The clinical scale is then created via:

```bash
$ ./clinical_scales.py --output ../ucamstaffoncosts/data/clinical_scales.yaml
```

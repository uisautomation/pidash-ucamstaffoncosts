# Hashed private data

This directory contains SHA256 checksums of private data from the HR website.

## On-costs

Hashes for the on-cost tables are generated in the following way:

* The [HR on-costs tables](https://www.hr.admin.cam.ac.uk/Salaries/242) are
  copied and pasted as plain text. On Firefox, this results in tab-separated
  files.

* These TSV files are normalised via [normalise.py](normalise.py) into CSV
  files using the following command:

```bash
$ for i in *.tsv; do ./normalise.py <$i >$(basename $i .tsv).csv; done
```

* The files are checksummed via ``sha256sum``:

```bash
$ sha256sum *.csv >on-costs-hashes.txt
```

The CSV and TSV files have been added to .gitignore to ensure that they are not
inadvertently checked in.

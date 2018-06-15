"""
General utility functions.

"""


def pprinttable(rows):
    """Adapted from: https://stackoverflow.com/questions/5909873

    >>> import collections
    >>> Row = collections.namedtuple('Row', 'foo bar buzz')
    >>> pprinttable([
    ...     Row('one', 'two', 'three'), Row(1, 2, 3),
    ... ]) # doctest: +NORMALIZE_WHITESPACE
    foo | bar | buzz
    ----+-----+------
    one | two | three
    1   | 2   | 3
    """
    headers = rows[0]._fields
    lens = []
    for i in range(len(rows[0])):
        lens.append(
            len(max([str(x[i]) for x in rows] + [headers[i]], key=lambda x: len(str(x)))))
    formats = []
    hformats = []
    for i in range(len(rows[0])):
        formats.append("%%-%ds" % lens[i])
        hformats.append("%%-%ds" % lens[i])
    pattern = " | ".join(formats)
    hpattern = " | ".join(hformats)
    separator = "-+-".join(['-' * n for n in lens])
    print(hpattern % tuple(headers))
    print(separator)

    for line in rows:
        print(pattern % tuple(str(t) for t in line))

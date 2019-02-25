import collections
import enum
import fractions


@enum.unique
class Scheme(enum.Enum):
    """
    Possible pension schemes an employee can be a member of.

    """

    #: No pension scheme.
    NONE = enum.auto()

    #: CPS hybrid
    CPS_HYBRID = enum.auto()

    #: CPS hybrid with salary exchange
    CPS_HYBRID_EXCHANGE = enum.auto()

    #: USS
    USS = enum.auto()

    #: USS with salary exchange
    USS_EXCHANGE = enum.auto()

    #: NHS
    NHS = enum.auto()

    #: MRC
    MRC = enum.auto()

    #: CPS pre-2013
    CPS_PRE_2013 = enum.auto()

    #: CPS pre-2013 with salary exchange
    CPS_PRE_2013_EXCHANGE = enum.auto()


#: A tuple holding the employer and employee rates for a pension scheme.
Rate = collections.namedtuple('Rate', 'employer employee')


def is_exchange(scheme):
    """
    Return a flag indicating if the passed scheme is a salary exchange scheme

    >>> is_exchange(Scheme.NONE)
    False
    >>> is_exchange(Scheme.CPS_HYBRID)
    False
    >>> is_exchange(Scheme.USS)
    False
    >>> is_exchange(Scheme.CPS_PRE_2013)
    False
    >>> is_exchange(Scheme.NHS)
    False
    >>> is_exchange(Scheme.MRC)
    False
    >>> is_exchange(Scheme.CPS_HYBRID_EXCHANGE)
    True
    >>> is_exchange(Scheme.USS_EXCHANGE)
    True
    >>> is_exchange(Scheme.CPS_PRE_2013_EXCHANGE)
    True
    """
    return scheme in _EXCHANGE_SCHEMES


def scheme_rates(scheme, from_date):
    """
    Return an iterable of (date, Rate) tuples for the passed pension scheme. The date is the date
    when that rate becomes valid. The first date will always equal *from_date*.

    Some schemes are simple and have a single rate:

    >>> import datetime
    >>> list(scheme_rates(Scheme.NHS, datetime.date(year=2010, month=1, day=1)))
    [(datetime.date(2010, 1, 1), Rate(employer=Fraction(719, 5000), employee=0))]

    Salary exchange schemes are, from the point of view of rates, are equal to non-exchange
    schemes:

    >>> list(scheme_rates(Scheme.CPS_PRE_2013, datetime.date(year=2030, month=1, day=1)))
    [(datetime.date(2030, 1, 1), Rate(employer=Fraction(237, 1000), employee=Fraction(1, 20)))]
    >>> list(scheme_rates(Scheme.CPS_PRE_2013_EXCHANGE, datetime.date(year=2030, month=1, day=1)))
    [(datetime.date(2030, 1, 1), Rate(employer=Fraction(237, 1000), employee=Fraction(1, 20)))]

    """  # noqa: E501
    rates = _SCHEME_TO_RATES[scheme]

    start_dates = [d for d, _ in rates]
    end_dates = [d for d, _ in rates[1:]] + [None]

    for entry, start, end in zip(rates, start_dates, end_dates):
        if end is not None and end <= from_date:
            continue

        if start is None:
            start = from_date

        yield max(from_date, start), entry[1]


#: A set of pension schemes which are salary exchange schemes
_EXCHANGE_SCHEMES = {
    Scheme.USS_EXCHANGE, Scheme.CPS_HYBRID_EXCHANGE, Scheme.CPS_PRE_2013_EXCHANGE,
}


#: A pension scheme to ordered Rate tuples map. Each scheme's rates are recorded with a date
#: interval with the earliest date at which the rate applies or "None" if that rate applied for all
#: time.
_SCHEME_TO_RATES = {
    Scheme.NONE: [
        (None, Rate(employer=0, employee=0)),
    ],

    #: Rate of USS employer contribution.
    #: Related website
    #: https://www.uss.co.uk/~/media/document-libraries/uss/member/member-guides/post-april-2016/your-guide-to-universities-superannuation-scheme.pdf  # noqa: E501
    Scheme.USS: [
        (
            None,
            Rate(employer=fractions.Fraction(180, 1000), employee=fractions.Fraction(80, 1000))
        ),
    ],

    #: Rate of CPS employee contribution. Taken from CPS website at
    #: https://www.pensions.admin.cam.ac.uk/files/8cps_hybrid_contributions_march_2017.pdf
    Scheme.CPS_HYBRID: [
        (None, Rate(employer=fractions.Fraction(237, 1000), employee=fractions.Fraction(3, 100))),
    ],

    Scheme.CPS_PRE_2013: [
        (None, Rate(employer=fractions.Fraction(237, 1000), employee=fractions.Fraction(5, 100))),
    ],

    #: Rate of NHS employer contribution. Taken from NHS website at:
    #: http://www.nhsemployers.org/your-workforce/pay-and-reward/pensions/pension-contribution-tax-relief  # noqa: E501
    Scheme.NHS: [
        (None, Rate(employer=fractions.Fraction(1438, 10000), employee=0)),
    ],

    #: Rate or MRC employer contribution.Taken from
    #: https://mrc.ukri.org/about/our-structure/council/mrc-legacy-council/meeting-dates-agendas-minutes/december-2017-council-business-meeting-minutes-pdf/  # noqa: E501
    Scheme.MRC: [
        (None, Rate(employer=fractions.Fraction(159, 1000), employee=0)),
    ],
}

# Exchange schemes are, from the point of view of rates, identical to their non-exchange
# equivalents.
_SCHEME_TO_RATES[Scheme.CPS_HYBRID_EXCHANGE] = _SCHEME_TO_RATES[Scheme.CPS_HYBRID]
_SCHEME_TO_RATES[Scheme.CPS_PRE_2013_EXCHANGE] = _SCHEME_TO_RATES[Scheme.CPS_PRE_2013]
_SCHEME_TO_RATES[Scheme.USS_EXCHANGE] = _SCHEME_TO_RATES[Scheme.USS]

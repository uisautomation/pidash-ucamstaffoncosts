import fractions

#: Rate of apprenticeship levy. This is not expected to change every tax year so it is added as an
#: un-dated constant. Taken from:
#: https://www.gov.uk/guidance/pay-apprenticeship-levy#how-much-you-need-to-pay
APPRENTICESHIP_LEVY_RATE = fractions.Fraction(5, 1000)  # 0.5%

#: Rate of USS employer contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant. Taken from USS website at
#: https://www.uss.co.uk/~/media/document-libraries/uss/member/member-guides/post-april-2016/your-guide-to-universities-superannuation-scheme.pdf  # noqa: E501
USS_EMPLOYER_RATE = fractions.Fraction(18, 100)  # 18%

#: Rate of USS employee contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant. Taken from USS website at
#: https://www.uss.co.uk/~/media/document-libraries/uss/member/member-guides/post-april-2016/your-guide-to-universities-superannuation-scheme.pdf  # noqa: E501
USS_EMPLOYEE_RATE = fractions.Fraction(8, 100)  # 8%

#: Rate of CPS employee contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant. Taken from CPS website at
#: https://www.pensions.admin.cam.ac.uk/files/8cps_hybrid_contributions_march_2017.pdf
CPS_HYBRID_EMPLOYEE_RATE = fractions.Fraction(3, 100)  # 3%

#: Rate of CPS employer contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant.
#: FIXME: where does this come from?
CPS_HYBRID_EMPLOYER_RATE = fractions.Fraction(237, 1000)  # 23.7%

#: Rate of CPS pre-2013 employee contribution. This is not expected to change every tax year so it
#: is added as an un-dated constant.
#: FIXME: where does this come from?
CPS_PRE_2013_EMPLOYEE_RATE = fractions.Fraction(5, 100)  # 5%

#: Rate of CPS pre-2013 employer contribution. This is not expected to change every tax year so it
#: is added as an un-dated constant.
#: FIXME: where does this come from?
CPS_PRE_2013_EMPLOYER_RATE = fractions.Fraction(237, 1000)  # 23.7%

#: Rate of NHS employer contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant. Taken from NHS website at:
#: http://www.nhsemployers.org/your-workforce/pay-and-reward/pensions/pension-contribution-tax-relief  # noqa: E501
NHS_EMPLOYER_RATE = fractions.Fraction(1438, 10000)  # 14.38%

#: Rate or MRC employer contribution. This is not expected to change every tax year so it is added
#: as an un-dated constant. Taken from
#: https://mrc.ukri.org/about/our-structure/council/mrc-legacy-council/meeting-dates-agendas-minutes/december-2017-council-business-meeting-minutes-pdf/  # noqa: E501
MRC_EMPLOYER_RATE = fractions.Fraction(159, 1000)  # 15.9%

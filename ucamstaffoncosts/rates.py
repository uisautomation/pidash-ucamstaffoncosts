import fractions

#: Rate of apprenticeship levy. This is not expected to change every tax year so it is added as an
#: un-dated constant. Taken from:
#: https://www.gov.uk/guidance/pay-apprenticeship-levy#how-much-you-need-to-pay
APPRENTICESHIP_LEVY_RATE = fractions.Fraction(5, 1000)  # 0.5%

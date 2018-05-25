from . import rates


def uss_employer_contribution(gross_salary):
    """
    Return the USS employer contribution from gross salary.

    """
    return gross_salary * rates.USS_EMPLOYER_RATE


def uss_employee_contribution(gross_salary):
    """
    Return the USS employee contribution from gross salary.

    """
    return gross_salary * rates.USS_EMPLOYEE_RATE


def cps_hybrid_employer_contribution(gross_salary):
    """
    Return the CPS_HYBRID employer contribution from gross salary.

    """
    return gross_salary * rates.CPS_HYBRID_EMPLOYER_RATE


def cps_hybrid_employee_contribution(gross_salary):
    """
    Return the CPS_HYBRID employee contribution from gross salary.

    """
    return gross_salary * rates.CPS_HYBRID_EMPLOYEE_RATE


def nhs_employer_contribution(gross_salary):
    """
    Return the NHS employer contribution.

    """
    return gross_salary * rates.NHS_EMPLOYER_RATE

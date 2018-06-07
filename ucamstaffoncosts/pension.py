from . import rates


def uss_employer_contribution(base_salary):
    """
    Return the USS employer contribution from base salary.

    """
    return base_salary * rates.USS_EMPLOYER_RATE


def uss_employee_contribution(base_salary):
    """
    Return the USS employee contribution from base salary.

    """
    return base_salary * rates.USS_EMPLOYEE_RATE


def cps_hybrid_employer_contribution(base_salary):
    """
    Return the CPS_HYBRID employer contribution from base salary.

    """
    return base_salary * rates.CPS_HYBRID_EMPLOYER_RATE


def cps_hybrid_employee_contribution(base_salary):
    """
    Return the CPS_HYBRID employee contribution from base salary.

    """
    return base_salary * rates.CPS_HYBRID_EMPLOYEE_RATE


def nhs_employer_contribution(base_salary):
    """
    Return the NHS employer contribution.

    """
    return base_salary * rates.NHS_EMPLOYER_RATE

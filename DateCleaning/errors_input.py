import numpy as np
import math
import datetime

"""
Module that checks if the input corresponds to the required criteria
"""


def check_input(date):
    """
    Remove words that are useless and negatively affect the end results

    :param date: Date string to parse
    :type date: str
    :return: Cleaned date string with useless keywords removed
    :rtype: str
    """
    date_split = date.split()
    clean_date = [elem for elem in date_split if elem not in ["date", "dated", "dating", "epoch", "epoque", "unkown"]]
    return " ".join(clean_date)


def check_errors(date, time):
    """
    Function that performs multiple checks to verify that the input has no error (in terms of format and content)

    :param date: Input date
    :type date: str
    :param time: Time dictionary with time metadata
    :type time: dict
    :return: Boolean that indicates if an error has been found. False if error.
    :rtype: bool
    """
    if type(date) == int or isinstance(date, np.int64) or type(date) == float:
        if math.isnan(date):
            time["date_start"] = ""
            time["date_end"] = ""
            return False
        date = str(int(date))
    if isinstance(date, datetime.date):
        time["date_english"] = str(date.year)
        time["date_start"] = int(date.year)
        time["date_end"] = int(date.year)
        time["date_original_lang"] = "en"
        return False
    if type(date) != str:
        raise ValueError("Input must be of type str or int.")
    split = date.lower().split()
    if date == "NULL" or date == "" or date == "uncertain" or date == "indeterminate" \
            or "unknown" in split or "undated" in split:
        time["date_original_lang"] = None
        time["date_start"] = ""
        time["date_end"] = ""
        return False
    return True

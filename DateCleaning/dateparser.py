import re
from . import settings
from .package_logging import log

"""
Module that replaces the pip dateparser package. Dateparser directly looks for a correctly formatted date
"""


def search_year(date, idx):
    """
    Searches the element that corresponds to the year (for ex, the year in "01/01/10")

    :param date: Date to parse
    :type date: list
    :param idx: Index of the regex that the date matched to
    :type idx: int
    :return: Year if found. None if there is an error in the date format
    :rtype: int
    """
    first = int(date[0])
    second = int(date[1])
    third = int(date[2])
    if idx == 0:
        if first > 31 or second > 31 or (first > 12 and second > 12):
            return None
        year = third
    elif idx == 1:
        if third > 31 or second > 31 or (third > 12 and second > 12):
            return None
        year = first
    else:
        if third < 32 and second < 32 and first > 31 and (third < 13 or second < 13):
            year = 1900 + first if first < 100 else first
        elif third < 32 and first < 32 and second > 31 and (third < 13 or first < 13):
            year = 1900 + second if second < 100 else second
        elif first < 32 and second < 32 and (first < 13 or second < 13):
            year = 1900 + third if third < 100 else third
        else:
            return None
    return year


def handle_date(text, idx):
    """
    If the date matches to a regex format, checks if the length of the date is correct (equal to 3) and calls the
    functions that looks for the year

    :param text: Date to parse
    :type text: list
    :param idx: Index of the regex that the date matched to
    :return: Year if found. None if there is an error in the date format
    :rtype: int
    """
    date = re.split(r'\W+', text)
    if len(date) == 3:
        year = search_year(date, idx)
        if year:
            return year
    return None


def check_formatted_pattern(original_text, time):
    """
    Check if the date string corresponds to a formatted date. If it is the case, updates
    the time dictionary with a clean year

    :param original_text: Date to clean
    :type original_text: str
    :param time: Dictionary with date metadata
    :return: True is true date format has been found. False otherwise
    :rtype: bool
    """
    if settings.__DEBUG__:
        log("Checking for formatted date...")
    text = "-".join([elem.strip() for elem in original_text.split("-")])
    date1 = r"\b[\d]{2}.{1}[\d]{2}.{1}[\d]{4}\b"
    date2 = r"\b[\d]{4}.{1}[\d]{2}.{1}[\d]{2}\b"
    date3 = r"\b[\d]{1,4}.{1}[\d]{1,2}.{1}[\d]{1,4}\b"
    date4 = r"\b[\d]{1,2}\/[\d]{2}\b"
    dates = [date1, date2, date3]
    for idx, d in enumerate(dates):
        search = re.findall(d, text)
        if search:
            year_start = handle_date(search[0], idx)
            if year_start:
                time["date_start"] = year_start
                time["date_end"] = year_start
                if len(search) > 1:
                    year_end = handle_date(search[-1], idx)
                    if year_end:
                        time["date_end"] = year_end
                if settings.__DEBUG__:
                    log("Formatted date found")
                return True
    search_mmyy = re.findall(date4, text)
    if search_mmyy:
        found_dates = search_mmyy[0].split("/")
        if len(found_dates) == 2 and int(found_dates[0]) <= 12:
            if settings.__DEBUG__:
                log("Formatted date found")
            time["date_start"] = 1900 + int(found_dates[1])
            time["date_end"] = time["date_start"]
            return True
    return False

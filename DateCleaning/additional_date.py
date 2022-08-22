from . import settings
from .time_dict import create_time
from .corrections import check_error_elem
from .keywords import create_keywords, check_keywords
from .century_millennium import search_century_millennium, is_ordinal
from .numbers_processing import contain_numbers, extract_number_suffix
from .year import check_year
from .package_logging import log

"""
Module that checks if an additional date is to be found in the remaining string once a dirst date 
has been found
"""


def check_additional_year(text, time, keywords):
    """
    Parses the rest of the string. If it finds a numerical word, this functions looks if another year (or century)
    is present in the string

    :param text: Date string to parse
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    """
    if settings.__DEBUG__:
        log("Checking for additional year or century...")
    for idx, word in enumerate(text):
        if contain_numbers(word) or is_ordinal(word):
            keywords_second = create_keywords()
            time_second = create_time(time["date_original_lang"])
            #time_second["date_original"] = time["date_original"]
            check_year(text, time_second, keywords_second, additional_year=True)  # Check if another year is present
            if keywords_second["year"] is True and 0 < time_second["date_start"] < time["date_start"] and idx != 0:
                break  # If a smaller number is found and the number is not directly next to the year, we discard the
                # number (for example "1934 45" vs "1934 Dynasty 45")
            elif keywords_second["year"]:
                # To be sure that smaller second will be merged with higher firsts
                time["last"] = True
                time_second["first"] = True
                check_error_elem(time, time_second, keywords, keywords_second)
            if "century" in text:
                search_century_millennium(text, time_second, keywords_second)
            keywords["keywords_second"] = keywords_second
            keywords["time_second"] = time_second
            break


def check_additional_date(text, time, keywords):
    """
    Check if other dates are present in the rest of the string.
    Correct the string if there are two "century" present.

    :param text: Rest of the date string onc a date has been found
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    """
    if (keywords["century"] and "century" in text) or (keywords["millennium"] and "millennium" in text):
        if settings.__DEBUG__:
            log("Checking for additional century or millennium...")
        keywords_second = create_keywords()
        time_second = create_time(time["date_original_lang"])
        #time_second["date_original"] = time["date_original"]
        search_century_millennium(text, time_second, keywords_second)
        check_error_elem(time, time_second, keywords, keywords_second)
        keywords["keywords_second"] = keywords_second
        keywords["time_second"] = time_second
    elif keywords["year"] is True:
        check_additional_year(text, time, keywords)

from . import settings
from .text_preprocessing import preprocess_text, keywords_to_string
from .keywords import create_keywords, check_keywords, process_keywords
from .century_millennium import search_century_millennium
from .year import check_year, check_hidden_year
from .corrections import check_error_elem
from .time_dict import create_time
from .additional_date import check_additional_date
from .splitting import split_elements
from .package_logging import log

"""
Module that parses the date string and handle several elements if the date is a period
or if multiple dates are to be found in the string
"""


def compare_keywords(time, time_second, keywords, keywords_second):
    """
    Compare the keywords and checks if a keywords exist in one date but not in another.
    In this case, copies the keyword in the first date's dictionary

    :param time: Dictionary with the first date metadata
    :type time: dict
    :param time_second: Dictionary with the second date metadata
    :type time_second: dict
    :param keywords: Dictionary with found keywords of the first date
    :type keywords: dict
    :param keywords_second: Dictionary with found keywords of the second date
    :type keywords_second: dict
    """
    if time["date_start"] is None and time_second["date_start"] is not None:
        if keywords_second["split"]["active"] is None and not keywords_second["part"]["active"]:
            if keywords["split"]["active"] is not None and keywords["last_idx"]:
                process_keywords(time_second, keywords["split"], keywords["ordinal"], keywords["part"])
                time_second["date_english"] = time_second["date_english"] + keywords_to_string(keywords)
            if keywords["part"]["active"] and keywords["last_idx"]:
                process_keywords(time_second, keywords["split"], keywords["ordinal"], keywords["part"])
                time_second["date_english"] = time_second["date_english"] + keywords_to_string(keywords)


def handle_second_element(text, time, keywords):
    """
    Store the found dates in buffers and search a date in the second element

    :param text: Date to clean
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with possible date keywords
    :type keywords: dict | None
    """
    if settings.__DEBUG__:
        log("Handling second element:" + str(text))
    keywords_second = create_keywords()
    time_second = create_time(time["date_original_lang"])
    #time_second["date_original"] = time["date_original"]
    parse_element(text, time_second, keywords_second, several_elements=True)
    if time["date_start"] is None and time_second["date_start"] is None:
        if time["parentheses"] and parse_parentheses(time) is True:
            return None
    compare_keywords(time, time_second, keywords, keywords_second)
    check_error_elem(time, time_second, keywords, keywords_second)


def parse_parentheses(time):
    """
    Function that launches the parenthesis parsing. Calls the functions parse_string for recursively parse an element
    and returns True if successful, False otherwise

    :param time: Dictionary with time metadata
    :type time: dict
    :return: Boolean that indicates if a date (year of century/millennium) has been found in the parenthesis
    :rtype: bool
    """
    if settings.__DEBUG__:
        log(f"Checking date in parentheses: {time['parentheses']}")
    text = time["parentheses"]
    time["parentheses"] = None
    parse_string(text, time)
    if time["date_start"] is not None:
        return True
    return False


def parse_element(text, time, keywords, several_elements=False):
    """
    Parse the element by following these steps:
    1. Check if there is a year in the string
    2. If not, check if there is a century or millennium
    3. If not, Check if there is a hidden year
    4. If not, if there is only one element in the original string, parse the parentheses' content (if existing)
    5. If a date has been found, search for an additional date.

    :param text: Date to clean
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with possible date keywords
    :type keywords: dict
    :param several_elements: Boolean that checks if the function has been called in the realm of several parsed elements
    or several dates found in the same string, defaults to False
    :type several_elements: bool
    :return: The rest of the cleaned date string if a date has not been found. None otherwise
    :rtype: list | None
    """
    time["date_english"] = " ".join(text)
    clean_text = check_year(text, time, keywords)
    if keywords["year"] is False and clean_text:
        clean_text = search_century_millennium(text, time, keywords)
        if keywords["century"] is False and keywords["millennium"] is False and clean_text:
            clean_text = check_hidden_year(clean_text, time, keywords)
            if keywords["year"] is False:
                if several_elements is False and time["parentheses"] is not None:
                    parse_parentheses(time)
                    return
                elif several_elements is True:
                    clean_text = check_keywords(clean_text, time, keywords)
    if clean_text:
        check_additional_date(clean_text, time, keywords)


def parse_string(text, time):
    """
    Parse elements separately of there are two of them or sends
    the date string into the general parsing function

    :param text: Date to clean separated in elements if there are two
    :type text: str
    :param time: Dictionary with date metadata
    :type time: dict
    """
    keywords = create_keywords()
    splitted_text = split_elements(text, time)
    if len(splitted_text) > 1:
        # Join the last two parts (example 5th-6th centuries ryeo period,918-1392)
        if len(splitted_text) > 2 and "century" in text:
            splitted_text = splitted_text[:-2] + [" ".join(splitted_text[-2:])]
        if settings.__DEBUG__:
            log("Handling first element:" + splitted_text[-2])
        text_first = preprocess_text(splitted_text[-2], time)
        parse_element(text_first, time, keywords, several_elements=True)
        text_second = preprocess_text(splitted_text[-1], time)
        handle_second_element(text_second, time, keywords)
    elif len(splitted_text) == 1:
        text_first = preprocess_text(splitted_text[0], time)
        parse_element(text_first, time, keywords)

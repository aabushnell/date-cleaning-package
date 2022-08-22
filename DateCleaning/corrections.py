from . import settings
from .numbers_processing import retrieve_ordinal, find_highest_number
from .time_dict import copy_time
from .keywords import process_keywords
from .century_millennium import convert_century_millennium
from .text_preprocessing import keywords_to_string
from .package_logging import log

"""
Module that engages in data and string correction one all the data from the string have been retrieved
"""


def correct_year(time, time_second):
    """
    Corrects the year if the functions detects a truncation of a year (Ex: 1995-98) or error in year formatting
    (for ex, 600-500 or 500-100 BC)

    :param time: Dictionary with date metadata of the first element
    :type time: dict
    :param time_second: Dictionary with date metadata of the second element
    :type time_second: dict
    """
    if settings.__DEBUG__:
        log("Correct year in second element...")
    if time["date_start"] > 0 and time["date_end"] < 0:  # If second element is negative, first must be as well
        time["date_start"] *= -1
    if time["date_end"] < time["date_start"]:  # If second element is lower than first, engage correction
        time["date_flags"] = "FF-WO"
        if (find_highest_number(time["date_start"]) == find_highest_number(time["date_end"])) \
                or (time["date_end"] <= 0 and time["date_start"] <= 0):  # If of same magnitude,
            # replace their order
            buffer = time["date_start"]
            time["date_start"] = time_second["date_end"]
            time["date_end"] = buffer
        # If not, must be of format ("1995-98"), engage correction
        elif time["last"] and time_second["first"]:  # Additional check, first year must be end of string, second
            # element ust be at the beginning of the string
            highest = find_highest_number(time["date_start"])
            buff = time["date_start"]
            while time["date_end"] < time["date_start"] and highest > 0:
                time["date_end"] += buff // 10 ** highest * 10 ** highest
                buff %= 10 ** highest
                highest -= 1
            # If there is a bug (like 1912-1, which ends up as 1912-1911), keep only date_start
            if time["date_end"] < time["date_start"]:
                time["date_end"] = time["date_start"]
        # Something went wrong, correct the date to have the same year both start and end
        else:
            time["date_end"] = time["date_start"]


def check_error_year(time, time_second, keywords):
    """
    Keeps the latest year in the first element if there are several. Calls then the function to correct possible errors.
    Correct the string_english with the kept years

    :param time: Dictionary with date metadata of the first element
    :type time: dict
    :param time_second: Dictionary with date metadata of the second element
    :type time_second: dict
    :param keywords: Dictionary with keywords
    :type keywords: dict
    """
    if "keywords_second" in keywords.keys() and keywords["keywords_second"]["year"] and \
            keywords["time_second"]["date_start"] > 31:
        # Keep the last found year in the first element if there is one and is greater than 31
        copy_time(time, keywords["time_second"])
    time["date_end"] = time_second["date_end"]
    if time["date_end"] < time["date_start"]:  # If end is lower than start, engage correction (multiple cases)
        correct_year(time, time_second)
    if 0 <= time["date_start"] < 32 and time["date_end"] > 1000:
        time["date_start"] = time["date_end"]
    str_start = str(time["date_start"])
    str_end = str(time["date_end"])
    if time["date_start"] < 0:
        str_start = str_start[1:] + " BC"
        if time["date_end"] < 0:
            str_end = str_end[1:] + " BC"
        else:
            str_end = str_end + " AD"
    time["date_english"] = str_start + " - " + str_end


def check_error_century_millennium(time, time_second, keywords, keywords_second, period_word):
    """
    Corrects possible errors in century/millennium if the formatting is wrong (wrong order, BC/AD..)
    Corrects then the date_english entry

    :param time: Dictionary with date metadata of the first element
    :type time: dict
    :param time_second: Dictionary with date metadata of the second element
    :type time_second: dict
    :param keywords: Dictionary with keywords from the first element
    :type keywords: dict
    :param keywords_second: Dictionary with keywords from the second element
    :type keywords_second: dict
    :param period_word: Keyword of the period the function works with ("century" of "millennium")
    :type period_word: str
    """
    # If end date is negative, start date must be as well
    if keywords[period_word] > 0 and time_second["date_end"] <= 0:
        keywords[period_word] *= -1
        convert_century_millennium(period_word, time, keywords[period_word], turn=False)
        process_keywords(time, keywords["split"], keywords["ordinal"], keywords["part"])
    if not (time["date_start"] > 1000 and 0 < time_second["date_start"] < 32):  # For "19th century, 7 - 22"
        if time_second["date_start"] < time["date_start"]:
            # If date_start of second element is lower than date_start of the first element, invert their order
            time["date_start"] = time_second["date_start"]
            buffer = keywords
            keywords = keywords_second
            keywords_second = buffer
        else:
            time["date_end"] = time_second["date_end"]
    time["date_english"] = str(abs(keywords[period_word])) + retrieve_ordinal(keywords[period_word]) + " " + \
                           period_word + keywords_to_string(keywords)
    if keywords_second[period_word] is not False:
        time_second["date_english"] = str(abs(keywords_second[period_word])) + \
                                      retrieve_ordinal(keywords_second[period_word]) + " " + period_word + \
                                      keywords_to_string(keywords_second)
    if keywords[period_word] < 0:
        time["date_english"] = time["date_english"] + " bc"
        if keywords_second[period_word] < 0:
            time_second["date_english"] = time_second["date_english"] + " bc"
        else:
            time_second["date_english"] = time_second["date_english"] + " ad"


def merge_century_millennium(time, keywords, time_second, keywords_second):
    """
    Keeps the latest found date in every element if there is one. Calls then the function to correct possible errors

    :param time: Dictionary with date metadata of the first element
    :type time: dict
    :param keywords: Dictionary with keywords from the first element
    :type keywords: dict
    :param time_second: Dictionary with date metadata of the second element
    :type time_second: dict
    :param keywords_second: Dictionary with keywords from the second element
    :type keywords_second: dict
    """
    if keywords_second["century"] and "keywords_second" in keywords.keys() and keywords["keywords_second"]["century"]:
        # Keep second century of first element if it exists
        copy_time(time, keywords["time_second"])
        keywords = keywords["keywords_second"]
    # elif False and keywords["century"] and "keywords_second" in keywords_second.keys() and \
    #        keywords_second["keywords_second"]["century"]:
    #    # Keep second century of second element if it exists
    #    time_second = keywords_second["time_second"]
    #    keywords_second = keywords_second["keywords_second"]
    elif keywords["millennium"] and "keywords_second" in keywords.keys() and keywords["keywords_second"]["millennium"] \
            and keywords_second["millennium"]:  # Keep second millennium of first element if it exists
        copy_time(time, keywords["time_second"])
        keywords = keywords["keywords_second"]
    if keywords["century"] is not False:
        check_error_century_millennium(time, time_second, keywords, keywords_second, "century")
    elif keywords["millennium"] is not False:
        check_error_century_millennium(time, time_second, keywords, keywords_second, "millennium")
    elif keywords["year"] is True and keywords_second["century"] and \
            0 < time["date_start"] < keywords_second["century"]:  # For case "18 - 19th century"
        keywords["century"] = time["date_start"]
        convert_century_millennium("century", time, time["date_start"], turn=False)
        check_error_century_millennium(time, time_second, keywords, keywords_second, "century")
    time["date_english"] = time["date_english"] + " - " + time_second["date_english"]


def check_error_elem(time, time_second, keywords, keywords_second):
    """
    Entry of date corrections and element merging if there are multiple dates. Checks first the composition of each
    element (if there are year or century/millennium present) and calls the corresponding function to look and
    correct for errors

    :param time: Dictionary with the first date metadata
    :type time: dict
    :param time_second: Dictionary with the second date metadata
    :type time_second: dict
    :param keywords: Dictionary with found keywords of the first date
    :type keywords: dict
    :param keywords_second: Dictionary with found keywords of the second date
    :type keywords: dict
    """
    if settings.__DEBUG__:
        log("Correct possible errors...")
    if keywords["year"] is True and keywords_second["year"] is True:
        check_error_year(time, time_second, keywords)
        if "keywords_second" in keywords.keys() and keywords["keywords_second"]["century"]:
            if time["date_end"] - time["date_start"] > keywords["time_second"]["date_end"] \
                    - keywords["time_second"]["date_start"]:
                copy_time(time, keywords["time_second"])
                if settings.__DEBUG__:
                    log("Keep century because of more narrow period.")
        elif "keywords_second" in keywords_second.keys() and keywords_second["keywords_second"]["century"]:
            if time["date_end"] - time["date_start"] > keywords_second["time_second"]["date_end"] \
                    - keywords_second["time_second"]["date_start"]:
                copy_time(time, keywords_second["time_second"])
                if settings.__DEBUG__:
                    log("Keep century because of more narrow period.")
    elif time["date_start"] is not None and time_second["date_end"] is not None:
        if settings.__DEBUG__:
            log("Merge both elements...")
        merge_century_millennium(time, keywords, time_second, keywords_second)
    elif time["date_start"] is None:
        if settings.__DEBUG__:
            log("Keep only second element...")
        time["date_start"] = time_second["date_start"]
        time["date_end"] = time_second["date_end"]
        time["date_english"] = time_second["date_english"]
    if settings.__DEBUG__:
        log("Corrected period is now: " + str(time["date_start"]) + "-" + str(time["date_end"]))

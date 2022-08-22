from .numbers_processing import contain_numbers, extract_number
from .text_preprocessing import remove_punct, keywords_to_string
from .numbers_processing import retrieve_ordinal
from . import settings
from .keywords import process_keywords, extract_ordinal
from .package_logging import log

'''
This module treats everything related to centuries and millenniums. It finds and extracts century and millennium
information.
'''


def is_ordinal(word):
    """
    Check if the inputted word is a literal ordinal word or not. Returns the ordinal's number if it is the case or
    zero otherwise.

    :param word: Word to check
    :type word: str
    :return: cardinal number
    :rtype: int
    """
    ordinal = {"first": 1,
               "second": 2,
               "third": 3,
               "fourth": 4,
               "fifth": 5,
               "sixth": 6,
               "seventh": 7,
               "eighth": 8,
               "ninth": 9,
               "tenth": 10,
               "eleventh": 11,
               "twelfth": 12,
               "thirteenth": 13,
               "fourteenth": 14,
               "fifteenth": 15,
               "sixteenth": 16,
               "seventeenth": 17,
               "eighteenth": 18,
               "nineteenth": 19,
               "twentieth": 20}
    if word in ordinal:
        return ordinal[word]
    return 0


def check_ordinal(text, idx):
    """
    Checks if an ordinal word has been found and returns the corresponding integer

    :param text: Date to parse
    :type text: list
    :param idx: Index of the found keyword (century or millennium)
    :type idx: int
    :return: The corresponding integer and the found word
    :rtype: (int, str)
    """
    if idx > 0 and is_ordinal(text[idx - 1]):
        return is_ordinal(text[idx - 1]), text[idx - 1]
    for w in text:
        if is_ordinal(w):
            return is_ordinal(w), w
    return None, None


def convert_century_millennium(keyword, time, period, turn):
    """
    Converts the period number into a date (for ex, 19 to 1900 for century)

    :param keyword: Keyword to convert (century or millennium)
    :type keyword: str
    :param time: Time dictionary with date metadata
    :type time: dict
    :param period: Period number to convert
    :type period: int
    :param turn: Boolean that indicates if a "turn keyword" has been found in the string
    :type turn: bool
    """
    bc = False
    if period < 0:
        bc = True
    if keyword == "century":
        if turn:
            time["date_start"] = (period - 1 * (not bc)) * 100 - 10
            time["date_end"] = (period - 1 * (not bc)) * 100 + 10
        else:
            time["date_start"] = (period - 1 * (not bc)) * 100 + 1 * (not bc)
            time["date_end"] = (period + 1 * bc) * 100 - 1 * bc
    elif keyword == "millennium":
        if turn:
            time["date_start"] = (period - 1 * (not bc)) * 1000 - 10
            time["date_end"] = (period - 1 * (not bc)) * 1000 + 10
        else:
            time["date_start"] = (period - 1 * (not bc)) * 1000 + 1 * (not bc)
            time["date_end"] = (period + 1 * bc) * 1000 - 1 * bc


def check_keywords(text, period_ordinal, keywords):
    """
    Function that parses the string to look for keywords

    :param text: String to parse
    :type text: list
    :param period_ordinal: Keyword of the period ("century" or "millennium")
    :type period_ordinal: str
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :return: True if keywords have been found. False otherwise
    :rtype: bool
    """
    for idx, word in enumerate(text):
        if word == "active":
            continue
        if ((contain_numbers(word) or is_ordinal(word) > 4) and word != period_ordinal) or word in ["dynasty",
                                                                                                    "period"]:
            keywords["part"]["active"] = []
            keywords["split"]["active"] = None
            keywords["ordinal"]["active"] = None
            keywords["ordinal"]["word"] = None
        elif word == period_ordinal and ("century" in text[idx + 2:] or "millennium" in text[idx + 2:]):
            break
        elif word in keywords["part"].keys():
            keywords["part"]["active"].append(word)
        elif word in keywords["split"].keys():
            if word != "third" or (idx != 0 and text[idx - 1] in keywords["ordinal"].keys()):
                keywords["split"]["active"] = word
                extract_ordinal(text, idx, keywords["ordinal"])
                if keywords["ordinal"]["active"] is None:
                    keywords["split"]["active"] = None
                    return False
    if keywords["part"]["active"] or (keywords["split"]["active"] and keywords["ordinal"]["active"]):
        return True
    return False


def parse_date(text, keywords, idx, period_keyword):
    """
    Function that parse the string to look for the period number and possible keywords (for ex, "19th" or "nineteenth")

    :param text: String to parse
    :type text: list
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :param idx: Index of the found keywords ("century" or "millennium")
    :type idx: int
    :param period_keyword: Period keyword the function is working with ("century" or "millennium")
    :type period_keyword: str
    :return: Found period word if there is one (for ex, "19th" or "nineteenth"). None otherwise
    :rtype: str
    """
    period_ordinal = None  # Stores the period word if one is found
    period = None  # Stores the period in form of an integer
    if idx > 0 and contain_numbers(text[idx - 1]):
        period = extract_number(text[idx - 1])
        period_ordinal = text[idx - 1]
    else:
        for w in text[0:idx]:
            if contain_numbers(w):
                period_ordinal = w
                period = extract_number(w)
    if period is None:
        period, period_ordinal = check_ordinal(text, idx)
        if period is None:
            return None
    if not check_keywords(text, period_ordinal, keywords) and "turn" in text[0:idx]:
        keywords["turn"] = True
    if idx < len(text) - 1 and remove_punct(text[idx + 1], True) in ["bc", "bce"]:
        period *= -1
    keywords[period_keyword] = period
    return period_ordinal


def correct_english_string(time, period, keyword, keywords):
    """
    Functions that corrects the date_english entry of the time dictionary if a century/millennium has been found.
    Replaces directly the entry in the dictionary

    :param time: Time dictionary with date metadata
    :type time: dict
    :param period: Found period number
    :type period: int
    :param keyword: Period keyword the function is working with ("century" or "millennium")
    :type keyword: str
    :param keywords: Keywords dictionary
    :type keywords: dict
    """
    if period < 0:
        time["date_english"] = str(abs(period)) + retrieve_ordinal(period) + " " + keyword + " bc" + \
                               keywords_to_string(keywords)
    else:
        time["date_english"] = str(abs(period)) + retrieve_ordinal(period) + " " + keyword + \
                               keywords_to_string(keywords)
    if keywords["turn"]:
        time["date_english"] = time["date_english"] + " (turn)"


def check_century_millennium(text, time, period_keyword, keywords):
    """
    Checks if the word "century" is in the date and extract the century if it is the case

    :param text: Preprocessed date
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param period_keyword: Keyword to look for: "century" or "millennium"
    :type period_keyword: str
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :return: True if century has been found and extracted. False otherwise
    :rtype: bool
    """
    idx_period_word = 0
    while idx_period_word + 1 < len(text) and period_keyword in text[idx_period_word + 1:]:
        idx_period_word = text[idx_period_word + 1:].index(period_keyword) + idx_period_word + 1
        period_ordinal = parse_date(text, keywords, idx_period_word, period_keyword)
        if keywords[period_keyword] is not False:
            break
    if keywords[period_keyword] is False:
        return False
    convert_century_millennium(period_keyword, time, keywords[period_keyword], keywords["turn"])
    text.remove(period_ordinal)
    try:
        if keywords["part"]["active"]:
            for word in keywords["part"]["active"]:
                text.remove(word)
        elif keywords["split"]["active"]:
            text.remove(keywords["split"]["active"])
            text.remove(keywords["ordinal"]["word"])
    except ValueError:
        pass
    idx_period_word = text.index(period_keyword)
    if len(text) == 1 or ((idx_period_word == 0 or (not contain_numbers(text[idx_period_word - 1])
                                                    and not is_ordinal(text[idx_period_word - 1]))) and
                          (idx_period_word <= 1 or (not contain_numbers(text[idx_period_word - 2])
                                                    and not is_ordinal(text[idx_period_word - 2])))):
        if keywords[period_keyword] < 0 and idx_period_word + 1 < len(text):
            text.remove(text[idx_period_word + 1])
        text.remove(period_keyword)
    if keywords["turn"]:  # Ugly
        while text:
            text.pop()


def search_century_millennium(text, time, keywords):
    """
    Check if a "century" or a "millennium" keyword is present in the string. If it is the case, parse the string to
    retrieve the period's information. Also check for time keywords (like early or late) and process them if any has
    been found.

    :param text: Date string to parse:
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :return: Original date string if no "century" or "millennium" keyword is found or the cleaned string otherwise
    :rtype: list
    """
    if settings.__DEBUG__:
        log("Checking for keywords...")
    if "century" in text:
        check_century_millennium(text, time, "century", keywords)
    elif "millennium" in text:
        check_century_millennium(text, time, "millennium", keywords)
    else:
        return text
    process_keywords(time, keywords["split"], keywords["ordinal"], keywords["part"])
    if keywords["century"]:
        correct_english_string(time, keywords["century"], "century", keywords)
    elif keywords["millennium"]:
        correct_english_string(time, keywords["century"], "millennium", keywords)
    if settings.__DEBUG__:
        if keywords["part"]["active"]:
            log(f"Part keyword has been found:{keywords['part']['active']}")
        if keywords["split"]["active"] is not None:
            log(f"Splitting keywords has been found: {keywords['ordinal']['active']}, {keywords['split']['active']}")
        if keywords["century"] is not False:
            log(f"Century has been found:{keywords['century']}")
        if keywords["millennium"] is not False:
            log(f"Millennium has been found:{keywords['millennium']}")
    return text

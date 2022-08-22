import math

from .text_preprocessing import remove_punct, keywords_to_string
from .numbers_processing import contain_numbers, extract_number, extract_number_suffix, extract_number_prefix
from .numbers_processing import split_num_char
from .keywords import create_keywords, check_keywords
from . import settings
from .package_logging import log

def correct_decade(time, year_input, keywords_year):
    """
    Correct the date if the date is a decade

    :param time: Dictionary with date metadata
    :type time: dict
    :param year_input: Year that has been found
    :type year_input: int
    :param keywords_year: Dictionary with keywords for the year
    :type keywords_year: dict
    """
    keywords_year["decade"] = True
    year = math.floor(year_input / 10) * 10
    if 0 < year < 100:
        year += 1900
    if year < 0:
        if year_input % 10 == 0 and year_input % 100 == 0:
            time["date_start"] = year - 100
            time["date_end"] = year - 1
        else:
            time["date_start"] = year - 9
            time["date_end"] = year
    else:
        if year_input % 10 == 0 and year_input % 100 == 0:
            time["date_start"] = year + 1
            time["date_end"] = year + 100
        else:
            time["date_start"] = year
            time["date_end"] = year + 9


def check_splitted_suffix(text, idx, suffix):
    """
    Check if a suffix has been splitted (for ex:, ["B", "C"] for "BC")

    :param text: String to parse
    :type text: list
    :param idx: Index of the suffix to check
    :type idx: int
    :param suffix: Suffix to compare to (for ex, "BC" or "AD")
    :type suffix: str
    :return: Boolean that indicates if the suffix has been found. False if not found
    :rtype: bool
    """
    for letter in suffix:
        if idx == len(text) - 1 or remove_punct(text[idx + 1], True) != letter:
            return False
        idx += 1
    return True


def correct_year(time, keywords, text, year, idx, keywords_year, suffix, prefix):
    """
    Correct the date if a suffix has been found ("BC", "AH")

    :param time: Time dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary of found keywords
    :type keywords: dict
    :param text: String to parse
    :type text: list
    :param year: Year that has been found
    :type year: int
    :param idx: Index of the found year in the string
    :type idx: int
    :param keywords_year: Dictionary of the year keywords that have been found
    :type keywords_year: dict
    :param suffix: Found suffix of the year if present
    :type suffix: str
    :param prefix: Found prefix of the year if present
    :type prefix: str
    """
    if (idx < len(text) - 1 and remove_punct(text[idx + 1], True) in ["bc", "bce"]) or suffix in ["bc", "bce"] \
            or check_splitted_suffix(text, idx, "bc"):
        year = -year
        keywords_year["bc"] = True
    elif (idx > 0 and remove_punct(text[idx - 1], True) in ["bc", "bce"]) or prefix in ["bc", "bce"]:
        year = -year
        keywords_year["bc"] = True
    elif idx > 0 and text[idx - 1] == "-" or prefix == "-":
        year = -year
    elif (idx < len(text) - 1 and remove_punct(text[idx + 1], True) in ["ah", "hejira"]) or suffix == "ah":
        year = int(0.970229 * year + 621.5643)
        keywords_year["ah"] = True
    elif idx > 0 and remove_punct(text[idx - 1], True) == "ah" or prefix == "ah":
        year = int(0.970229 * year + 621.5643)
        keywords_year["ah"] = True
    time["date_start"] = year
    time["date_end"] = year
    if (idx > 0 and remove_punct(text[idx - 1], True) == "before") or prefix == "before":
        time["date_start"] = int(math.floor(year / 100.0)) * 100 + 1
        keywords_year["before"] = True
    elif (idx > 0 and remove_punct(text[idx - 1], True) == "after") or prefix == "after":
        time["date_end"] = int(math.ceil(year / 100.0)) * 100
        keywords_year["after"] = True
    keywords["year"] = True


def store_year(text, idx, time, word, keywords_year, keywords):
    """
    Store the year in the time dictionary and check beforehand if there is a decade or a bc

    :param text: Date to clean
    :type text: list
    :param idx: Index of the year in the data string
    :type idx: int
    :param time: Dictionary with date metadata
    :type time: dict
    :param word: Year that has been found in the string
    :type word: str
    :param keywords_year: Dictionary with keywords for the year
    :type keywords_year: dict
    :param keywords: Dictionary of found keywords
    :type keywords: dict
    """
    year = extract_number(word)
    suffix = extract_number_suffix(word)
    prefix = extract_number_prefix(word)
    if suffix == "s" or (idx < len(text) - 1 and remove_punct(text[idx + 1], True) == "s"):
        if idx < len(text) - 1 and remove_punct(text[idx + 1], True) in ["bc", "bce"]:
            year = -year
            keywords_year["bc"] = True
        correct_decade(time, year, keywords_year)
        keywords["year"] = True
    elif word.isnumeric() or suffix in ["bce", "bc", "ad", "ah"] or prefix is not None:
        correct_year(time, keywords, text, year, idx, keywords_year, suffix, prefix)


def clean_string_year(text, keywords_year, idx_year, year_word, time):
    """
    Removes the year and additional words relating to the date ("bc", "ad", "s").
    Returns a clean string.

    :param text: String to clean
    :type text: list
    :param keywords_year: Dictionary with keywords for the year
    :type keywords_year: dict
    :param idx_year: index of the year that has been detected
    :type idx_year: int
    :param year_word: Word of the year that has been found
    :type year_word: str
    :param time: Dictionary with time metadata
    :type time: dict
    :return: Cleaned string
    :rtype: list
    """
    text_tmp = text
    if "century" not in text:
        text_tmp = text[idx_year + 1:]
        if idx_year == 0:
            time["first"] = True
        if idx_year + 1 == len(text):
            time["last"] = True
    new_text = []
    for word in text_tmp:
        if remove_punct(word, True) == "ad":
            continue
        if word == year_word:
            continue
        elif keywords_year["bc"] is True and remove_punct(word, True) in ["bc", "bce"]:
            keywords_year["bc"] = False
            continue
        elif keywords_year["ah"] is True and remove_punct(word, True) == "ah":
            keywords_year["ah"] = False
            continue
        elif keywords_year["after"] is True and remove_punct(word, True) == "after":
            keywords_year["after"] = False
            continue
        elif keywords_year["before"] is True and remove_punct(word, True) == "before":
            keywords_year["before"] = False
            continue
        elif keywords_year["decade"] is True and word == "s":
            keywords_year["decade"] = False
            continue
        new_text.append(word)
    return new_text


def check_year_basic(text, keywords, time):
    """
    Checks if the string is a plain year

    :param text: String to parse
    :type text: list
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :param time: Time dictionary with date metadata
    :type time: dict
    :return: Boolean that indicates if the string a plain year. False otherwise
    :rtype: bool
    """
    date = " ".join(text)
    if date.isnumeric():
        year = int(date)
    elif contain_numbers(date) and extract_number_prefix(date) == "-" and extract_number_suffix(date) is None:
        year = -int(extract_number(date))
    else:
        return False
    keywords["year"] = True
    time["date_start"] = year
    time["date_end"] = year
    time["first"] = True
    time["last"] = True
    if year < 0:
        time["date_english"] = str(abs(year)) + " bc"
    if settings.__DEBUG__:
        log("Year " + "\"" + date + "\"" + " has been found")
    return True


def check_hidden_year(text, time, keywords):
    """
    Checks if a year is hidden in the string, i.e. "glued" to text

    :param text: String to parse
    :type text: list
    :param time: Time dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :return: Cleaned string without year if found
    :rtype: list
    """
    if settings.__DEBUG__:
        log("Check for hidden year...")
    text_splitted = split_num_char(" ".join(text))
    for word in text_splitted:
        if word.isnumeric() and int(word) > 21:
            text_splitted = check_year(text_splitted, time, keywords)
            if keywords["year"] is True:
                break
    if keywords["year"] is True:
        if settings.__DEBUG__:
            log("Hidden year has been found:" + time["date_start"])
        return text_splitted
    return text


def correct_time_date_english(time, keywords, keywords_period):
    """
    Corrects the date_english entry of the time dictionary

    :param time: Time dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with found keywords
    :type keywords: dict
    :param keywords_period: Dictionary of found keywords for the year
    :type keywords_period: dict
    """
    if keywords["decade"]:
        if time["date_start"] < 0:
            time["date_english"] = str(time["date_end"]) + "s" + keywords_to_string(keywords_period)
        else:
            time["date_english"] = str(time["date_start"]) + "s" + keywords_to_string(keywords_period)
    elif time["date_start"] == time["date_end"]:
        if time["date_start"] < 0:
            time["date_english"] = str(abs(time["date_start"])) + " bc"
        else:
            time["date_english"] = str(time["date_start"])


def check_if_year(text, word, idx, additional_year):
    """
    Carries out multiple checks to look if the number is truly a year or if it is part of something else
    (for ex, Dynasty, Day of month..."

    WARNING: WIKI

    :param text: String to parse
    :type text: list
    :param word: Found year
    :type word: str
    :param idx: Index of the found year in the string
    :type idx: int
    :param additional_year: Boolean indicating that the program is currently searching for an additional year. If set
    to False, the program looks for an initial year
    :type additional_year: bool
    :return: Boolean that indicates if the number is a year. False otherwise
    :rtype: bool
    """
    nbr = extract_number(word)
    # count alphabetical characters before
    c = 0
    if idx > 0:
        for index in range(0, idx):
            for i in text[index]:  # i holds each character in String s for every iteration of loop
                if i.isalpha():
                    c = c + 1
    # make decisions
    if idx > 0 and text[idx - 1] == "printed":
        return False
    elif nbr < 32 and idx > 0 and text[idx - 1] in ["january", "february", "march", "april", "may", "june", "july",
                                                    "august", "september", "october", "november", "december"]:
        return False
    elif nbr < 32 and len(text) > idx + 1 and text[idx + 1] in ["january", "february", "march", "april", "may", "june",
                                                                "july", "august", "september", "october", "november",
                                                                "december"]:
        return False
    if idx < len(text) - 1 and text[idx + 1] in ["st", "nd", "rd", "th"]:
        return False
    if 0 < nbr < 22 and "century" in text:
        return False
    elif idx == 0 or nbr > 31:
        return True
    elif nbr < 21 and text[idx - 1] == "dynasty":
        return False
    elif nbr < 5 and idx < len(text) - 1 and text[idx + 1] in ["half", "third", "quarter"]:
        return False
    elif nbr < 6 and not additional_year:
        return False
    elif nbr < 25 and c > 2:  # more than two alphabetical characters before the number
        return False
    return True


def check_year(text, time, keywords, additional_year=False):
    """
    Check if a year is present in the string.

    :param text: Date to clean
    :type text: list
    :param time: Dictionary with time metadata
    :type time: dict
    :param keywords: Dictionary with possible date keywords
    :type keywords: dict
    :param additional_year: Boolean indicating if the process is currently searching for an additional year or if it is
    the initial search
    :type additional_year: bool
    :return: String in list form without the year if a year has been found
    :rtype: list

    .. note:: Warning on the method: checks over 4 and additional check if number is below 31
    """
    if settings.__DEBUG__:
        log("Check for year...")
    keywords_year = {"bc": False,
                     "ah": False,
                     "decade": False,
                     "before": False,
                     "after": False}
    if check_year_basic(text, keywords, time):
        return None
    year = None
    year_tmp = False  # Used to check if another number is present when the first one below 31
    idx_year = None
    for idx, word in enumerate(text):
        if contain_numbers(word):
            if check_if_year(text, word, idx, additional_year):
                if year_tmp is False or extract_number(word) > 99:
                    year = word
                    idx_year = idx
                    store_year(text, idx, time, word, keywords_year, keywords)
                if keywords["year"] is True and 0 < time["date_start"] <= 99 and (idx != 0 or additional_year):
                    keywords["year"] = False
                    year_tmp = True
            if keywords["year"] is True:
                break
    if year_tmp is True:
        keywords["year"] = True
    if keywords["year"] is False or idx_year is None:
        return text
    correct_time_date_english(time, keywords_year, keywords)
    if time["date_start"] != time["date_end"]:
        keywords = create_keywords()
        check_keywords(text[:idx_year], time, keywords)
    new_text = clean_string_year(text, keywords_year, idx_year, year, time)
    if settings.__DEBUG__:
        log("Year " + "\"" + str(time["date_start"]) + "\"" + " has been found")
    return new_text

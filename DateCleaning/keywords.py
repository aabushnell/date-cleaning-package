import numpy as np
from .numbers_processing import contain_numbers, extract_number
from . import settings
from .package_logging import log


"""
Module that handles all potential keywords of splitting, parting
and centuries in the string
"""


def create_keywords():
    """
    Creates the keywords dictionary

    :return: The keywords dictionary
    :rtype: dict
    """
    ordinal = {"first": 0,
               "second": 1,
               "third": 2,
               "fourth": 3,
               "last": None,
               "latter": None,
               "active": None,
               "word": None}
    split = {"half": 3,
             "third": 4,
             "quarter": 5,
             "active": None}
    part = {"early": 0,
            "mid": 1,
            "middle": 1,
            "late": 2,
            "nbr_parts": 4,
            "active": []}
    keywords = {"ordinal": ordinal,
                "split": split,
                "part": part,
                "turn": False,
                "millennium": False,
                "century": False,
                "year": False,
                "last_idx": False}
    return keywords


def extract_ordinal(text, idx, ordinal):
    """
    Extract the ordinal parameter linked the splitting of the period
    (Ex: "second" for the splitting "quarter")

    :param text: Date to clean
    :type text: list
    :param idx: Index of the splitting word
    :type idx: int
    :param ordinal: Dictionary of ordinals with vocabulary and meaning
    :type ordinal: dict
    """
    if idx > 0:
        if text[idx - 1] in ordinal:
            ordinal["active"] = text[idx - 1]
            ordinal["word"] = text[idx - 1]
        elif contain_numbers(text[idx - 1]):
            ordinal["active"] = extract_number(text[idx - 1])
            ordinal["word"] = text[idx - 1]


def handle_split(time, nbr_parts, select_part, multiple=None):
    """
    Split the time period and store the selected period
    in the time dictionary

    :param time: Dictionary with date metadata
    :type time: dict
    :param nbr_parts: Number of parts the period has to be split into
    :type nbr_parts: int
    :param select_part: Part that will be selected
    :type select_part: int
    :param multiple: List that contains all the part keywords if there are several of them, defaults to None
    :type multiple: list
    """
    if select_part + 1 >= nbr_parts:
        return
    periods = np.floor(np.linspace(time["date_start"], time["date_end"], nbr_parts))
    if multiple:
        time["date_start"] = int(periods[min(multiple)])
        time["date_end"] = int(periods[max(multiple) + 1])
    else:
        time["date_start"] = int(periods[select_part])
        time["date_end"] = int(periods[select_part + 1])


def process_keywords(time, split, ordinal, part):
    """
    Takes the keywords dictionaries and process them in order
    to form a clean date

    :param time: Dictionary with date metadata
    :type time: dict
    :param split: Dictionary with splitting keywords
    :type split: dict
    :param ordinal: Dictionary with ordinal keywords
    :type ordinal: dict
    :param part: Dictionary with part keywords
    :param part: dict
    """
    if split["active"] and part["active"]:
        split["active"] = None
        part["active"] = None
        return
    if time["date_start"] is not None and time["date_end"] is not None:
        if split["active"] is not None:
            nbr_parts = split[split["active"]]
            ordi = ordinal["active"]
            if ordi == "last" or ordi == "latter":
                select_part = nbr_parts - 2
            elif type(ordi) is int:
                select_part = ordi - 1
            elif type(ordi) is str and ordi.isnumeric():
                select_part = int(ordi) - 1
            else:
                select_part = ordinal[ordi]
            handle_split(time, nbr_parts, select_part)
        elif part["active"]:
            multiple = []
            nbr_parts = part["nbr_parts"]
            if len(part["active"]) == 1:
                select_part = part[part["active"][0]]
            else:
                for word in part["active"]:
                    multiple.append(part[word])
                select_part = max(multiple)
            handle_split(time, nbr_parts, select_part, multiple)


def search_keywords(text, keywords):
    """
    Parse the string and look for keywords

    :param text: String to parse
    :type text: list
    :param keywords:  Dictionary with keywords
    :type keywords: dict
    :return: Cleaned text without found keywords
    :rtype: list
    """
    new_text = []
    for idx, word in enumerate(text):
        if word == "active":
            continue
        if word in keywords["split"].keys() and keywords["split"]["active"] is None:
            if word != "third" or (idx != 0 and text[idx - 1] in keywords["ordinal"].keys()):
                keywords["split"]["active"] = word
                extract_ordinal(text, idx, keywords["ordinal"])
                if keywords["ordinal"]["active"] is None:
                    keywords["split"]["active"] = None
                    return text
                if idx == len(text) - 1:
                    keywords["last_idx"] = True
            else:
                new_text.append(word)
        elif word in keywords["part"].keys():
            keywords["part"]["active"].append(word)
            if idx == len(text) - 1:
                keywords["last_idx"] = True
        else:
            new_text.append(word)
    if keywords["ordinal"]["active"] is not None:
        try:
            new_text.remove(str(keywords["ordinal"]["word"]))
        except ValueError:
            pass
    return new_text


def check_keywords(text, time, keywords):
    """
    Parse the string to look for keywords of splitting or centuries
    in the date string

    :param text: Date to clean
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param keywords: Dictionary with possible date keywords
    :type keywords: dict
    :return: A cleaned text string without keywords
    :rtype: list
    """
    text = search_keywords(text, keywords)
    process_keywords(time, keywords["split"], keywords["ordinal"], keywords["part"])
    if settings.__DEBUG__:
        if keywords["part"]["active"]:
            log(f"Part keyword has been found:{keywords['part']['active']}")
        if keywords["split"]["active"] is not None:
            log(f"Splitting keywords has been found:{keywords['ordinal']['active']}, {keywords['split']['active']}")
    return text

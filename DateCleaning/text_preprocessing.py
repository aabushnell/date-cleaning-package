import string

from .numbers_processing import retrieve_ordinal, check_convert_roman
from .numbers_processing import contain_numbers, extract_number_suffix, extract_number
from autocorrect import Speller
from spellchecker import SpellChecker
from . import settings
from .package_logging import log

"""
Module that prepossesses and cleans the date string
"""


def keywords_to_string(keywords):
    """
    Takes the keyword dictionary and transforms the existing keywords into a correctly formatted string

    :param keywords: Dictionary of keywords
    :type keywords: dict
    :return: Correctly formatted string
    :rtype: str
    """
    if keywords["part"]["active"]:
        return " (" + " ".join(keywords["part"]["active"]) + ")"
    elif keywords["split"]["active"] is not None:
        return " (" + str(keywords["ordinal"]["active"]) + " " + str(keywords["split"]["active"]) + ")"
    return ""


def remove_stopwords(text):
    """
    Removes stopwords from the string

    :param text: String to parse and clean
    :type text: list
    :return: Cleaned string
    :rtype: list
    """
    stops = ["and", "or", "of", "the", "to"]
    return [word for word in text if word not in stops]


def remove_ordinal_suffix(text):
    """
    Removes ordinal suffix from a string

    :param text: Date to clean
    :type text: list
    :return: Cleaned string without ordinal suffix
    :rtype: list
    """
    while "st" in text:
        text.remove("st")
    while "rd" in text:
        text.remove("rd")
    while "nd" in text:
        text.remove("nd")
    while "th" in text:
        text.remove("th")


def remove_punct(text, dot=False, replace=""):
    """
    Remove the punctuation from the string
    :param text: Words of the date to clean
    :type text: str
    :param dot: Boolean if dots must be taken into account of not
    :type dot: bool
    :param replace: Character by which punctuation must be replaced, defaults to ""
    :type replace: str
    :return: Word without punctuation
    :type: str
    """
    punct = string.punctuation.replace("-", "")
    if not dot:
        punct = punct.replace(".", "")
    return "".join([char if char not in punct else replace for char in text])


def add_millennium_century(time, text, prepro):
    """
    Add a missing century/millennium keyword if there is a ordinal number without it

    :param time: Time dictionary with date metadata
    :type time: dict
    :param text: Original inputted string
    :type text: list
    :param prepro: Preprocessed string
    :type prepro: list
    """
    if "millennium" in text:
        prepro.append("millennium")
    elif "century" in text:
        prepro.append("century")
    else:
        corrected_text = spell_corrector(time["date_english"].split(), time["date_original_lang"])
        if "millennium" in corrected_text:
            prepro.append("millennium")
        else:
            prepro.append("century")


def check_ordinal_without_century(prepro, time):
    """
    Checks if there is an ordinal word without the "century" keyword.

    :param prepro: Preprocessed string to parse
    :type prepro: list
    :param time: Time dictionary with date metadata
    :type time: dict
    :return: Preprocessed string with added "century" keyword if its missing
    :rtype: str
    """
    #text = time["date_original"].split()
    text = time["date_english"].split()
    if len(prepro) == 1:
        if contain_numbers(prepro[0]) and extract_number_suffix(prepro[0]) in ["st", "nd", "rd", "th"]:
            add_millennium_century(time, text, prepro)
    elif len(prepro) == 2:
        if prepro[0].isnumeric() and prepro[1] in ["st", "nd", "rd", "th"]:
            add_millennium_century(time, text, prepro)
    if len(prepro) > 1:
        if contain_numbers(prepro[-1]) and extract_number_suffix(prepro[-1]) in ["st", "nd", "rd", "th"]:
            add_millennium_century(time, text, prepro)
    if len(prepro) > 2:
        if prepro[-2].isnumeric() and prepro[-1] in ["st", "nd", "rd", "th"]:
            add_millennium_century(time, text, prepro)
    return prepro


def spell_corrector(text, lang):
    """
    Corrects possible spelling mistakes in the string
    thanks to the SpellChecker API

    :param text: Date to clean
    :type text: list
    :param lang: Language of the string
    :type lang: str
    :return: String corrected from spelling mistakes
    :rtype: list
    """
    corrected = text
    keywords = ["century", "centuries", "c.", "millennium"]
    inter = [w for w in text if w in keywords]
    if inter:  # if contains keyword
        return corrected
    elif len(text) == 1 and contain_numbers(text[0]):  # if it's one word and contains a number
        return corrected
    elif len(text) == 2 and contain_numbers(text[1]) and text[0] == "ca.":
        return corrected
    for word in text:
        if word.isnumeric() and int(word) > 30:  # if there is a number present which is bigger than 30
            return corrected
    if lang in ["en", "pl", "ru", "uk", "tr", "es", "cs"]:
        spell = Speller(lang)
        corrected = [spell(word) if not contain_numbers(word) and word != "mid" else word for word in text]
    elif lang in ["fr", "de", "pt"]:
        spell = SpellChecker(language=lang)
        corrected = [spell.correction(word) if not contain_numbers(word) and word != "mid" else word for word in text]
    return corrected


def small_corrections(text):
    """
    Implements small corrections: "century" for "cen.", "centuries", "c."

    :param text: String to parse
    :type text: list
    :return: Cleaned string
    :rtype: list
    """
    new_text = []
    if "centuries" in text or "cen." in text:
        text = ["century" if w in ["centuries", "cen."] else w for w in text]
    for idx, word in enumerate(text):
        if word in ["c.", "c"] and idx != 0 and contain_numbers(text[idx - 1]) and extract_number(text[idx - 1]) < 22:
            new_text.append("century")
        elif contain_numbers(word):
            nbr = extract_number(word)
            suffix = extract_number_suffix(word)
            if nbr and suffix and suffix == retrieve_ordinal(nbr) + "c":
                new_text.append(str(nbr))
                new_text.append("century")
            else:
                new_text.append(word)
        else:
            new_text.append(word)
    return new_text


def check_comma_nbr(preprocessed):
    """
    Checks if there is a number with a comma in it (for ex: "1,000") and correct the word if present

    :param preprocessed: String to parse
    :type preprocessed: list
    :return: Cleaned string
    :rtype: list
    """
    new_text = []
    for word in preprocessed:
        if "," in word and contain_numbers(word):
            splitted = word.split(",")
            if len(splitted) == 2 and splitted[0].isnumeric() and splitted[1].isnumeric() and len(splitted[1]) == 3:
                new_text.append("".join(splitted))
            else:
                new_text.append(word)
        else:
            new_text.append(word)
    return new_text


def preprocess_text(text, time, correct_spelling=True, chronontology=False):
    """
    Preprocess the text in order to have a cleaned string. Steps
    - Split numeric and characters from the string
    - Remove the punctuations except dots
    - Convert roman numbers
    - Convert into lowercases

    :param text: Date to clean
    :type text: str
    :param time: Dictionary with date metadata
    :type time: dict
    :param correct_spelling: Boolean that indicates if the spelling must be corrected or not, defaults to True
    :type correct_spelling: bool
    :return: Cleaned string
    :rtype: list
    """
    if settings.__DEBUG__:
        log("Preprocessing string \"" + text + "\"")
    preprocessed = text
    if time["date_original_lang"] is None or time["date_original_lang"] == "en":
        printable = string.printable
        preprocessed = "".join([w if w in printable else " " for w in text])
    preprocessed = preprocessed.lower().split(" ")
    preprocessed = check_comma_nbr(preprocessed)
    preprocessed = " ".join([remove_punct(w, replace=" ") for w in preprocessed])
    preprocessed = preprocessed.split(" ")
    preprocessed = [w for w in preprocessed if w != ""]
    if not chronontology:
        preprocessed = check_convert_roman(preprocessed)
    if correct_spelling:
        preprocessed = spell_corrector(preprocessed, time["date_original_lang"])
    preprocessed = small_corrections(preprocessed)
    preprocessed = remove_stopwords(preprocessed)
    preprocessed = check_ordinal_without_century(preprocessed, time)
    if preprocessed and preprocessed[-1][-1] == ".":  # Not sure why this is needed
        preprocessed[-1] = preprocessed[-1][:-1]
    if settings.__DEBUG__:
        log(f"Preprocessed string is {preprocessed}")
    return preprocessed

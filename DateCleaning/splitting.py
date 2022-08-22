from . import settings
from .numbers_processing import contain_numbers
from .text_preprocessing import remove_punct
from .package_logging import log

def check_minus(text):
    """
    Parses the string and checks if there dashes ("-") that corresponds to minuses of negative dates.
    Replaces minuses by asterisks "#"

    :param text: String to parse
    :type text: str
    :return: String with replaces minuses
    :rtype: list
    """
    text = text.split()
    if len(text) > 0 and len(text[0]) > 0 and text[0][0] == "-":  # if the string starts with "-"
        # Checks if the element after the dash is a number
        if len(text[0]) > 1 and text[0][1].isnumeric():
            text[0] = text[0].replace("-", "##", 1)
        elif len(text[0]) == 1 and len(text) > 1 and len(text[1]) > 0 and text[1][0].isnumeric():
            text[0] = text[0].replace("-", "##", 1)
    new_text = []
    for idx, word in enumerate(text):  # Checks for two following dashes
        new_word = word
        if "--" in word:
            idx_dash = word.index("--")
            if len(word) > idx_dash + 2 and word[idx_dash + 2].isnumeric():
                new_word = new_word.replace("--", "-##")
            elif len(word) == idx_dash + 2 and len(text) > idx + 1 and text[idx + 1][0].isnumeric():
                new_word = new_word.replace("--", "-##")
        elif word[0] == "-" and ((len(word) > 1 and word[1].isnumeric()) or
                                 (len(text) > idx + 1 and text[idx + 1][0].isnumeric)) and idx > 0 and \
                text[idx - 1][-1] == "-":
            new_word = new_word.replace("-", "##")
        new_text.append(new_word)
    return " ".join(new_text)


def convert_minus(text):
    """
    Converts asterisks "#" back to minuses "-" after the splitting has been done

    :param text: String to parse
    :type text: list
    :return: String with converted asterisks to minuses
    :rtype: list
    """
    new_text = []
    for word in text:
        if "##" in word:
            new_text.append(word.replace("##", "-"))
        else:
            new_text.append(word)
    return new_text


def check_parentheses(text, time):
    """
    Checks if parentheses are present and cuts the content out of the string
    to put it into the "parentheses" entry of the time dictionary if they are present.

    :param text: String to parse
    :type text: list
    :param time: Time dictionary with date metadata
    :type time: dict
    :return: String without parentheses
    :rtype: str
    """
    while text and ((text[0] == "(" and text[-1] == ")") or (text[0] == "[" and text[-1] == "]")):
        text = text[1:-1]
    while "(" in text and ")" in text and text.index("(") < text.index(")"):
        idx1 = text.index("(")
        idx2 = text.index(")")
        if not contain_numbers(text[idx1:idx2]):
            text = text.replace("(", " ", 1)
            text = text.replace(")", " ", 1)
        else:
            text = text.split("(", 1)
            second = text[1].split(")", 1)
            time["parentheses"] = second[0]
            text = text[0] + second[1]
    while "[" in text and "]" in text and text.index("[") < text.index("]"):
        idx1 = text.index("[")
        idx2 = text.index("]")
        if not contain_numbers(text[idx1:idx2]):
            text = text.replace("[", " ", 1)
            text = text.replace("]", " ", 1)
        else:
            text = text.split("[")
            second = text[1].split("]")
            time["parentheses"] = second[0]
            text = text[0] + second[1]
    return text


def split_elements(text, time):
    """
    Split the string into two elements if there is a character "-".
    Additionally checks for hidden "century" or "millennium", minuses and parentheses.

    :param text: Date to clean
    :type text: str
    :param time: Time dictionary with date metadata
    :type time: dict
    :return: String converted into a list with multiple elements if it is the case
    :rtype: list
    """
    if settings.__DEBUG__:
        log("Check for splitting...")
    text = text.replace("–", "-")
    text = text.replace("‒", "-")
    text = text.replace("—", "-")
    test = text.split("century")
    text = " century ".join(test)
    text = text.split("millennium")
    text = " millennium ".join(text)
    text = check_minus(text)
    text = check_parentheses(text, time)
    elements = text.split("-")
    while '' in elements:
        elements.remove("")
    while ' ' in elements:
        elements.remove(" ")
    try:
        new_text = [elements[0]]
    except IndexError:
        return []
    if len(elements) >= 2:
        for elem in elements[1:]:
            first_word = elem.split()[0].lower()
            last = new_text[-1]
            if remove_punct(first_word) in ["st", "nd", "rd", "th", "century"] or \
                    remove_punct(last) in ["early", "mid", "late"]:
                last_elem = new_text.pop()
                new_text.append(" ".join([last_elem, elem]))
            else:
                new_text.append(elem)
    new_text = convert_minus(new_text)
    if settings.__DEBUG__ and len(new_text) > 1:
        log(f"Text splitted into: {new_text}")
    return new_text

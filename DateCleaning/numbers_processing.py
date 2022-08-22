import re

"""
Module containing generic functions relating to number parsing, extraction and converting
"""


def contain_numbers(text):
    """
    Check if the string contain numbers

    :param text: Word to check
    :type text: str
    :return: True if the word contains numbers. False otherwise.
    :rtype: bool
    """
    result = any(char.isnumeric() for char in text)
    return result


def find_highest_number(nbr):
    """
    Finds the highest order of a number (thousands, hundreds, tenths)

    :param nbr: Number to check
    :type nbr: int
    :return: Highest order
    :rtype: int
    """
    if nbr < 0:
        nbr *= -1
    highest = -1
    while nbr >= 1:
        nbr /= 10
        highest += 1
    return highest


def retrieve_ordinal(n):
    """
    Return the correct ordinal suffix to a number

    :param n: Number to check
    :type n: int
    :return: String with the ordinal suffix
    :rtype: str
    """
    if n < 0:
        n *= -1
    if 3 < n < 21:
        return "th"
    last = n % 10
    if last == 1:
        return "st"
    elif last == 2:
        return "nd"
    elif last == 3:
        return "rd"
    return "th"


def extract_number(word):
    """
    Extract the number out of a string

    :param word: Word to extract from
    :type word: str
    :return: A number if there is one. None if not.
    :rtype: int | None
    """
    elems = split_num_char(word)
    for elem in elems:
        if elem.isnumeric():
            return int(elem)
    return None


def extract_number_prefix(word):
    """
    Extract the prefix out of a string

    :param word: Word to extract from
    :type word: str
    :return: A number if there is one. None if not.
    :rtype: str | None
    """
    elems = split_num_char(word)
    for idx, elem in enumerate(elems):
        if elem.isnumeric() and idx > 0:
            return elems[idx - 1]
    return None


def extract_number_suffix(word):
    """
    Extract the suffix out of a string

    :param word: Word to extract from
    :type word: str
    :return: A number if there is one. None if not.
    :rtype: str | None
    """
    elems = split_num_char(word)
    for idx, elem in enumerate(elems):
        if elem.isnumeric() and idx < len(elems) - 1:
            return elems[idx + 1]
    return None


def split_num_char(text):
    """
    Use regex to split numbers and characters in a string

    :param text: Date to clean
    :type text: str
    :return: List of words with characters and numbers separated
    :rtype: list
    """
    elements = re.findall(r"[^ \d]+|\d+", text)
    return elements


def check_convert_roman(text):
    """
    Check if roman numbers are present and convert them if it is the case.
    Also adds a "century" word if the roman number stands alone

    :param text: Date to clean
    :type text: list
    :return: New text with roman numbers converted
    :rtype: list
    """
    new_text = []
    valid_roman_numerals = ["X", "V", "I", "x", "v", "i"]
    all_roman = False
    if all(all(letter in valid_roman_numerals for letter in word.lower()) or word in ["bc", "ad"] for word in text):
        all_roman = True
    for word in text:
        if all(letter in valid_roman_numerals for letter in word):  # and word != "MID":
            nums = {'X': 10, 'V': 5, 'I': 1, 'x': 10, 'v': 5, 'i': 1}
            sum = 0
            for i in range(len(word)):
                value = nums[word[i]]
                if i + 1 < len(word) and nums[word[i + 1]] > value:
                    sum -= value
                else:
                    sum += value
            if all_roman:
                new_text.append(str(sum) + retrieve_ordinal(sum))
                new_text.append("century")
            else:
                new_text.append(str(sum))
        else:
            new_text.append(word)
    return new_text

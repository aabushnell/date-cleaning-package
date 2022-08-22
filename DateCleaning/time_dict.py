"""
Module with generic function handling the time dictionary
"""

def fill_missing_columns(time):
    """
    For manual dates these columns are not filled, so we fill them before returning the
    time dictionary
    :param time: dictionary
    """
    columns = ["date_debug", "date_debug_spatial", "date_match_id", "date_match_label",
                "date_match_score", "date_match_spatial"]
    for column in columns:
        if column not in time:
            time[column] = ""


def change_time(time, time_second):
    """
    Copies the content of one dictionary into the other, both ways

    :param time: First dictionary to copy into second
    :type time: dict
    :param time_second: Second dictionary to copy into first one
    :type time_second: dict
    """
    date_start = time_second["date_start"]
    date_end = time_second["date_end"]
    date_english = time_second["date_english"]
    #date_original = time_second["date_original"]
    date_original_lang = time_second["date_original_lang"]
    date_match_label = time_second["date_match_label"]
    date_match_score = time_second["date_match_score"]

    time_second["date_start"] = time["date_start"]
    time_second["date_end"] = time["date_end"]
    time_second["date_english"] = time["date_english"]
    #time_second["date_original"] = time["date_original"]
    time_second["date_original_lang"] = time["date_original_lang"]
    time_second["date_match_label"] = time["date_match_label"]
    time_second["date_match_score"] = time["date_match_score"]

    time["date_start"] = date_start
    time["date_end"] = date_end
    time["date_english"] = date_english
    #time["date_original"] = date_original
    time["date_original_lang"] = date_original_lang
    time["date_match_label"] = date_match_label
    time["date_match_score"] = date_match_score


def copy_time(time, time_second):
    """
    Copies the content of the second dictionary into the first one

    :param time: Dictionary to fill with the content of the second
    :type time: dict
    :param time_second: Dictionary to copy into the first one
    :param time_second: dict
    """
    time["date_start"] = time_second["date_start"]
    time["date_end"] = time_second["date_end"]
    time["date_english"] = time_second["date_english"]
    #time["date_original"] = time_second["date_original"]
    time["date_original_lang"] = time_second["date_original_lang"]
    time["date_match_label"] = time_second["date_match_label"]
    time["date_match_score"] = time_second["date_match_score"]


def create_time(language):
    """
    Creates a time dictionary

    :param language: Language of the input
    :type language: str
    :return: Time dictionary
    :rtype: dict
    """
    time = {"date_start": None,
            "date_end": None,
            "date_english": None,
            #"date_original": None,
            "date_original_lang": language,
            "date_flags": "NF",
            "first": False,
            "last": False,
            "date_match_label": None,
            "date_match_score": None}
    return time


def fill_flags(time,date):
    # Do necessary corrections
    if time["date_original_lang"] is None:
        time["date_original_lang"] = "en"
    if time["date_start"] is None:
        time["date_start"] = ""
        time["date_end"] = ""
    # time["date_original"] = str(date)

    # Check the flagging
    """if validated_dates \
            and str(date) in validated_dates and validated_dates[str(date)]["date_start"] == time["date_start"] \
            and validated_dates[str(date)]["date_end"] == time["date_end"]:
        time["date_flags"] = "NF-CK" 
    """
    if time["date_start"] == None or time["date_start"] == "" \
            or time["date_end"] == None or time["date_end"] == "":
        time["date_flags"] = "FF-NULL"
    elif time["date_start"] < - 30000 or time["date_end"] > 2020:
        time["date_flags"] = "FF-OB"
    elif len(" ".join(str(date).split("-")).split(" ")) >= 10:
        time["date_flags"] = "FF-LS"
    if time["date_flags"] == "NF":
        time["date_flags"] = "NF-NU"

    # Delete the useless variables
    del time["parentheses"]
    del time["first"]
    del time["last"]
    fill_missing_columns(time)


def check_country_code(country_code):
    # If there are country codes, pick the first one that is a two-letter code
    if country_code is None or not isinstance(country_code, str):
        country_code = ""
    if country_code:
        # Use the first country code of the list
        country_code = country_code.split(",")
        for loc in country_code:
            if len(loc) == 2:
                country_code = loc
                break
        if len(country_code) != 2:
            # time["date_flags"] = "FF-CC"
            country_code = ""
    return country_code

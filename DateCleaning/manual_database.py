from .keywords import create_keywords, check_keywords, process_keywords
from .text_preprocessing import preprocess_text
from .text_preprocessing import keywords_to_string
from .time_dict import copy_time
from . import settings
from .package_logging import log

def parse_manual(cleaned_date, time, manual_dates, country_code):
    """
    Check if the date string is present in the manual_dates dictionary and updates the time dictionary if it is the case

    :param cleaned_date: Date string cleaned from time keywords
    :type cleaned_date: str
    :param time: Dictionary with date metadata
    :type time: dict
    :param manual_dates: Dictionary linking manually inputted date with time periods
    :type manual_dates: dict
    :param country_code: Country code of the country in which the object is located. Helps to find specific time periods
    if the program has to query the Chronontology API.
    :type country_code: str
    :return: Boolean indicating if the date string has been found in the original date string or not
    :rtype: bool
    """

    # cleaned_date_str = " ".join([word for word in cleaned_date if word not in ["dynasty", "period"]])
    if manual_dates is not None and len(manual_dates) > 0:
        # if there is one manual mapping for the date_original, we use it, otherwise, we search for cleaned_date
        if time["date_original"] != "":
            manual_df = manual_dates[manual_dates["input_string"].str.lower() == time["date_original"]]
            if len(manual_df) > 0:
                manual_df = manual_dates[manual_dates["is_date_original"] == 1]

        else:
            manual_df = manual_dates[manual_dates["input_string"].str.lower() == cleaned_date.lower()]
            if len(manual_df) > 0:
                manual_df = manual_df[manual_df["is_date_original"] == 0]

        if country_code != "" and len(manual_df) > 0:
            manual_df = manual_df[manual_df["countries"].str.contains(country_code, na=False)]
        if len(manual_df) > 0:
            if settings.__DEBUG__:
                log(f"Manual date found for input string: {cleaned_date}, {country_code}")
            found_time = manual_df.iloc[0]
            time["date_start"] = found_time["date_start"]
            time["date_end"] = found_time["date_end"]
            time["date_flags"] = "NF-MN"
            return True
    return False


def check_manual(text, time, manual_dates, country_code):
    """
    Parse the date string to check if it is present in the database of manually inputted dates. Before checking,
    preprocess the string and check if the for the presence of time keywords

    :param date_original:
    :param text: Date string to parse
    :type text: str
    :param time: Dictionary with date metadata
    :type time: dict
    :param manual_dates: Dictionary linking manually inputted date with time periods
    :type manual_dates: dict
    :param country_code: Country code of the country in which the object is located. Helps to find specific time periods
    if the program has to query the Chronontology API.
    :type country_code: str
    :return: Boolean indicating if the date string has been found in the original date string or not
    :rtype: bool
    """
    keywords_original = create_keywords()
    original = preprocess_text(text, time, correct_spelling=False)
    #original = check_keywords(original, time, keywords_original)
    #original = [word for word in original if word not in ["early", "mid", "late", "possibly"]]
    if manual_dates is not None and len(manual_dates) > 0 \
            and parse_manual(text, time, manual_dates, country_code) is True:
        process_keywords(time, keywords_original["split"], keywords_original["ordinal"], keywords_original["part"])
        time["date_english"] += keywords_to_string(keywords_original)
        if settings.__DEBUG__:
            log("A manual date has been found for the string:" + text)
        return True
    elif settings.__DEBUG__:
        log("No manual date has been found.")
    return False

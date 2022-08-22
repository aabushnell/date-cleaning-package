from . import settings
from .time_dict import copy_time
from .package_logging import log

def check_validated_dates(cleaned_date, time, validated_dates, country_code):
    """
    Check if the date string is present in the validated_dates dataframe
    :param cleaned_date: Cleaned date string
    :type cleaned_date: str
    :param time: Time dictionary to save final result
    :type time: dict
    :param validated_dates: DataFrame with tl_date_checked
    :type validated_dates: DataFrame
    :param country_code: Two letter country code
    :type country_code: str
    :return: True if there's a checked date for that string, else False
    :rtype: bool
    """
    if validated_dates is not None and len(validated_dates) > 0:
        validated_df = validated_dates[validated_dates["date_english"].str.contains(cleaned_date)]
        if len(validated_df) > 0 and validated_df["location_mapped_country"].iloc[0]:
            validated_df = validated_df[validated_df["location_mapped_country"].str.contains(country_code, na=False)]
            if validated_df.empty:
                # found string but for a different country
                return False
        if len(validated_df) > 0:
            if settings.__DEBUG__:
                log(f"Validated date found for input string: {cleaned_date}, {country_code}")
            found_time = validated_df.iloc[0]
            if found_time["correct"] == 1:
                time["date_debug"] = found_time["date_debug"]
                time["date_debug_spatial"] = found_time["date_debug_spatial"]
                time["date_start"] = found_time["date_start"]
                time["date_end"] = found_time["date_end"]
                time["date_match_id"] = found_time["date_match_id"]
                time["date_match_label"] = found_time["date_match_label"]
                time["date_match_score"] = found_time["date_match_score"]
                time["date_match_spatial"] = found_time["date_match_spatial"]
                time["date_flags"] = "NF-CK"
            else:
                time["dates_flag"] = "FF-NULL"
            return True
    return False

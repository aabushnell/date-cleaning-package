from . import settings
from .package_logging import log

def check_synonym(date, date_original, synonyms, country_code):
    """
    Return synonym if a synonym/country is found
    :param date: input string
    :type date: str
    :param synonyms: data from table tl_synonyms
    :type synonyms: DataFrame
    :return: synonym if found, if not original date
    :rtype: str | None
    """
    if synonyms is not None and len(synonyms) > 0:

        if date_original != "":
            syn_df = synonyms[synonyms["original_string"].str.lower() == date_original.lower()]
            if len(syn_df) > 0:
                syn_df = syn_df[syn_df["is_date_original"] == 1]

        else:
            syn_df = synonyms[synonyms["original_string"].str.lower() == date.lower()]
            if len(syn_df) > 0:
                syn_df = syn_df[syn_df["is_date_original"] == 0]

        #if country_code != "":
        #    syn_df = syn_df[syn_df["country_code"].str.contains(country_code, na=False)]
        if len(syn_df) > 0:
            if settings.__DEBUG__:
                synonym = syn_df["synonym"]
                log(f"Synonym {synonyms['original_string'].str.lower()} found for input string: {date}, {country_code}")
            return syn_df.iloc[0]["synonym"]#, True

    log(f"No synonym found for: {date}, {country_code}")
    return date

'''
    if manual_dates is not None and len(manual_dates) > 0:
        # if there is one manual mapping for the date_original, we use it, otherwise, we search for cleaned_date
        if time["date_original"] != "":
            manual_df = manual_dates[manual_dates["input_string"].str.lower() == time["date_original"]]
            if len(manual_df) > 0:
                manual_df = manual_dates[manual_dates["is_date_original"] == 1]

        else:
            manual_df = manual_dates[manual_dates["input_string"].str.lower() == cleaned_date.lower()]
            if len(manual_df) > 0:
                manual_df = manual_dates[manual_dates["is_date_original"] == 0]
'''
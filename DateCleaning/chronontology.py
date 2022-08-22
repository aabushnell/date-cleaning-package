from datetime import datetime
import requests
import os
import json
from fuzzywuzzy import fuzz
import pandas as pd
from difflib import SequenceMatcher
import logging
from .keywords import create_keywords, check_keywords, process_keywords
from .text_preprocessing import preprocess_text
from .database import query_cache, to_sql, get_perido_data
from . import settings
from .text_preprocessing import keywords_to_string
import numpy as np
from .package_logging import log

'''
This module searches for a chronontology entry in the API and in the local cache of the API
'''


def remove_dates(name_period):
    """
    Removes possibles dates that you can find at the end of the choronontology request
    Example: "French Revolution, 1789-1793"

    :param name_period: chronotology period
    :type name_period: str
    :return: Cleaned string
    :rtype: str
    """
    if "," in name_period:
        name_period = name_period[:name_period.index(",")]
        name_period = name_period.strip()
    return name_period


def correct_date(date):
    """
    Correct possible erroneous date outputs of the API's request

    :param date: Date output of the API's request
    :type date: str | dict | int
    :return: Correct date if possible
    :rtype: int | None
    """
    if date is None:
        return None
    try:
        date = int(date)
        return date
    except (ValueError, TypeError) as e:
        pass
    if type(date) == dict:
        try:
            start = int(date["notBefore"])
            end = int(date["notAfter"])
            return int(start) + (int(end) - int(start)) / 2
        except (KeyError, ValueError) as e:
            pass
    if type(date) == str:
        if date == "not specified":
            return None
        if date == "present":
            return 2020
    log(f"New entry in DAINST API: {date}")
    return None


def is_close_country(close_countries_list, query_countries_list):
    """
    This function returns a boolean if at least of country codes of the query's results is in the list of close or
    border countries list of the query's original country.
    :param close_countries_list: List that contains the close or border countries list of the query's original country.
    :type close_countries_list: list
    :param query_countries_list: List separated by commas of the country codes of the query's results.
    :type query_countries_list: str
    :return: Boolean that indicates if at least of country codes of the query's results is in the list of close or
    border countries list of the query's original country.
    :rtype: bool
    """
    close_countries_list = np.array(close_countries_list)
    query_countries_list = query_countries_list.split(",")
    query_countries_list = np.array(query_countries_list)
    is_close_country_result = np.intersect1d(close_countries_list, query_countries_list)
    is_close_country_result = is_close_country_result.size != 0
    return is_close_country_result


def erase_keywords_both(string1, string2, words_to_erase):
    """
        some keywords are relevant in the string but is better to
        compute the match score without them. Like "early bronze age" and
        "early iron age" can have a high score, so we remove early and age from
        both strings. The strings are remove ONLY if they are present in both
        strings
        :return: string1, string2 without the words_to_erase
    """
    list_string_1 = string1.split()
    list_string_2 = string2.split()
    for word in words_to_erase:
        if word in list_string_1 and word in list_string_2:
            list_string_1.remove(word)
            list_string_2.remove(word)
    return " ".join(list_string_1), " ".join(list_string_2)


def string_similarity(date_debug, date_match_label):
    """
    compute the string similarity, result from 0 to 1
    :param date_debug:
    :param date_match_label:
    :return:
    """
    words_to_remove_both = ["late", "early", "middle", "republic", "dynastic",
                            "reign", "beginning", "monarchy", "emperor",
                            "proto", "pre", "age", "ages", "intermediate","revolution"]
    words_to_remove_any = ["dynasty", "year"] #kingdom
    str1, str2 = erase_keywords_both(date_match_label, date_debug, words_to_remove_both)
    str1 = erase_keywords(str1, words_to_remove_any)
    str2 = erase_keywords(str2, words_to_remove_any)
    return SequenceMatcher(None, str1, str2).ratio()

def check_publication_year(best_matches, engine):
    """
    Implements the rule of selecting the start and end date based on publication year in case there is more than
    1 perfect match.
    :param best_matches: ordered matches
    :return:
    """
    best_matches.sort_values(by=['score', 'rank'], ascending=[False, True], inplace=True)
    top_score = best_matches.iloc[0]["score"]
    best_matches = best_matches[best_matches["score"] == top_score]
    if (len(best_matches) == 1):
        log(f"Date found in chronontology:{best_matches['date_match_label']}, Similarity Score: {best_matches['score']}")
        return best_matches.iloc[0].to_dict()
    log(f"More than one perfect match found. Using publication year rule:")
    periodo_ids = {s.replace("periodo:", "") for s in best_matches["date_match_id"].to_list()}
    df_periodo = get_perido_data(periodo_ids, engine)

    if len(df_periodo[pd.to_numeric(df_periodo["publication_year"]) >= 2000].count()) > 1:
        df_periodo = df_periodo[pd.to_numeric(df_periodo["publication_year"]) >= 2000]

    min = df_periodo["date_start"].min()
    max = df_periodo["date_end"].max()
    #best = pd.DataFrame(columns=["date_start", "date_end", "date_match_label", "score",
    #                             "date_match_spatial"])
    best = {}

    periodo_min = df_periodo[df_periodo["date_start"] == min].iloc[0]
    periodo_max = df_periodo[df_periodo["date_end"] == max].iloc[0]
    best["date_start"] = periodo_min["date_start"]
    best["date_end"] = periodo_min["date_end"]
    best["date_match_label"] = best_matches.iloc[0]["date_match_label"]
    best["score"] = top_score

    if len(df_periodo) == 1:
        best["date_match_id"] = f"periodo:{periodo_min['periodo_id']}"
        best["date_match_spatial"] = periodo_min["country_list"]
    else:
        best["date_match_id"] = f"periodo:{periodo_min['periodo_id']},{periodo_max['periodo_id']}"
        list_countries = []
        if periodo_min["country_list"] != "":
            list_countries.append(periodo_min["country_list"])
        if periodo_max["country_list"] != "":
            list_countries.append(periodo_max["country_list"])

        if len(list_countries) > 0:
            countries = set(list_countries)
            best["date_match_spatial"] = ','.join(str(e) for e in countries)
        else:
            best["date_match_spatial"] = ""
    return best


def search_best_match(time, cleaned_data, country_info, engine, confidence=0.7):
    """
    Loops through the API requests' results and compare the date to the best possible solution
    :param time: Time dictionary with date metadata
    :type time: dict
    :param cleaned_data: Cleaned results of the API request
    :type cleaned_data: pandas.core.DataFrame
    :param country_info: Dict with country information of the date string, None if it doesn't apply.
    :type country_info: dict
    :param db: Database engine
    :type db: SQLAlchemy engine
    :param confidence: Lower bound that decides if a match should be picked or not.
    :type confidence: float
    :return: Boolean based on `call_chrono`. If everything is ok and it found a result, True, else, False.
    :rtype: bool
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    close_countries = pd.read_pickle(os.path.join(base_dir, "border_countries.pkl"))

    best = {"score": 0, "date_start": None, "date_end": None, "date_match_label": None}
    cleaned_data['date_match_label'] = cleaned_data['date_match_label'].str.lower().apply(remove_dates)
    # String matching
    # SM Method
    cleaned_data['score'] = cleaned_data['date_match_label'].apply(lambda x: string_similarity(time["date_debug"], x))

    if country_info is not None:
        close_countries_df = close_countries.query(f"ISO_A2 == '{country_info['country_code'].upper()}'")
        if close_countries_df.empty:
            country_info = None
            log(f"""The provided country code is not recognized.
                           'Please use the ISO 3166 2-letter country codes.""")
        else:
            # join own country with its close countries
            close_countries_list = ','.join(close_countries_df.values[0]).split(",")
            cleaned_data['is_close_country'] = cleaned_data['date_match_spatial'].apply(lambda x:
                                                                                        is_close_country(
                                                                                            close_countries_list,
                                                                                            x))
            cleaned_data = cleaned_data.query("is_close_country == True")
            if cleaned_data.empty:
                return False

    # for method in ['ratio_SM', 'ratio_FW_sort']:
    best_matches = cleaned_data[cleaned_data["score"] >= confidence]
    if best_matches.empty:
        return False
    winner = check_publication_year(best_matches, engine)

    best["date_start"] = correct_date(winner["date_start"])
    best["date_end"] = correct_date(winner["date_end"])
    best["date_match_label"] = winner["date_match_label"]
    best["score"] = winner["score"]
    best["date_match_id"] = winner["date_match_id"]
    best["date_match_spatial"] = winner["date_match_spatial"]
    log(f"Date found in chronontology:{winner['date_match_label']}, Similarity Score: {winner['score']}")

    if country_info:
        fill_time(time, best, country_info['country_code'], winner['date_match_spatial'])
    else:
        fill_time(time, best, "no country info", winner['date_match_spatial'])
    # save_date(text, time, best, db)
    return True


def erase_keywords(text, words_to_erase):
    """
    Erase possible keyword from the querying string. Useful for better
    results from the API

    :param text: String to query
    :type text: str
    :return: Cleaned string without these keywords
    :rtype: str
    """
    request_string = text.split()
    for word in words_to_erase:
        if word in request_string:
            request_string.remove(word)
    request_string = " ".join(request_string)
    return request_string


def fill_time(time, best, query_country="", result_countries=""):
    """
    Fills a placeholder of the time variables for the best match.
    :param time: Time's placeholder
    :type time: dict
    :param best: Best match
    :type best: dict
    :param query_country: Query's specified country.
    :type query_country: Optional[str]
    :param result_countries: List of the countries associated with the best match
    :type result_countries: str
    :return: Cleaned string without these keywords
    :rtype: str
    """
    # date_debug WAS ALREADY FILLED AT THE CHRONO REQUEST
    time["date_match_label"] = best["date_match_label"]
    time["date_debug_spatial"] = query_country
    time["date_start"] = best["date_start"]
    time["date_end"] = best["date_end"]
    time["date_match_label"] = best["date_match_label"]
    time["date_match_score"] = best["score"]
    time["date_match_id"] = best["date_match_id"]
    time["date_match_spatial"] = result_countries

    if settings.__DEBUG__:
        log(f"""String has been found in the chronontology API: {best['date_match_label']} (
              {str(best['date_start'])}-{str(best['date_end'])})""")


def clean_chron_response(data, countries_shape):
    """
    Takes the decoded JSON results of the Chronontology API query and saves them into a DataFrame
    :param data: Dictionary with Chronontology API query's results
    :type data: dict
    :param countries_shape: Shapefile with GIS information from the World. 
    :type countries_shape: dict
    :return: Cleaned results from Chronontology API
    :rtype: DataFrame
    """
    cleaned_data = []
    for rank, elem in enumerate(data["results"]):
        if "en" in elem["resource"]["names"]:
            for element in elem["resource"]["names"]["en"]:
                try:
                    chrono_date_start = elem["resource"]["hasTimespan"][0]["begin"]["at"]
                    if chrono_date_start is None:
                        continue
                    if not chrono_date_start.replace("-", "").isdigit():
                        continue
                    chrono_date_start = int(chrono_date_start)
                    if chrono_date_start < -400000 or chrono_date_start > 2022:
                        continue
                    new_elem = {"date_match_label": element,
                                "original_date": elem["resource"]["hasTimespan"][0]["timeOriginal"],
                                "date_start": elem["resource"]["hasTimespan"][0]["begin"]["at"],
                                "date_end": elem["resource"]["hasTimespan"][0]["end"]["at"],
                                "date_match_id": f"{elem['resource']['provenance']}:{elem['resource']['externalId']}",
                                "rank": rank}
                except KeyError:
                    continue
                new_elem["country_strings"] = ""
                new_elem["date_match_spatial"] = ""
                if "spatiallyPartOfRegion" in elem["resource"]:
                    new_elem["country_strings"] = ",".join(elem["resource"]["spatiallyPartOfRegion"])
                    countries = [ctr_str.split("/")[-1].lower() for ctr_str in
                                 elem["resource"]["spatiallyPartOfRegion"]]
                    countries = [" ".join(ctr.split("_")) for ctr in countries]
                    new_elem["date_match_spatial"] = ",".join(
                        [countries_shape["codes"][ctr] if ctr in countries_shape["codes"]
                         else ctr for ctr in countries])

                cleaned_data.append(new_elem)
    if not cleaned_data:
        cleaned_data = [{"date_match_label": "NULL",
                         "original_date": "",
                         "date_start": 0,
                         "date_end": 0,
                         "country_strings": "",
                         "date_match_spatial": "",
                         "rank": 0}]

    cleaned_data = pd.DataFrame(cleaned_data)
    return cleaned_data


def save_chrono_cache(cleaned_data, cached_dates, db):
    """
    save chrono response to tl_chrono_cache table
    :param cleaned_data: Cleaned DataFrame that contains the results from Chronontology
    :type cleaned_data: DataFrame
    :param db: Connection to PostgreSQL to save
    :type db: db connection string
    """
    chrono_date = cleaned_data.copy()
    tl_chrono_cache = pd.DataFrame({#"input_string": [chrono_date["date_original"]],
                                    "input_string": [chrono_date["date_english"]],
                                    "date_debug": [chrono_date["date_debug"]],
                                    "date_start": [chrono_date["date_start"]],
                                    "date_end": [chrono_date["date_end"]],
                                    "date_match_label": [chrono_date["date_match_label"]],
                                    "date_match_score": [chrono_date["date_match_score"]],
                                    "date_match_id": [chrono_date["date_match_id"]],
                                    "date_match_spatial": [chrono_date["date_match_spatial"]]
                                    })
    to_sql(tl_chrono_cache, "tl_chrono_cache", db)


def fill_chached_date(cached_date, time):
    time["date_english"] = cached_date["input_string"]
    time["date_start"] = cached_date["date_start"]
    time["date_end"] = cached_date["date_end"]
    time["date_debug"] = cached_date["date_debug"]
    time["date_match_label"] = cached_date["date_match_label"]
    time["date_match_score"] = cached_date["date_match_score"]
    time["date_match_spatial"] = cached_date["date_match_spatial"]
    time["date_match_id"] = cached_date["date_match_id"]


def call_chrono(text, time, country_info, countries_shape, cached_dates, engine):
    """
    Search for a chronontology entry in the IDAI API. If there is an entry, change the tome
    dictionary with updated metadata
    :param text: Date to clean
    :type text: list
    :param time: Dictionary with date metadata
    :type time: dict
    :param country_info: Two letter country code
    :type country_info: str
    :param countries_shape: Dictionary with countries information
    :type countries_shape: dict
    :param time: Time dictionary with date metadata
    :type time: dict
    :param engine: Parameters of engine (path and force option)
    :type engine: dict
    :return: True if an entry has been found at the confidence level. False otherwise
    :rtype: bool
    """
    if settings.__DEBUG__:
        log(f"Searching chronontology for:{text}")
    cleaned_data = None
    logging.info("Chrono search for string " + str(text) + " in the date: " + str(time["date_english"]))
    text = " ".join([w for w in text])
    words_to_erase = ["period", "the", "and", "era", "eras",
                      "culture", "style"]
    request_string = erase_keywords(text, words_to_erase)
    time["date_debug"] = request_string

    if country_info is not None and country_info["country_code"] is not None and country_info["country_code"] != "":
        time["date_debug_spatial"] = country_info["country_code"]
        cleaned_data = query_cache(request_string, country_info["country_code"], cached_dates=cached_dates)
    else:
        time["date_debug_spatial"] = ""
        cleaned_data = query_cache(request_string, country_code=None, cached_dates=cached_dates)

    if cleaned_data.empty:
        if country_info and country_info["name"]:
            request_string += " " + country_info["name"]
        try:
            response = requests.get("http://chronontology.dainst.org/data/period",
                                    params={"q": request_string, "size": 30, "fq": "resource.provenance:periodo"})
        except requests.exceptions.ConnectionError:
            log("Error when trying to retrieve information from chronontology API. Check you internet correction.")
            return False
        if response.status_code != 200:
            log("Something went wrong with the chronontology API. (Request did not return status code 200). String:" +
                request_string)
            return False
        data = json.loads(response.content.decode("utf-8"))
        if len(data["results"]) == 0:
            return False
        cleaned_data = clean_chron_response(data, countries_shape)
        found_at_chrono = search_best_match(time, cleaned_data, country_info, engine)

        if found_at_chrono:
            save_chrono_cache(time, cached_dates, engine)
    else:
        log("Found cached chrono date")
        fill_chached_date(cleaned_data, time)
        found_at_chrono = True

    return found_at_chrono


def search_chrono(date_original, country_code, countries_shape, time, cached_dates, engine):
    """
    Function that organizes the chronontology calls.
    If the original language is english, will first try to clean the original string and and call chronontology for it
    (Useful the spelling correction changed the meaning of the string, for ex "King dynasty" for "Ming Dynasty")
    If the original string was not english, process to call chronontology on the already cleaned and translated string

    :param date_original: Date string to query
    :type date_original: str
    :param country_code: Country code of the date string
    :type country_code: str
    :param countries_shape: Dictionary with countries information
    :type countries_shape: dict
    :param time: Time dictionary with date metadata
    :type time: dict
    :param engine: Parameters of engine (path and force option)
    :type engine: dict
    """

    country_info = None
    time["date_flags"] = "FF-CH"
    keywords_original = create_keywords()
    original = preprocess_text(date_original, time, correct_spelling=False, chronontology=True)
    #original = check_keywords(original, time, keywords_original)
    original = [word for word in original if word not in ["possibly"]]

    if countries_shape is None:
        # Load country information
        base_dir = os.path.dirname(os.path.abspath(__file__))
        countries_shape = pd.read_pickle(os.path.join(base_dir, "countries_shapefile.pkl"))
        countries_shape = countries_shape.to_dict(orient="records")
        countries_shape = {"info": {country["country_code"]: country for country in countries_shape},
                           "codes": {country["name"]: country["country_code"] for country in countries_shape}}

    if country_code and country_code.upper() in countries_shape["info"]:
        country_info = countries_shape["info"][country_code.upper()]

    found_at_chrono = call_chrono(original, time, country_info, countries_shape, cached_dates, engine)
    if found_at_chrono:
        process_keywords(time, keywords_original["split"], keywords_original["ordinal"], keywords_original["part"])
        if time["date_english"] is not None:
            time["date_english"] += keywords_to_string(keywords_original)

import os
import time as t
import pandas as pd
from tqdm import tqdm

from .parsing import parse_string
from .time_dict import create_time, fill_flags, check_country_code
from .dateparser import check_formatted_pattern
from .errors_input import check_errors, check_input
from .database import read_sql
from .manual_database import check_manual
from .chronontology import search_chrono
from .synonyms import check_synonym
from .validated_dates import check_validated_dates
from .package_logging import clear_log, get_log, log
import re

DATE_PACKAGE_VERSION = 2.1


def clean_date(date_english, date_original="",
               engine="postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@postgresql11.db.huma-num.fr/longrungrowth",
               country_code="", language="en", manual_dates=None, validated_dates=None, synonyms=None, cached_dates=None,
               force=False, debug=False, countries_shape=None):
    """
    Takes a string date as input and outputs a clean dictionary
    corresponding to the string's time period. Works with several languages.
    :param date: Date to clean
    :type date: str | int | float
    :param engine: Path of Database engine, defaults to
    "postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@postgresql11.db.huma-num.fr/longrungrowth"
    :type engine: str
    :param country_code: Country code of the country in which the object is located. Helps to find specific time periods
    if the program has to query the Chronontology API.
    :type country_code: str
    :param language: language of the input, defaults to "en" (english)
    :type language: str
    :param manual_dates: DataFrame holding manually inputted dates stored in a local database
    :type manual_dates: DataFrame
    :param validated_dates: DataFrame holding manually validated dates stored in a local database
    :type validated_dates: DataFrame
    :param synonyms: DataFrame holding synonyms from tl_synonyms
    :type synonyms: DataFrame
    :param force: Boolean that forces a chronontology API call (if needed) even in the case that the engine path is
    wrong or missing. If set to False, error in database call throws error. Set to True, the program ignores the error.
    (Exclusively for testing purposes !). Defaults to False
    :type force: bool
    :param debug: sets the debug mode where the decision tree is printed, defaults to false
    :type debug: bool
    :param countries_shape: DataFrame countaining the name and the shape of every existing country, defaults to None.
    If the user does not call clean_fill_df, i.e. the parameter is None, the function will laod the information if
    needed.
    :type countries_shape: DataFrame
    :return: Dictionary with a cleaned time period and the string's metadata
    :rtype: dict
    :Example:
    >>> from DateCleaning.DateCleaning import clean_date
    >>> date="01/01/1995"
    >>> cleaned_date = clean_date(date)
    >>> print(cleaned_date)
    {'date_start': 1995, 'date_end': 1995, 'date_english': '01/01/1995', 'date_original': '01/01/1995',
    'date_original_lang': 'en', 'date_flags': 'NF-NU', 'date_match_label': None, 'date_match_score': None}
    >>> print(cleaned_date["date_start"])
    1995
    >>> print(cleaned_date["date_end"])
    1995
    >>> date = "Early Han Dynasty"
    >>> cleaned_date = clean_date(date)

    >>> print(cleaned_date)
    {'date_start': -205, 'date_end': -64, 'date_english': 'han dynasty (early)', 'date_original': 'Early Han Dynasty',
    'date_original_lang': 'en', 'date_flags': 'FF-CH', 'date_match_label': 'han dynasty',
    'date_match_score': 1.0}
    >>> date = 'Ottoman Empire'
    >>> country = 'TR'
    >>> cleaned_date = clean_date(date, country_code = country)
    >>> print(cleaned_date)
    {'date_start': 1513, 'date_end': 1918, 'date_english': 'ottoman empire; turkey', 'date_original': 'Ottoman Empire',
    'date_original_lang': 'en', 'date_flags': 'FF-CH',
    'date_match_label': 'ottoman empire; CY,DJ,EG,GR,IQ,JO,LB,PS,SA,SD,SY,TR,YE', 'date_match_score': 1.0}
    .. note:: Function accepts two dates forming a period separated by character "-" (Ex: "1960-1970")
    .. note:: Requires internet connection for literal periods (Ex: "Early Han Dynasty")
    """

    #print(f"processing string: date_original={date_original}, date_english={date_original}, {country_code}")
    __DEBUG__ = True
    clear_log()
    # Check errors in input
    if language is not None and type(language) != str and len(language) != 2:
        raise ValueError("Language must be of type str and of length 2")
    time = create_time(language)
    time["date_package_version"] = DATE_PACKAGE_VERSION

    try:
        time["date_original"] = str(date_original).lower()
        time["date_english"] = str(date_english).lower()
        if check_errors(date_english, time) is False:
            return time

        date = check_input(date_english)
        country_code = check_country_code(country_code)
        # Parse the string
        #engine = {"path": engine, "force": force}

        #time["date_original"] = date
        time["parentheses"] = None

        check_formatted_pattern(date, time)
        if not time["date_start"]:
            parse_string(date, time)
            #check_manual(date_english, date_original, time, manual_dates, country_code)
        found_validated_date = True
        found_manual_date = True

        if time["date_start"] is None or time["date_start"] == "":
            date = date.replace("en: ", "")
            date = date.replace("en:", "")
            date = re.sub('[^-A-Za-z0-9 ]+', ' ', date)
            date = date.strip()
            date = check_synonym(date, date_original, synonyms, country_code)
            found_validated_date = check_validated_dates(date, time, validated_dates, country_code)

        if not found_validated_date:
            found_manual_date = check_manual(date, time, manual_dates, country_code)

        if not found_manual_date:
            search_chrono(date, country_code, countries_shape, time, cached_dates, engine)

        time["date_english"] = date_english
        if date_original != "":
            time["date_original"] = date_original
        fill_flags(time, date)
    except Exception as err:
        log(f"Error cleaning string: {date_original}, {country_code}")
        log(str(err))
        print(err)
    time["log"] = get_log()
    #if debug:
        #print(time["log"])
    return time


def clean_fill_df(df,
                  engine="postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@postgresql11.db.huma-num.fr/longrungrowth",
                  language="en", force=False, debug=True):
    """
    Takes a pandas DataFrame with all dates as input and fills it with the date's metadata.
    The DataFrame must be of size N*1.
    :param df: Dataframe to clean and fill. Must be of size N*1.
    :type df: pandas.core.series.series
    :param engine: Path of Database engine, defaults to
    "postgresql://user_longrungrowth:YjkqSNQ_CG6M25TKf@postgresql11.db.huma-num.fr/longrungrowth"
    :type engine: str
    :param language: language of the input, defaults to "en" (english)
    :type language: str
    :param force: Boolean that forces a chronontology API call (if needed) even in the case that the engine path is
    wrong or missing. If set to False, error in database call throws error. Set to True, the program ignores the error.
    (Exclusively for testing purposes !). Defaults to False
    :type force: bool
    :param debug: sets the debug mode where the decision tree is printed, defaults to false
    :type debug: bool
    :return: Dataframe with filled dates
    :rtype: DataFrame
    :Example:
    >>> from DateCleaning.DateCleaning import clean_fill_df
    >>> import pandas as pd
    >>>
    >>> df = pd.DataFrame({"Date":["Early Han Dynasty", "16th Century"]})
    >>> cleaned_df = clean_fill_df(df)
    >>> print(cleaned_df)
        date                date_start    ... date_original_lang date_flags date_match_label  date_match_score
    0  Early Han Dynasty        -205      ...           en      FF-CH       han dynasty                      1.0
    1       16th Century        1501      ...           en      NF-NU              None                      NaN
    >>> print(cleaned_df.iloc[0, :])
    date                         Early Han Dynasty
    date_start                                -205
    date_end                                   -64
    date_english               han dynasty (early)
    date_original                Early Han Dynasty
    date_original_lang                          en
    date_flags                               FF-CH
    date_match_label                  han dynasty
    date_match_score                    1.0
    Name: 0, dtype: object
    >>> df = pd.DataFrame({"str": ["byzantine empire", "ottoman empire"], "co": ["GR", "TR"]})
    >>> cleaned_df = clean_fill_df(df)
    Cleaning dates:   0%|                                                                         | 0/2 [00:00<?, ?it/s]
    Cleaning dates:  50%|█████████████████████████████████                                | 1/2 [00:00<00:00,  3.71it/s]
    Cleaning dates: 100%|████████████████████████████████████████████████████████████████ | 2/2 [00:00<00:00,  4.03it/s]
    0.6739811897277832 seconds
    >>> print(cleaned_df)
                   date country_code  date_start ... date_flags    date_match_label  date_match_score
    0  byzantine empire           GR         330 ... FF-CH       byzantine; GR,TR,CY                      1.0
    1    ottoman empire           TR        1288 ... FF-CH        ottoman empire; TR                      1.0
    >>> print(cleaned_df.iloc[0, :])
    date                          byzantine empire
    country_code                                GR
    date_start                                 330
    date_end                                  1453
    date_english                 byzantine; greece
    date_original                 byzantine empire
    date_original_lang                          en
    date_flags                               FF-CH
    date_match_label          byzantine; GR,TR,CY
    date_match_score                    1.0
    Name: 0, dtype: object
    """
    start = t.time()
    manual_dates = {}
    validated_dates = {}
    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)
    elif not isinstance(df, pd.core.frame.DataFrame):
        raise ValueError("Input must be of a pandas Dataframe or pandas Series")
    # if df.shape[1] > 1 and any(len(code) != 2 for code in df.iloc[:, 1]):
    #    raise ValueError("Country codes must be of size 2")
    #if df.shape[1] > 2:
    #    raise ValueError("Input must be of size N*1")
    dates = df.drop_duplicates().values.tolist()
    validated_dates = read_sql("SELECT * FROM tl_date_checked", engine)
    manual_dates = read_sql("SELECT * FROM tl_date_manual_mapping", engine)
    synonyms = read_sql("SELECT * FROM tl_synonyms", engine)
    cached_dates = read_sql("SELECT * FROM tl_chrono_cache", engine)

    # Load country information
    base_dir = os.path.dirname(os.path.abspath(__file__))
    countries_shape = pd.read_pickle(os.path.join(base_dir, "countries_shapefile.pkl"))
    countries_shape = countries_shape.to_dict(orient="records")
    countries_shape = {"info": {country["country_code"]: country for country in countries_shape},
                       "codes": {country["name"]: country["country_code"] for country in countries_shape}}

    if df.shape[1] == 3:

        time_dicts = [dict({"date": date[0], "country_code": date[2]},
                           **clean_date(date_english=date[0], date_original=date[1], engine=engine,
                                        country_code=date[2], language=language, manual_dates=manual_dates,
                                        validated_dates=validated_dates, synonyms=synonyms,
                                        cached_dates=cached_dates, force=force, debug=debug, countries_shape=countries_shape))
                      for date in tqdm(dates, desc="Cleaning dates")]
        df.columns = ["date_english", "date_original", "country_code"]
        df_unique = pd.DataFrame(time_dicts)
        new_df = pd.merge(df, df_unique, on=["date_english", "date_original", "country_code"], how="left")
    elif df.shape[1] == 2:
        time_dicts = [dict({"date": date[0], "country_code": date[1]},
                           **clean_date(date_english=date[0], date_original="", engine=engine,
                                        country_code=date[1], language=language, manual_dates=manual_dates,
                                        validated_dates=validated_dates, synonyms=synonyms,
                                        cached_dates=cached_dates, force=force, debug=debug, countries_shape=countries_shape))
                      for date in tqdm(dates, desc="Cleaning dates")]
        df.columns = ["date_english", "country_code"]
        df_unique = pd.DataFrame(time_dicts)
        new_df = pd.merge(df, df_unique, on=["date_english", "country_code"], how="left")

    else:
        time_dicts = [dict({"date": date[0]},
                           **clean_date(date_english=date[0], date_original="", engine=engine,
                                        country_code="", language=language, manual_dates=manual_dates,
                                        validated_dates=validated_dates, synonyms=synonyms,
                                        cached_dates=cached_dates, force=force, debug=debug, countries_shape=countries_shape))
                      for date in tqdm(dates, desc="Cleaning dates")]
        df.columns = ["date_english"]
        df_unique = pd.DataFrame(time_dicts)
        new_df = pd.merge(df, df_unique, on=["date_english"], how="left")
    end = t.time()
    print(end - start, "seconds")
    return new_df

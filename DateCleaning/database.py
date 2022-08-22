import time
import pandas as pd
import sqlalchemy
import sqlalchemy.exc

from . import settings
from .package_logging import log


def query_cache(input_string="", country_code=None, cached_dates=None):
    """
    This function takes an input string and queries it with the SQL database.
    It then returns an output string (which may or may not be empty).
    This function is for the main output string.

    :param input_string: String to query with the database
    :type input_string: str
    :param country_code: Two letter country code
    :type country_code: str
    :return: Data.frame with the corresponding start_date, end_date and confidence_level
    :rtype: DataFrame
    """
    found_in_cache_df = pd.DataFrame()
    if cached_dates is not None and len(cached_dates) > 0:
        found_in_cache_df = cached_dates[cached_dates["input_string"] == input_string]
        if "date_match_spatial" in cached_dates and country_code is not None:
            found_in_cache_df = found_in_cache_df[found_in_cache_df["date_match_spatial"] == country_code]
    if len(found_in_cache_df) > 0:
        return found_in_cache_df.iloc[0]
    else:
        return found_in_cache_df


def search_database(text, time, cache_return, confidence):
    """
    Function that parses the local database's output.

    :param text: String to query
    :type text: str
    :param time: Dictionary with time metadata
    :type time: dict
    :param cache_return: Local database's output
    :type cache_return: dict
    :param confidence: Confidence level at which we accept the output as a valid date
    :type confidence: int
    :return: Boolean that indicates if the local database returned a satisfactory data. False it not
    :rtype: bool
    """
    # if something was returned we check it against the confidence level
    if cache_return["confidence"][0] > confidence:
        if settings.__DEBUG__:
            log("String has been found in the chronontology API: " + text + " (" +
                  str(cache_return["date_start"][0]) + "-" + str(cache_return["date_end"][0]) + ")")
        # if it surpasses the confidence requirement we write it to the time dict
        time["date_start"] = cache_return["date_start"][0]
        time["date_end"] = cache_return["date_end"][0]
        return True
    else:
        return False


def open_db(engine_path, force):
    """
    Create the Engine object out of the database path. If the force option is enabled the program ignores error linked
    the Engine creation

    :param engine_path: Path to the database
    :type engine_path: str
    :param force: Force option
    :type force: bool
    :return: Engine object linked to the database
    :rtype: Engine
    """
    try:
        db = sqlalchemy.create_engine(engine_path)
    except sqlalchemy.exc.ArgumentError:
        if force is False:
            raise ValueError("Engine path is incorrect.")
        db = None
    except sqlalchemy.exc.OperationalError:
        if force is False:
            raise ValueError("Database is not right.")
        db = None
    return db


def read_sql(sql_string, engine):
    """
    run a pd.read_sql, but retry up to 5 times in case of connection errors
    :param sql_string: sql statement
    :param engine: connection string or object
    :return: data from database
    """
    i = 1
    error = None
    while i <= 15:
        try:
            return pd.read_sql(sql_string, engine)
        except Exception as e:
            print(f"Connection error, retrying in {i*i*10} seconds")
            error = e
            time.sleep(i*i*10)
        i += 1
    print("Connection error with postgres. Retried 5 times without success")
    raise error


def to_sql(pandas_df, table_name, engine):
    """
    same as pd.to_sql, but retry up to 5 times in case of connection errors
    :param pandas_df: df with the fields as in the table
    :param table_name: exact as in the database
    :param engine: connection string or object
    :return:
    """
    i = 1
    error = None
    while i <= 15:
        try:
            pandas_df.to_sql(table_name, con=engine,
                             if_exists='append', index=False)
            return
        except Exception as e:
            print(f"Connection error, retrying in {i*i*10} seconds")
            error = e
            time.sleep(i*i*10)
        i += 1
    print("Connection error with postgres. Retried 5 times without success")
    raise error

def get_perido_data(periodo_ids, engine):
    i = 1
    error = None
    while i <= 15:
        try:
            ids = "','".join(periodo_ids)
            sql_string = f"select * from tl_date_periodo where periodo_id in ('{ids}')"
            return pd.read_sql(sql_string, con=engine)
        except Exception as e:
            print(f"Connection error, retrying in {i*i*10} seconds")
            error = e
            time.sleep(i*i*10)
        i += 1
    print("Connection error with postgres. Retried 15 times without success")
    raise error

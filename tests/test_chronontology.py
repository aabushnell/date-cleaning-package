import sys
import os
import pytest

import numpy as np
import pandas as pd
from db_connection import get_engine, get_postgres_engine
from DateCleaning.DateCleaning import clean_date, clean_fill_df

engine = get_engine()
#engine = get_postgres_engine()


def insert_manual_date(date, date_start, date_end,
                       country_codes="", is_date_original=False):
    columns = ["input_string", "date_start", "date_end",
               "countries", "is_date_original"]
    tl_date_manual_mapping = pd.DataFrame(columns=columns)
    data = pd.Series([date, date_start, date_end, country_codes, is_date_original],
                     index=tl_date_manual_mapping.columns)
    tl_date_manual_mapping = tl_date_manual_mapping.append(data, ignore_index=True)
    tl_date_manual_mapping.to_sql('tl_date_manual_mapping', con=engine, if_exists='append', index=False)

def insert_validated_date(date_english, date_start, date_end, correct,
                          date_debug, date_debug_spatial, date_match_id, date_match_label,
                          date_match_score, date_match_spatial, location_mapped_country):
    columns = ["date_english", "date_start", "date_end", "correct",
                          "date_debug", "date_debug_spatial", "date_match_id", "date_match_label",
                          "date_match_score", "date_match_spatial", "location_mapped_country"]

    tl_date_checked = pd.DataFrame(columns=columns)
    data = pd.Series([date_english, date_start, date_end, correct,
                      date_debug, date_debug_spatial, date_match_id, date_match_label,
                      date_match_score, date_match_spatial, location_mapped_country],
                     index=tl_date_checked.columns)
    tl_date_checked = tl_date_checked.append(data, ignore_index=True)
    tl_date_checked.to_sql('tl_date_checked', con=engine, if_exists='replace', index=False)

def insert_synonym(original_string, synonym, comment, is_date_original):
    columns = ["original_string", "synonym", "comment", "is_date_original"]
    tl_synonyms = pd.DataFrame(columns=columns)
    data = pd.Series([original_string, synonym, comment, is_date_original], index=tl_synonyms.columns)
    tl_synonyms = tl_synonyms.append(data, ignore_index=True)
    tl_synonyms.to_sql('tl_synonyms', con=engine, if_exists='replace', index=False)

class TestChronontology(object):

    def test_middle_kingdom(self):
        date = clean_date(date_english="middle kingdom",
                          engine=engine, debug=True)
        assert date["date_start"] == -2179
        assert date["date_end"] == -1550


    def test_date_original_manual(self):
        insert_manual_date("northern kingdom", 1000, 2000,
                           country_codes="", is_date_original=True)
        insert_manual_date("northern kingdom", 10, 20,
                           country_codes="", is_date_original=False)
        manual_dates = pd.read_sql("select * from tl_date_manual_mapping", engine)

        date = clean_date(date_original="northern kingdom",
                          date_english="northern kingdom",
                          manual_dates=manual_dates,
                          engine=engine, debug=True)
        assert date["date_start"] == 1000
        assert date["date_end"] == 2000
        date = clean_date(date_english="northern kingdom",
                          manual_dates=manual_dates,
                          engine=engine, debug=True)
        assert date["date_start"] == 10
        assert date["date_end"] == 20


    def test_iron_ii(self):
        date = clean_date(date_english="iron ii", engine=engine, debug=True)
        assert date["date_start"] == -999
        assert date["date_end"] == -585

    def test_santa_rosa(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["santa rosa"], "co": ["PR"]}), engine)
        assert dates.iloc[0]["date_debug"] == "santa rosa"
        assert dates.iloc[0]["date_match_label"] == "santa rosa"

    def test_date_origin(self):
        date = clean_date(date_original="fecha original", date_english="en:ming dynasty period", engine=engine, debug=True)
        assert date["date_original"] == "fecha original"
        assert date["date_english"] == "en:ming dynasty period"
        assert date["date_debug"] == "ming dynasty"
        assert date["date_start"] == 1368
        assert date["date_end"] == 1644

    def test_debug(self):
        date = clean_date(date_english="en:ming dynasty", engine=engine, debug=True)
        assert date["date_start"] == 1368
        assert date["date_end"] == 1644

    def test_ming_dynasty(self):
        date = clean_date(date_english="ming dynasty", engine=engine, debug=True)
        assert date["date_start"] == 1368
        assert date["date_end"] == 1644

        date = clean_date(date_english="ming", engine=engine, debug=True)
        assert date["date_start"] == 1368
        assert date["date_end"] == 1644


    def test_bounds(self):
        date = clean_date(date_english="two dry", engine=engine, debug=True)
        assert date["date_start"] == ""
        assert date["date_end"] == ""

    # This code will query chron and then insert it on the
    def test_chronontology_not_in_manual_mapping(self):
        date = clean_date(date_english="cabanagem", engine=engine, debug=True)
        assert date["date_start"] == 1835
        assert date["date_end"] == 1840

    def test_close_countries_1(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["ottoman empire"], "co": ["TR"]}), engine)
        assert dates.iloc[0]["date_start"] == 1288
        assert dates.iloc[0]["date_end"] == 1918
        assert dates.iloc[0]["date_flags"] == "FF-CH"

    def test_close_countries_2(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["byzantine empire"], "co": ["GR"]}), engine)
        assert dates.iloc[0]["date_start"] == 324
        assert dates.iloc[0]["date_end"] == 1453
        assert dates.iloc[0]["date_flags"] == "FF-CH"

    def test_close_countries_3(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["byzantine"], "co": ["RO"]}), engine)
        assert dates.iloc[0]["date_start"] == 1000
        assert dates.iloc[0]["date_end"] == 1389
        assert dates.iloc[0]["date_flags"] == "FF-CH"
    
    def test_french_revolution(self):
        date = clean_date("french revolution", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1794
        assert date["date_flags"] == "FF-CH"

        # do it again to test cashed data
        date = clean_date("french revolution", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1794

    def test_df(self):
        dates = clean_fill_df(pd.Series(["1450-1500", "1789.1799"]), engine)
        assert dates.iloc[0]["date_start"] == 1450
        assert dates.iloc[1]["date_start"] == 1789

    def test_df_manual(self):
        """
        Inserts data into tl_date_manual_mapping check if clean_fill_df picks it correctly
        """
        insert_manual_date("vaccine revolt", 1904, 1904, "")
        dates = clean_fill_df(pd.Series(["vaccine revolt", "republic"]), engine)
        assert dates.iloc[0]["date_start"] == 1904
        assert dates.iloc[0]["date_end"] == 1904
        assert dates.iloc[0]["date_flags"] == "NF-MN"
        assert dates.iloc[0]["date_english"] == "vaccine revolt"
        #assert dates.iloc[0]["date_original"] == "vaccine revolt"
        assert dates.iloc[0]["date_original_lang"] == "en"
        columns = ["date_debug", "date_debug_spatial", "date_match_id", "date_match_label",
                   "date_match_score", "date_match_spatial"]
        for column in columns:
            assert column in dates.iloc[0]

    def test_synonym(self):
        # synonym: Capture of the Bastille = french revolution
        insert_synonym("capture of the bastille", "french revolution", "unit test", False)

        #dates = clean_fill_df(pd.DataFrame({"date_english": ["capture of the bastille"], "co": ["FR"]}), engine)
        dates = clean_fill_df(pd.Series(["capture of the bastille"]), engine)
        assert dates.iloc[0]["date_start"] == 1789
        assert dates.iloc[0]["date_end"] == 1794
        assert dates.iloc[0]["date_flags"] == "FF-CH"

    def test_manual_mapping_country(self):
        #Combines synonym with manual mapping
        insert_synonym("ww ii", "world war ii", "", False)
        insert_manual_date("world war ii", 1939, 1945, "")
        dates = clean_fill_df(pd.Series(["ww ii"]), engine)
        assert dates.iloc[0]["date_start"] == 1939
        assert dates.iloc[0]["date_end"] == 1945
        assert dates.iloc[0]["date_flags"] == "NF-MN"


    def test_date_match_label(self):
        insert_manual_date("my empire", 1912, 1914, "FR")
        insert_manual_date("my empire", 1900, 1900, "SP")
        dates = clean_fill_df(pd.DataFrame({"date_english": ["my empire"], "co": ["FR"]}), engine)
        assert dates.iloc[0]["date_start"] == 1912
        assert dates.iloc[0]["date_end"] == 1914
        # assert dates.iloc[0]["date_flags"] == "NF-MN"

    def test_cached_date(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["war of independence"], "co": ["AR"]}), engine)
        assert dates.iloc[0]["date_start"] == 1810
        assert dates.iloc[0]["date_end"] == 1817

        dates = clean_fill_df(pd.DataFrame({"date_english": ["war of independence"], "co": ["AR"]}), engine)
        assert dates.iloc[0]["date_start"] == 1810
        assert dates.iloc[0]["date_end"] == 1817
        assert dates.iloc[0]["date_match_label"] == 'war of independence'
        assert 'AR' in dates.iloc[0]["date_match_spatial"]
    
    def test_multiple_countries_1(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["ottoman empire"], "co": ["crete"]}), engine)
        assert dates.iloc[0]["date_flags"] == 'FF-CH'

    def test_multiple_countries_2(self):
        """
        This test asserts multiple requirements of the code:
        1. The code can take multiple two-letter country codes.
        2. It'll pick the first two-letter country code.
        3. If there aren't two-letter country code, but larger strings, it'll return the 'FF-CC', which means that the
        Country Code is wrong.
        4. The code won't stop if it has more any line has more than one country code. 
        """
        dates = clean_fill_df(pd.DataFrame({"date_english": ["ottoman empire", "ottoman empire", "ottoman empire"],
                                            "co": ["Turke", "TR", "Turke,SY,TR"]}), engine)
        assert dates.iloc[0]["date_flags"] == 'FF-CH'
        assert dates.iloc[1]["date_flags"] == "FF-CH"
        assert dates.iloc[2]["date_flags"] == "FF-CH"

    def test_date_match_id(self):
        date = clean_date("french revolution", engine)
        assert date["date_match_id"] == "periodo:p06c6g3kwjx,p06c6g38xfb"

        #check if with chached date we also get the id
        date = clean_date("french revolution", engine, debug=True)
        assert date["date_match_id"] == "periodo:p06c6g3kwjx,p06c6g38xfb"

    def test_api_id(self):
        date = clean_date("Late Chalcolithic", engine)
        assert date["date_match_id"] == "periodo:p0m63njtxw8"

    def test_date_match_spatial(self):
        dates = clean_fill_df(pd.DataFrame({"date_english": ["french revolution"],
                                            "co": ["FR"]}), engine)
        assert dates.iloc[0]["date_match_spatial"] == "FR"

        dates = clean_fill_df(pd.DataFrame({"date_english": ["french revolution"],
                                            "co": ["BE"]}), engine)
        assert dates.iloc[0]["date_match_spatial"] == "FR"

    def test_date_match_spatial_no_country(self):
        date = clean_date("french revolution", engine, debug=True)
        assert date["date_match_spatial"] == "FR"

        #Test again to see if cached data has date_match_spatial
        date = clean_date("french revolution", engine, debug=True)
        assert date["date_match_spatial"] == "FR"

    def test_all_fields_chrono_cache(self):
        date = clean_date("french revolution", engine, debug=True)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1794
        assert date["date_english"] == "french revolution"
        #assert date["date_original"] == "french revolution"
        assert date["date_original_lang"] == "en"
        assert date["date_debug"] == "french revolution"
        assert date["date_debug_spatial"] == "no country info"
        assert date["date_match_id"] == "periodo:p06c6g3kwjx,p06c6g38xfb"
        assert date["date_match_label"] == "french revolution"
        assert date["date_match_score"] == 1
        assert date["date_match_spatial"] == "FR"

        #Test again to see if cached data has date_match_spatial
        date = clean_date("french revolution", engine, debug=True)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1794
        assert date["date_english"] == "french revolution"
        #assert date["date_original"] == "french revolution"
        assert date["date_original_lang"] == "en"
        assert date["date_debug"] == "french revolution"
        assert date["date_debug_spatial"] == "no country info"
        assert date["date_match_id"] == "periodo:p06c6g3kwjx,p06c6g38xfb"
        assert date["date_match_label"] == "french revolution"
        assert date["date_match_score"] == 1
        assert date["date_match_spatial"] == "FR"
        assert "date_package_version" in date

    def test_all_fields_validated_dates(self):
        insert_validated_date(date_english="civil war", location_mapped_country="US", date_start=1861, date_end=1865, correct=1,
            date_debug="civil war", date_debug_spatial="US", date_match_id="periodo:123",
            date_match_label="civil war", date_match_score=0.98, date_match_spatial='US')
        date = clean_fill_df(pd.DataFrame({"date_english": ["civil war"],
                                            "co": ["US"]}), engine)
        assert date.iloc[0]["date_start"] == 1861
        assert date.iloc[0]["date_end"] == 1865
        assert date.iloc[0]["date_english"] == "civil war"
        #assert date.iloc[0]["date_original"] == "civil war"
        assert date.iloc[0]["date_original_lang"] == "en"
        assert date.iloc[0]["date_debug"] == "civil war"
        assert date.iloc[0]["date_debug_spatial"] == "US"
        assert date.iloc[0]["date_match_id"] == "periodo:123"
        assert date.iloc[0]["date_match_label"] == "civil war"
        assert date.iloc[0]["date_match_score"] == 0.98
        assert date.iloc[0]["date_match_spatial"] == "US"
        assert "date_package_version" in date.iloc[0]

    def test_null_conutry(self):
        date = clean_fill_df(pd.DataFrame({"date_english": ["civil war"],
                                           "co": [np.nan]}), engine)

        date = clean_fill_df(pd.DataFrame({"date_english": ["civil war"],
                                           "co": [None]}), engine)
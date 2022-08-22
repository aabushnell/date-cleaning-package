import sys
import os
from db_connection import get_engine
from DateCleaning.DateCleaning import clean_date

engine = get_engine()

class BasicLanguage(object):

    # French
    def test_basic_french(self):
        date = clean_date("age de bronze", engine, language="fr")
        assert date["date_start"] == -2500
        assert date["date_end"] == -750
        assert date["date_original_lang"] == "fr"
        assert date["date_english"] == "bronze age"

    # German
    #def test_basic_german(self):
    #    date = clean_date("bronzezeit", engine, language="de")
     ##   assert date["date_start"] == -2500
     #   assert date["date_end"] == -750
     #   assert date["date_original_lang"] == "de"
      #  assert date["date_english"] == "bronze age"

    # Spanish
    def test_basic_spanish(self):
        date = clean_date("edad de bronze", engine, language="es")
        assert date["date_start"] == -2500
        assert date["date_end"] == -750
        assert date["date_original_lang"] == "es"
        assert date["date_english"] == "bronze age"

    # Chinese
    def test_basic_chinese(self):
        date = clean_date("青銅時代", engine, language="ch")
        assert date["date_start"] == -2500
        assert date["date_end"] == -750
        assert date["date_original_lang"] == "ch"
        assert date["date_english"] == "bronze age"

    # French century
    def test_basic_century_french(self):
        date = clean_date("20eme siecle", engine, language="fr")
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000
        assert date["date_original_lang"] == "fr"
        assert date["date_english"] == "20th century"

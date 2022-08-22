import sys
import os
from db_connection import get_engine

sys.path.insert(0, os.path.abspath('../'))

from DateCleaning.DateCleaning import clean_date

engine = get_engine()

class TestBasicSpelling(object):
    # Basic english spelling millennium
    def test_english_millennium(self):
        date = clean_date("3rd millenium", engine, language="en")
        assert date["date_start"] == 2001
        assert date["date_end"] == 3000

    # Basic english spelling millennium
    def test_english_millennium_2(self):
        date = clean_date("3rd milenium", engine, language="en")
        assert date["date_start"] == 2001
        assert date["date_end"] == 3000

    # Basic english spelling century
    def test_english_century(self):
        date = clean_date("3rd cetury", engine, language="en")
        assert date["date_start"] == 201
        assert date["date_end"] == 300


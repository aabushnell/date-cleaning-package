from db_connection import get_engine
from DateCleaning.DateCleaning import clean_date

engine = get_engine()


class TestBasicMillennium(object):
    # Basic millennium
    def test_basic_millennium(self):
        date = clean_date("2nd millennium", engine)
        assert date["date_start"] == 1001
        assert date["date_end"] == 2000

    # Basic millennium BC
    def test_basic_millennium_bc(self):
        date = clean_date("3rd millennium B.C", engine)
        assert date["date_start"] == -3000
        assert date["date_end"] == -2001


class TestMediumMillennium(object):
    # Missing century
    def test_medium_millennium(self):
        date = clean_date("early 3rd millennium B.C", engine)
        assert date["date_start"] == -3000
        assert date["date_end"] == -2667

    # Missing millennium
    def test_missing_millennium(self):
        date = clean_date("4th-3th millennium BC", engine)
        assert date["date_start"] == -4000
        assert date["date_end"] == -2001

    # Missing millennium
    def test_missing_millennium_2(self):
        date = clean_date("4th-3rd millenium B.C", engine)
        assert date["date_start"] == -4000
        assert date["date_end"] == -2001

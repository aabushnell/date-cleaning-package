from db_connection import get_engine
from DateCleaning.DateCleaning import clean_date

engine = get_engine()

class TestBasicYear(object):

    # Basic year
    def test_basic_year(self):
        date = clean_date("1789", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1789

    # Basic year
    def test_basic_year_minus(self):
        date = clean_date("-1789", engine)
        assert date["date_start"] == -1789
        assert date["date_end"] == -1789

    # Basic year with noise
    def test_basic_year_with_noise(self):
        date = clean_date("blalbla 1789 blalblalb", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1789

    # Basic year period
    def test_basic_year_period(self):
        date = clean_date("1789-1790", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year period
    def test_basic_year_period_minus(self):
        date = clean_date("-1790--1789", engine)
        assert date["date_start"] == -1790
        assert date["date_end"] == -1789

    # Basic year period
    def test_basic_year_period_minus_2(self):
        date = clean_date("-2500 to 1066", engine)
        assert date["date_start"] == -2500
        assert date["date_end"] == 1066
        
    # Basic year period
    def test_basic_year_period_minus_3(self):
        date = clean_date("-1790-1789", engine)
        assert date["date_start"] == -1790
        assert date["date_end"] == 1789

    # Basic year period
    def test_basic_year_period_minus_4(self):
        date = clean_date("-w 100 - 200", engine)
        assert date["date_start"] == 100
        assert date["date_end"] == 200

    # Basic year period
    def test_basic_year_period_minus_5(self):
        date = clean_date("- 200 - -100", engine)
        assert date["date_start"] == -200
        assert date["date_end"] == -100

    # Basic year period
    def test_basic_year_period_minus_6(self):
        date = clean_date("- 200 - - 100", engine)
        assert date["date_start"] == -200
        assert date["date_end"] == -100

    # Basic year without dash
    def test_basic_year_period_without_dash(self):
        date = clean_date("1789 1790", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year without dash and missing thousands
    def test_basic_year_period_without_dash_and_thousands(self):
        date = clean_date("1789 790", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year without dash and missing thousands and hundreds
    def test_basic_year_period_without_dash_and_hundreds(self):
        date = clean_date("1789 90", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year without dash and missing thousands and hundreds and tenths
    def test_basic_year_period_without_dash_and_tenths(self):
        date = clean_date("1786 9", engine)
        assert date["date_start"] == 1786
        assert date["date_end"] == 1789

    # Basic decade
    def test_basic_decade(self):
        date = clean_date("1960s", engine)
        assert date["date_start"] == 1960
        assert date["date_end"] == 1969

    # Basic decade BC
    def test_basic_decade_bc(self):
        date = clean_date("390s BC", engine)
        assert date["date_start"] == -399
        assert date["date_end"] == -390

    # Basic decade without thousands and hundreds
    def test_basic_without_thousands_and_hundreds(self):
        date = clean_date("60s", engine)
        assert date["date_start"] == 1960
        assert date["date_end"] == 1969

    # Basic year with dash and missing thousands
    def test_basic_year_period_with_dash_and_thousands(self):
        date = clean_date("1789-790", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year with dash and missing thousands and hundreds
    def test_basic_year_period_with_dash_and_hundreds(self):
        date = clean_date("1789-90", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1790

    # Basic year with dash and missing thousands and hundreds and tenths
    def test_basic_year_period_with_dash_and_tenths(self):
        date = clean_date("1786-9", engine)
        assert date["date_start"] == 1786
        assert date["date_end"] == 1789

    # Basic year with BC with blank
    def test_basic_year_blank_BC(self):
        date = clean_date("1300 B. C.", engine)
        assert date["date_start"] == -1300
        assert date["date_end"] == -1300

    # Basic year with BC with blank
    def test_basic_year_blank_BC_1(self):
        date = clean_date("1400 - 1300 B. C.", engine)
        assert date["date_start"] == -1400
        assert date["date_end"] == -1300

    # Basic year with BC with blank
    def test_basic_year_blank_BC_2(self):
        date = clean_date("1200 B. C. - 1300 B. C.", engine)
        assert date["date_start"] == -1300
        assert date["date_end"] == -1200

    # Basic year with BC with blank
    def test_basic_year_blank_BC_3(self):
        date = clean_date("1200 - 1300 B. C.", engine)
        assert date["date_start"] == -1300
        assert date["date_end"] == -1200

    # Basic year with BC with blank
    def test_basic_year_blank_BC_4(self):
        date = clean_date("100 - 200 B. C.", engine)
        assert date["date_start"] == -200
        assert date["date_end"] == -100


class TestBasicMillennium(object):

    # Basic date
    def test_basic_date(self):
        date = clean_date("05/09/1999", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_2(self):
        date = clean_date("05/09/99", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_3(self):
        date = clean_date("99/09/01", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_4(self):
        date = clean_date("1999/09/01", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_5(self):
        date = clean_date("05-09-1999", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_6(self):
        date = clean_date("05-09-99", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_7(self):
        date = clean_date("99-09-01", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_8(self):
        date = clean_date("1999-09-01", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Basic date
    def test_basic_date_period(self):
        date = clean_date("1/1/200-31/12/299", engine)
        assert date["date_start"] == 200
        assert date["date_end"] == 299
        

class TestMediumYear(object):
    # Year with BC
    def test_year_bc(self):
        date = clean_date("100 BC", engine)
        assert date["date_start"] == -100
        assert date["date_end"] == -100

    # Year with full date
    def test_full_date(self):
        date = clean_date("31 December 1999", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # Year with BC
    def test_year_bc_with_dot(self):
        date = clean_date("100 b.C.", engine)
        assert date["date_start"] == -100
        assert date["date_end"] == -100

    # Year with BC without space
    def test_year_bc_without_space(self):
        date = clean_date("100BC", engine)
        assert date["date_start"] == -100
        assert date["date_end"] == -100

    # Period with BC
    def test_period_bc(self):
        date = clean_date("300 BC - 100 BC", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -100

    # Period with missing BC
    def test_period_missing_bc(self):
        date = clean_date("3000 1500 B.C.", engine)
        assert date["date_start"] == -3000
        assert date["date_end"] == -1500

    # Period with BC-AD
    def test_period_bc_ad(self):
        date = clean_date("300 BC - 100 AD", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == 100

    # Period with AD-AD
    def test_period_ad_ad(self):
        date = clean_date("100 AD - 300 AD", engine)
        assert date["date_start"] == 100
        assert date["date_end"] == 300

    # Period with BC without dash
    def test_period_bc_without_dash(self):
        date = clean_date("300 BC  100 BC", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -100

    # Period with BC-AD without dash
    def test_period_bc_without_dash_2(self):
        date = clean_date("300 BC  100 AD", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == 100

    # Period with BC without dash
    def test_period_bce_without_dash(self):
        date = clean_date("300 BCE  100 BCE", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -100

    # Period with AD-AD without dash
    def test_period_ad_ad_without_dash(self):
        date = clean_date("100 AD  300 AD", engine)
        assert date["date_start"] == 100
        assert date["date_end"] == 300

    # Date islamic calendar
    def test_date_islamic(self):
        date = clean_date("A.H. 1075", engine)
        assert date["date_start"] == 1664
        assert date["date_end"] == 1664

    # Date islamic calendar
    def test_date_islamic_2(self):
        date = clean_date("1075ah", engine)
        assert date["date_start"] == 1664
        assert date["date_end"] == 1664

    # Date islamic calendar
    def test_date_islamic_3(self):
        date = clean_date("A.H. 1075/ A.D. 1664–65", engine)
        assert date["date_start"] == 1664
        assert date["date_end"] == 1665

    # Date islamic calendar
    def test_date_islamic_4(self):
        date = clean_date("dated A.H. 141/ A.D. 758", engine)
        assert date["date_start"] == 758
        assert date["date_end"] == 758

    # Date century with s
    def test_date_century_with_s(self):
        date = clean_date("300s", engine)
        assert date["date_start"] == 301
        assert date["date_end"] == 400

    # Date century with s
    def test_date_century_with_s_bc(self):
        date = clean_date("300s bc", engine)
        assert date["date_start"] == -400
        assert date["date_end"] == -301

    # Date century with s
    def test_date_century_with_s_keyword(self):
        date = clean_date("mid 300s", engine)
        assert date["date_start"] == 334
        assert date["date_end"] == 367

    # Date century with s
    def test_date_century_with_s_keyword_2(self):
        date = clean_date("early 300s", engine)
        assert date["date_start"] == 301
        assert date["date_end"] == 334

    # Date century with s
    def test_date_month(self):
        date = clean_date("October 3-21 1993", engine)
        assert date["date_start"] == 1993
        assert date["date_end"] == 1993

    # Date day with a month
    def test_date_month_2(self):
        date = clean_date("january 31", engine)
        assert date["date_start"] == ""
        assert date["date_end"] == ""

    # Date day with a month
    def test_date_month_3(self):
        date = clean_date("31 january", engine)
        assert date["date_start"] == ""
        assert date["date_end"] == ""

    # Date century multiple years
    def test_date_multiple_years(self):
        date = clean_date("1926/35, early Shôwa period (1926–1989)", engine)
        assert date["date_start"] == 1926
        assert date["date_end"] == 1935

    # Date yeer with comma
    def test_year_comma(self):
        date = clean_date("1,000", engine)
        assert date["date_start"] == 1000
        assert date["date_end"] == 1000

    # Date yeer with comma
    def test_year_comma_2(self):
        date = clean_date("1,000 B.C/200 B.C.", engine)
        assert date["date_start"] == -1000
        assert date["date_end"] == -200

    # Date new decade
    def test_year_new_decade(self):
        date = clean_date("Ming dynasty (1368–1644), c. 1590's", engine)
        assert date["date_start"] == 1590
        assert date["date_end"] == 1599


class TestParsingYear(object):
    # Year with BC
    def test_parsing_year(self):
        date = clean_date("Western Zhou dynasty ( 1046–771 BC ), 1000/950 BC", engine)
        assert date["date_start"] == -1000
        assert date["date_end"] == -950

    # Year with suffix
    def test_parsing_year_suffix(self):
        date = clean_date("c.1954/80", engine)
        assert date["date_start"] == 1954
        assert date["date_end"] == 1980
        
    # Year with before
    def test_parsing_year_before(self):
        date = clean_date("20th century, before 1975", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 1975

    # Year with after
    def test_parsing_year_after(self):
        date = clean_date("20th century, after 1975", engine)
        assert date["date_start"] == 1975
        assert date["date_end"] == 2000

    # Year with wrong order BC
    def test_year_wrong_order_BC(self):
        date = clean_date("500 BC - 10000 BC", engine)
        assert date["date_start"] == -10000
        assert date["date_end"] == -500

    # Year with days and dash
    def test_year_with_days_and_dash(self):
        date = clean_date("9-11 june 1995", engine)
        assert date["date_start"] == 1995
        assert date["date_end"] == 1995

    # Year with days and dash
    def test_year_with_days_and_dash_2(self):
        date = clean_date("0-1995", engine)
        assert date["date_start"] == 1995
        assert date["date_end"] == 1995

    # Year with days and dash
    def test_year_with_days_and_dash_3(self):
        date = clean_date("1789 04 - 1889 04", engine)
        assert date["date_start"] == 1789
        assert date["date_end"] == 1889

    # Year with days and dash
    def test_year_with_days_and_dash_4(self):
        date = clean_date("1876, 2/1873 - 6/1876", engine)
        assert date["date_start"] == 1873
        assert date["date_end"] == 1876

    # Low year without dash
    def test_low_year_without_dash(self):
        date = clean_date("35 123", engine)
        assert date["date_start"] == 35
        assert date["date_end"] == 123

    # Hidden year
    def test_hidden_year(self):
        date = clean_date("1456lala", engine)
        assert date["date_start"] == 1456
        assert date["date_end"] == 1456

    # Hidden year
    def test_hidden_year_2(self):
        date = clean_date("rgseg1456lala", engine)
        assert date["date_start"] == 1456
        assert date["date_end"] == 1456

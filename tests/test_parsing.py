from db_connection import get_engine
from DateCleaning.DateCleaning import clean_date

engine = get_engine()

class TestParsing(object):

    def test_columns(self):
        date = clean_date("blablabla", engine)
        columns = ["date_debug", "date_debug_spatial", "date_match_id", "date_match_label",
                   "date_match_score", "date_match_spatial"]
        for column in columns:
            assert column in date

        date = clean_date("ca. 1902-3", engine)
        columns = ["date_debug", "date_debug_spatial", "date_match_id", "date_match_label",
                   "date_match_score", "date_match_spatial"]
        for column in columns:
            assert column in date

    # No valid date
    def test_no_valid_date(self):
        date = clean_date("blablabla", engine)
        assert date["date_start"] == ""
        assert date["date_end"] == ""

    # No valid date
    def test_valid_date_with_punctuation(self):
        date = clean_date("1790, third month", engine)
        assert date["date_start"] == 1790
        assert date["date_end"] == 1790

    # No valid period (first error)
    def test_no_valid_period_1(self):
        date = clean_date("100-blablabla", engine)
        assert date["date_start"] == 100
        assert date["date_end"] == 100

    # No valid period (second error)
    def test_no_valid_period_2(self):
        date = clean_date("blablabla-16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1600

    # No valid period (second error)
    def test_no_period_with_noise(self):
        date = clean_date("ca. 1902-3", engine)
        assert date["date_start"] == 1902
        assert date["date_end"] == 1903

    # Multiple date with year
    def test_multiple_date_with_year(self):
        date = clean_date("19-th 1891 4 quarter of the 19th century Second half millenium AD", engine)
        assert date["date_start"] == 1891
        assert date["date_end"] == 1891

    # Century without blank
    def test_century_without_blank(self):
        date = clean_date("20thcentury", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000

    # Century as C
    def test_century_as_c(self):
        date = clean_date("20thC", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000

    # Century as C
    def test_century_as_c_keyword(self):
        date = clean_date("20thC (early)", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 1934

    # Century without blank
    def test_millennium_without_blank(self):
        date = clean_date("2ndmillennium", engine)
        assert date["date_start"] == 1001
        assert date["date_end"] == 2000

    # Weird character
    def test_weird_character(self):
        date = clean_date("Late Period, Dynasty 261930", engine)
        assert date["date_start"] == 1930
        assert date["date_end"] == 1930

    # Additional date error
    def test_additional_date_error(self):
        date = clean_date("1857 [Ansei 4], 9th month", engine)
        assert date["date_start"] == 1857
        assert date["date_end"] == 1857

    # Additional date error
    def test_additional_narrow_century(self):
        date = clean_date("tang dynasty 618–907 a d , first half of 8th century", engine)
        assert date["date_start"] == 701
        assert date["date_end"] == 750

    # Additional date error
    def test_additional_narrow_century_2(self):
        date = clean_date("18th century, qing dynasty1644–1911", engine)
        assert date["date_start"] == 1701
        assert date["date_end"] == 1800
        
    # Additional date error
    def test_centuries_at_end(self):
        date = clean_date("ing dynasty 1644–1911, mid 18th century", engine)
        assert date["date_start"] == 1734
        assert date["date_end"] == 1767

    # Additional date error
    def test_printed_ignore(self):
        date = clean_date("1978; printed 2007", engine)
        assert date["date_start"] == 1978
        assert date["date_end"] == 1978
        
    # Additional date error
    def test_multiple_parts(self):
        date = clean_date("mid- to late 1300s", engine)
        assert date["date_start"] == 1334
        assert date["date_end"] == 1400

    # Additional date error
    def test_c_in_string(self):
        date = clean_date("3rd-1st C BC", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -1

class TestParentheses(object):

    # Parentheses
    def test_parentheses(self):
        date = clean_date("Ming dynasty (1368–1644), c. 1590s", engine)
        assert date["date_start"] == 1590
        assert date["date_end"] == 1599

    # Parentheses
    def test_parentheses_2(self):
        date = clean_date("blablabla (lilili)", engine)
        assert date["date_start"] == ""
        assert date["date_end"] == ""

    # Parentheses
    def test_parentheses_3(self):
        date = clean_date("blablabla (1790-1810)", engine)
        assert date["date_start"] == 1790
        assert date["date_end"] == 1810

    # Parentheses
    def test_parentheses_4(self):
        date = clean_date("18th century (1790-1810)", engine)
        assert date["date_start"] == 1701
        assert date["date_end"] == 1800

    # Parentheses
    def test_parentheses_5(self):
        date = clean_date("Eastern Zhou dynasty, Warring States period (480–221 B.C.), c. 3rd century B.C.", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -201

    # Parentheses
    def test_parentheses_6(self):
        date = clean_date("Jin dynasty (1115–1234), 12th/13th century", engine)
        assert date["date_start"] == 1101
        assert date["date_end"] == 1300

    # Parentheses
    def test_parentheses_7(self):
        date = clean_date("Meiji period (1868–1912), late 19th century", engine)
        assert date["date_start"] == 1867
        assert date["date_end"] == 1900

    # Parentheses
    def test_parentheses_8(self):
        date = clean_date("1954 (reproduced 1983)", engine)
        assert date["date_start"] == 1954
        assert date["date_end"] == 1954
        
    # Parentheses
    def test_multiple_parentheses(self):
        date = clean_date("Roman period (30 B.C.– 641 A.D.)/Arab period (641–969), 6th/8th century", engine)
        assert date["date_start"] == 501
        assert date["date_end"] == 800

    # Parentheses crochet
    def test_parentheses_crochet(self):
        date = clean_date("ca. 1833–34 [Tenpō 4–5]", engine)
        assert date["date_start"] == 1833
        assert date["date_end"] == 1834


class TestFirstLast(object):

    # First and last feature test
    def test_first_last_1(self):
        date = clean_date("meji era, 1912-5", engine)
        assert date["date_start"] == 1912
        assert date["date_end"] == 1915

    # First and last feature test
    def test_first_last_2(self):
        date = clean_date("meji era, 1912-taisho 5", engine)
        assert date["date_start"] == 1912
        assert date["date_end"] == 1912

    # First and last feature test
    def test_first_last_3(self):
        date = clean_date("meji era, 1912 meiji 45-taisho 5", engine)
        assert date["date_start"] == 1912
        assert date["date_end"] == 1912

    # First and last feature test
    def test_first_last_4(self):
        date = clean_date("meji era, 1912 meiji 45-5", engine)
        assert date["date_start"] == 1912
        assert date["date_end"] == 1912

    # test roman number
    def test_roman_number(self):
        date = clean_date("bronze age period V 900 bc-700 bc", engine)
        assert date["date_start"] == -900
        assert date["date_end"] == -700

    # test roman number
    def test_roman_number_2(self):
        date = clean_date("bronze age V 900 bc-700 bc", engine)
        assert date["date_start"] == -900
        assert date["date_end"] == -700

    # test formatted date with spaces
    def test_formatted_date_with_spaces(self):
        date = clean_date("ca 1973 - 08 - 11", engine)
        assert date["date_start"] == 1973
        assert date["date_end"] == 1973

    # test formatted date with spaces
    def test_formatted_date_with_spaces_2(self):
        date = clean_date("1860s, 1877 - 07 - 04 through 1890 - 07 - 03", engine)
        assert date["date_start"] == 1877
        assert date["date_end"] == 1890

    # test formatted date with MM/YY
    def test_formatted_date_mmyy_format(self):
        date = clean_date("12/99", engine)
        assert date["date_start"] == 1999
        assert date["date_end"] == 1999

    # test long string
    def test_long_string(self):
        date = clean_date("bronze age britain 2500-800 bc, late bronze age ireland 1200-c600 bc, bronze age britain "
                          "2500-800 bc", engine)
        assert date["date_start"] == -2500
        assert date["date_end"] == -800

    # test noise century
    def test_noise_century(self):
        date = clean_date("noise century 20th century", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000

    # test noise century 2
    def test_noise_century_2(self):
        date = clean_date("lalala century lslsls century 16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1600
        
    # test keyword century
    def test_keyword_century(self):
        date = clean_date("mid bronze age-19th century", engine)
        assert date["date_start"] == 1801
        assert date["date_end"] == 1900

    # test keyword century
    def test_keyword_century_2(self):
        date = clean_date("bronze age mid-19th century", engine)
        assert date["date_start"] == 1834
        assert date["date_end"] == 1867


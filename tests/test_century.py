import sys
import os
from db_connection import get_engine
from DateCleaning.DateCleaning import clean_date

engine = get_engine()

class TestBasicCentury(object):
    # Basic century
    def test_basic_century(self):
        date = clean_date("16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1600

    # Basic century bc
    def test_basic_century_bc(self):
        date = clean_date("16th century bc", engine)
        assert date["date_start"] == -1600
        assert date["date_end"] == -1501

    # Basic century period
    def test_basic_century_period(self):
        date = clean_date("16th century - 19th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic century period bc
    def test_basic_century_period_bc(self):
        date = clean_date("19th century bc - 16th century bc", engine)
        assert date["date_start"] == -1900
        assert date["date_end"] == -1501

    # Basic roman period
    def test_basic_roman_period(self):
        date = clean_date("XVI - XIX", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic roman period without dash
    def test_basic_roman_period_without_dash(self):
        date = clean_date("XVI XIX", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic roman period without dash ad
    def test_basic_roman_period_without_dash_ad(self):
        date = clean_date("XVI XIX ad", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic roman period without dash bc
    def test_basic_roman_period_without_dash_bc(self):
        date = clean_date("XVI XIX bc", engine)
        assert date["date_start"] == -1900
        assert date["date_end"] == -1501

    # Basic roman period lowercase
    def test_basic_roman_period_lowercase(self):
        date = clean_date("xx century", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000

    # Basic roman period without dash
    def test_basic_mixed_period_without_dash(self):
        date = clean_date("XVI 19th Century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic century without dash
    def test_basic_century_period_without_dash(self):
        date = clean_date("16th century 19th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1900

    # Basic century without dash
    def test_basic_century_period_without_dash_bc(self):
        date = clean_date("19th century bc 16th century bc", engine)
        assert date["date_start"] == -1900
        assert date["date_end"] == -1501

    # Basic roman numbers
    def test_basic_roman_numbers(self):
        date = clean_date("XX", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 2000

    # Basic roman numbers 2
    def test_basic_roman_numbers_2(self):
        date = clean_date("I", engine)
        assert date["date_start"] == 1
        assert date["date_end"] == 100


class TestMediumCentury(object):
    # Missing century
    def test_missing_century(self):
        date = clean_date("14th-early 15th century", engine)
        assert date["date_start"] == 1301
        assert date["date_end"] == 1434

    # Missing century 2
    def test_missing_century_2(self):
        date = clean_date("late 19th–early 20th century", engine)
        assert date["date_start"] == 1867
        assert date["date_end"] == 1934

    # Missing century
    def test_missing_century_3(self):
        date = clean_date("14th", engine)
        assert date["date_start"] == 1301
        assert date["date_end"] == 1400

    # Missing century
    def test_missing_century_4(self):
        date = clean_date("14th C.", engine)
        assert date["date_start"] == 1301
        assert date["date_end"] == 1400

    # Missing century
    def test_missing_century_5(self):
        date = clean_date("15th-14th century BC", engine)
        assert date["date_start"] == -1500
        assert date["date_end"] == -1301

    # Splitted century early
    def test_splitted_century_early(self):
        date = clean_date("early 16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1534

    # Splitted century early
    def test_splitted_century_mid(self):
        date = clean_date("mid 16th century", engine)
        assert date["date_start"] == 1534
        assert date["date_end"] == 1567

    # Splitted century late
    def test_splitted_century_late(self):
        date = clean_date("late 16th century", engine)
        assert date["date_start"] == 1567
        assert date["date_end"] == 1600

    # Splitted century first half
    def test_splitted_century_first_half(self):
        date = clean_date("first half 16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1550

    # Splitted century second half
    def test_splitted_century_second_half(self):
        date = clean_date("second half 16th century", engine)
        assert date["date_start"] == 1550
        assert date["date_end"] == 1600

    # Splitted century last half
    def test_splitted_century_last_half(self):
        date = clean_date("last half 16th century", engine)
        assert date["date_start"] == 1550
        assert date["date_end"] == 1600

    # Splitted century first third
    def test_splitted_century_first_third(self):
        date = clean_date("first third 16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1534

    # Splitted century second third
    def test_splitted_century_second_third(self):
        date = clean_date("second third 16th century", engine)
        assert date["date_start"] == 1534
        assert date["date_end"] == 1567

    # Splitted century third third
    def test_splitted_century_third_third(self):
        date = clean_date("third third 16th century", engine)
        assert date["date_start"] == 1567
        assert date["date_end"] == 1600

    # Splitted century first quarter
    def test_splitted_century_first_quarter(self):
        date = clean_date("first quarter 16th century", engine)
        assert date["date_start"] == 1501
        assert date["date_end"] == 1525

    # Splitted century second quarter
    def test_splitted_century_second_quarter(self):
        date = clean_date("second quarter 16th century", engine)
        assert date["date_start"] == 1525
        assert date["date_end"] == 1550

    # Splitted century third quarter
    def test_splitted_century_third_quarter(self):
        date = clean_date("third quarter 16th century", engine)
        assert date["date_start"] == 1550
        assert date["date_end"] == 1575

    # Splitted century fourth quarter
    def test_splitted_century_fourth_quarter(self):
        date = clean_date("fourth quarter 16th century", engine)
        assert date["date_start"] == 1575
        assert date["date_end"] == 1600

    # Turn of the century
    def test_turn_century(self):
        date = clean_date("the turn of the 19 and 20 centuries", engine)
        assert date["date_start"] == 1890
        assert date["date_end"] == 1910

    # Turn of the century_2
    def test_turn_century_2(self):
        date = clean_date("the turn of the 20 century", engine)
        assert date["date_start"] == 1890
        assert date["date_end"] == 1910

    # Turn of the century_3
    def test_turn_century_3(self):
        date = clean_date("the turn of the 20th century", engine)
        assert date["date_start"] == 1890
        assert date["date_end"] == 1910

    # Turn of the century bc
    def test_turn_century_bc(self):
        date = clean_date("the turn of the 3 century bc", engine)
        assert date["date_start"] == -310
        assert date["date_end"] == -290

    # Test multiple century
    def test_multiple_century(self):
        date = clean_date("4th or 5th century B.C.", engine)
        assert date["date_start"] == -500
        assert date["date_end"] == -301

    # Test multiple century
    def test_multiple_century_wrong_order(self):
        date = clean_date("5th - 6th Century BC", engine)
        assert date["date_start"] == -600
        assert date["date_end"] == -401
        
    # Test multiple century
    def test_multiple_century_2(self):
        date = clean_date("3rd/2nd century BCE", engine)
        assert date["date_start"] == -300
        assert date["date_end"] == -101

    # Test multiple century
    def test_multiple_century_ordinal(self):
        date = clean_date("Ca. first century BC to third century AD", engine)
        assert date["date_start"] == -100
        assert date["date_end"] == 300

    # Test multiple century
    def test_missing_century_without_dash(self):
        date = clean_date("late 18th or early 19th century", engine)
        assert date["date_start"] == 1767
        assert date["date_end"] == 1834

    # Test multiple century
    def test_missing_century_multiple_dash(self):
        date = clean_date("blade early–mid 14th century, mounting late 18th–early 19th century", engine)
        assert date["date_start"] == 1334
        assert date["date_end"] == 1834

    # Test bogus century
    def test_bogus_century(self):
        date = clean_date("c. early 15th century", engine)
        assert date["date_start"] == 1401
        assert date["date_end"] == 1434

    # Test century cen.
    def test_cen(self):
        date = clean_date("15th cen.", engine)
        assert date["date_start"] == 1401
        assert date["date_end"] == 1500

    # Test century cen.
    def test_century_then_year(self):
        date = clean_date("Late Shang dynasty, 13th century–1046 B.C.", engine)
        assert date["date_start"] == -1300
        assert date["date_end"] == -1046
        
    # Test century cen.
    def test_century_bogus_keywords_first(self):
        date = clean_date("Late Period–Ptolemaic (7th to 1st centuries BCE)", engine)
        assert date["date_start"] == -700
        assert date["date_end"] == -1

    # Test medium century
    def test_new_medium_century(self):
        date = clean_date("late 8th–early 7th century B.C.", engine)
        assert date["date_start"] == -734
        assert date["date_end"] == -667

    # Test multiple parts
    def test_multiple_parts(self):
        date = clean_date("Early mid 20th century", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 1967

    # Test multiple parts
    def test_multiple_parts_2(self):
        date = clean_date("Early/mid–20th century", engine)
        assert date["date_start"] == 1901
        assert date["date_end"] == 1967

    # Test year century
    def test_year_century(self):
        date = clean_date("18 - 19th century", engine)
        assert date["date_start"] == 1701
        assert date["date_end"] == 1900

    # Test year century
    def test_year_century_2(self):
        date = clean_date("19th century, 7 - 22", engine)
        assert date["date_start"] == 1801
        assert date["date_end"] == 1900

    # Test century ordinal
    def test_century_ordinal(self):
        date = clean_date("late nineteenth century early twentieth century", engine)
        assert date["date_start"] == 1867
        assert date["date_end"] == 1934

    # Test century ordinal
    def test_century_ordinal_2(self):
        date = clean_date("late nineteenth early twentieth century", engine)
        assert date["date_start"] == 1867
        assert date["date_end"] == 1934

    # Test multiple centuries
    def test_multiple_centuries(self):
        date = clean_date("16th century bronze age 17th century-18th century", engine)
        assert date["date_start"] == 1601
        assert date["date_end"] == 1800

    # Test multiple centuries
    def test_multiple_centuries_2(self):
        date = clean_date("16th century 17th century-18th century", engine)
        assert date["date_start"] == 1601
        assert date["date_end"] == 1800

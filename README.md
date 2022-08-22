![Build Status](https://github.com/LongRunGrowth/DateCleaning/workflows/DateCleaning/badge.svg)

# DateCleaning package

Datecleaning parses date strings with various formats and outputs a clean python dictionary with the date's metadata. The package is defined by two functions:
* `clean_date`: cleans an individual date in the format of a string (type `str`).
* `clean_fill_df`: cleans multiple dates in the format of a DataFrame (type `pandas.DataFrame` or `pandas.Series`).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install DateCleaning.

```bash
pip3 install git+https://github.com/aabushnell/date-cleaning-package.git
```

If your system fails to install python-Levenshtein the first time, download the .whl file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein that matches your operating
system and python version. Install python-Levenshtein using the .whl file

```bash
pip3 install filepath\python-Levenshtein_filename.whl
```

Now you should be able to successfully install DateCleaning.

## Code Examples

```python
>>> from DateCleaning.DateCleaning import clean_date, clean_fill_df
>>> import pandas as pd
>>>
>>> date="01/01/1995"
>>> cleaned_date = clean_date(date)
>>> print(cleaned_date)
{'date_start': 1995, 'date_end': 1995, 'date_english': '01/01/1995', 'date_original': '01/01/1995', 'date_original_lang': 'en'}
>>> print(cleaned_date["date_start"])
1995
>>> print(cleaned_date["date_end"])
1995
>>> date = "Early Han Dynasty"
>>> cleaned_date = clean_date(date)
>>> print(cleaned_date)
{'date_start': -205.0, 'date_end': -63.0, 'date_english': 'Early Han Dynasty', 'date_original': 'Early Han Dynasty', 'date_original_lang': 'en'}
>>>
>>> date_series = pd.Series(["17th century", "1789.1799"]))
>>> df = pd.DataFrame({"str": ["byzantine empire", "ottoman empire"], "co": ["GR", "TR"]})
>>> cleaned_df = clean_fill_df(df)
Cleaning dates:   0%|                                                                 | 0/2 [00:00<?, ?it/s]
Cleaning dates:  50%|█████████████████████████████████                                | 1/2 [00:00<00:00,  3.71it/s]
Cleaning dates: 100%|████████████████████████████████████████████████████████████████ | 2/2 [00:00<00:00,  4.03it/s]
0.6739811897277832 seconds
>>> print(cleaned_df)
               date country_code  date_start ... date_flags    chrono_date_match  chrono_date_match_score
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
chrono_date_match          byzantine; GR,TR,CY
chrono_date_match_score                    1.0
Name: 0, dtype: object
```

## 1. Input

The input needs to be a pandas.Series or pandas.DataFrame for the function `clean_fill_df` (or type str for `clean_date`) containing date strings. Date strings can contain a year, a century, a millennium or a literal period (like `bronze age`). Date strings can also contain multiple elements (i.e. indicating a time period) separated by a dash (`-`), like `1789-1799`.

## 2. Workflow

The workflow is detailled in the repo's Wiki. The next paragraphs will sum up the process through which each string goes through.

The program works with unique input strings. Every string first goes through a preprocessing step that splits period according to dash (`-`) characters, formats and cleans useless words that may alter the end result.

Next, the program parses each individual string to find either (in that order) a year, a century or a millennium. If any of these elements is found in the string, the program parses the rest of the string or the next string parts for an additional time element. Hence, if the input string `1789 99` or `1789-1799`, the program first detects `1789` before parsing the rest of the string for an additional year. The exact behavior is detailed in the Wiki.

If no clear date is found in aforementionned process, the program queries the IDAI Chronontology API to find a date with the original date string and outputs the result if the string matching procedure renders a satisfactory score.

## 3. Output

The program outputs a pandas.DataFrame that contains time information for each input string. The variables in the output DataFrame are the following:

* `date`: the original date string.
* `date_start`: start year of the date string.
* `date_end`: end year of the date string.
* `date_english`: cleaned date string in English.
* `date_original`: the original date string.
* `date_original_lang`: language code of the original date string.
* `date_flags`: the flags assigned to the date string. 
* `chrono_date_match`: the string matched in the Chronontology API. 
* `chrono_date_match_score`: the score of the string matching algorithm with the original string. 

## 4. Cleaning

The DateCleaning package may output wrong dates (the flag FF is a strong indicator that there date output contains an issue). The research team has implemented one method to clean wrongly mapped dates:

* `Manual Assignation`: the program queries information from a local database containing manually mapped date (added by the research team), that directly maps a date string to a time period if there is an exact string match between the original string and the entry in the database. 
* `Synonyms`: the program queries a table of equivalencies before continuing the rest of the script. Example: "Capture of the Bastille"  -> "French Revolution". 
* `Validated Dates`: The program queries this table first. These skip the rest of the code and provide the correct date at once. It can take into account the `country_code`.  

## 5. Periodo dataset
We also uploaded the periodo dataset to postgres. We use that table in the dateapp and in case we have a response from chronontology that has a perfect score match. For "middle kingdom", for example, we have several results for "middle kingdom egypt", so we decided to get the greatest possible interval between the perfect matches. For "middle kingdom" we have the following possibilities (-2039,-1639), (-1800,-1639), (-2000,-1600). We decided to use: (-2039, -1600) 

## 5. TODO
Update the read.me file

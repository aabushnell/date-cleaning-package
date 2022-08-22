import pandas as pd

countries_csv = pd.read_csv("countries.csv", keep_default_na=False)
def get_country_code(country_name):
    country_name = str(country_name)
    row = countries_csv[countries_csv["country"]==country_name]
    if len(row) > 0:
        return row["code"].iloc[0]
    return None


def get_list_of_codes(string_list):
    """
    string_list: list of country names: "israel, syria, turkey"
    return list_of_codes: list like "IL, SY, IR, TR"
    """
    list_of_codes = ""
    for country_string in string_list.split("|"):
        country_string = country_string.strip()
        country_code = get_country_code(country_string)
        if country_code:
            list_of_codes = list_of_codes + country_code + ","
    return list_of_codes[0:(len(list_of_codes)-1)]


def load_periodo(connection):
    con = connection

    df = pd.read_csv("periodo-dataset.csv")
    df = df[["period", "label", "spatial_coverage", "start", "stop", "source", "publication_year"]]
    df = df.rename(columns={"period": "periodo_id", "spatial_coverage": "country_list",
                            "start": "date_start", "stop": "date_end"})
    df = df.fillna('')
    df["periodo_id"] = df["periodo_id"].str.replace("http://n2t.net/ark:/99152/", "")
    df["country_list"] = df["country_list"].apply(get_list_of_codes)
    df["date_end"] = df["date_end"].replace(r'^\s*$', 2022, regex=True)

    df.to_sql('tl_date_periodo', con=con, if_exists='append', index=False)
    print("finished tl_date_periodo")
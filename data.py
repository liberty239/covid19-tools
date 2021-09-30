#!/bin/python3
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from io import StringIO
import json

def fetch_weekly_deaths(code):
    url = "https://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/demo_r_mwk_ts?unit=NR&precision=1&sex=T&geo={}&sinceTimePeriod=1900W01".format(code)
    resp = requests.get(url)
    data = resp.json()

    ret = {"ts": [], "value": []}
    for week, index in data["dimension"]["time"]["category"]["index"].items():
        try:
            if str(index) in data["value"]:
                ts = datetime.strptime(week + '-1', "%YW%W-%w")
                ret["ts"].append(ts)
                ret["value"].append(data["value"][str(index)])
        except ValueError:
            pass
    return pd.DataFrame.from_dict(ret).set_index("ts")


def fetch_covid_deaths(region):
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    resp = requests.get(url)
    df = pd.read_csv(StringIO(resp.text))
    df = df.loc[df["Country/Region"] == region]
    df = df.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"], var_name="Date", value_name="Value")
    return pd.DataFrame({
        "ts": pd.to_datetime(df['Date'], format="%m/%d/%y"), 
        "value": df["Value"].diff()
    }).set_index("ts")


def fetch_vaccinations(region):
    url = "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv"
    resp = requests.get(url)
    df = pd.read_csv(StringIO(resp.text))
    df = df.loc[df["Country_Region"] == region]
    df = df.loc[df["Province_State"] != df["Province_State"]]
    return pd.DataFrame({
        "ts": pd.to_datetime(df['Date'], format="%Y-%m-%d"), 
        "partially": df["People_partially_vaccinated"].diff(),
        "fully": df["People_fully_vaccinated"].diff(),
    }).set_index("ts")


def main():
    df = fetch_weekly_deaths("PL")
    df = df[datetime(2020,1,1):datetime(2023,1,1)]

    df2 = fetch_covid_deaths("Poland")
    df2 = df2.resample('1W-Mon').sum()

    df3 = fetch_vaccinations("Poland")
    df3 = df3.resample('1W-Mon').sum()

    ax = df.plot()
    df2.plot(ax=ax)
    plt.show()

    # df3.to_json('df3.json', orient='split', date_format="iso", index=True)
    df3.plot()
    plt.show()

    print(df3["fully"].sum())


if __name__ == "__main__":
    main()

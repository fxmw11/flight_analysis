import json
import time
import pandas as pd
import subprocess
from datamodel import json_dump


def query_flightdata_by_airport(airport_icao):
    print(f"Getting flight data for {airport_icao}")
    auth = ""
    now = int(time.time())
    lastweek = now - 60 * 60 * 24 * 7 # one week ago
    cmd = f'curl -s "https://{auth}opensky-network.org/api/flights/arrival?airport={airport_icao}&begin={lastweek}&end={now}" | python -m json.tool > data/arrivals/{airport_icao}.json'
    #print(subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout[:-1].decode('utf-8'))
    print(cmd)


def parse_airports():
    # load data and prepare it for processing
    df_l = pd.read_csv("data/large_airports_europe.csv", sep="\t", comment='#')
    df_m = pd.read_csv("data/medium_airports_europe.csv", sep="\t", comment='#')
    df_airports = pd.concat([df_l, df_m])
    df_airports.columns = ["ICAO", "IATA", "Name", "Municipality", "Country", "Type"] # need to explicitely name columns, otherwise pandas does stupid things (converts column names to _1, _2, ...)
    df_airports.ICAO = df_airports.ICAO.str.strip()
    df_airports.Type.fillna("Large airport", inplace=True)

    # add position data to airports
    df_positions = pd.read_csv("data/GlobalAirportDatabase.txt", sep=":")
    df_positions = df_positions[['ICAO', 'LatDecimal', 'LongDecimal']]
    df_airports = df_airports.merge(df_positions, on='ICAO', validate="one_to_one")

    # filter some invalid airports
    df_airports = df_airports.query("not IATA.isnull().values") # https://stackoverflow.com/questions/51878316/pandas-python-series-objects-are-mutable-thus-they-cannot-be-hashed-in-query-me/51878559#51878559
    df_airports = df_airports.query("LatDecimal != 0.0")
    df_airports = df_airports.query("ICAO != 'UHMD'")
    df_airports = df_airports.query("ICAO != 'UWPP'")
    df_airports = df_airports.query("ICAO != 'UIAA'")
    df_airports = df_airports.query("ICAO != 'UMHA'")

    # export airport data to json and clean it
    df_airports = df_airports.set_index(keys="ICAO", drop=False)
    dict = df_airports.to_dict(orient="index")
    data = json.dumps(dict, sort_keys=True, indent=4, default=json_dump)
    data = data.replace("\'", "\\\'").replace("\"", "\\\"")
    data = f"var airport_data = `{data}`" # drop json in a js-variable for easier local testing
    with open('data_clean/airports.json', "w") as file:
        file.write(data)

    # export airport data to csv
    with open('data_clean/airports.csv', "w") as file:
        file.write("id,name,lat,lon\n")
        for row in df_airports.itertuples(index=False):
            file.write(f"{row.ICAO},{row.Name.replace(',', ' -').strip()},{row.LatDecimal},{row.LongDecimal}\n")

    # df_airports.to_json("data_clean/airports.json", orient="index", force_ascii=False, indent=4)
    # with open('data_clean/airports.json', 'r', encoding='utf-8') as file:
    #    content = file.read()
    # content = content.replace("\'", "\\\'")
    # content = content.replace("\"", "\\\"")
    # content = f"var airport_data = `{content}`"
    # with open('data_clean/airports.json', 'w', encoding='utf-8') as file:
    #     file.write(content)

    return df_airports

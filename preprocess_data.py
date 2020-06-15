import os
import subprocess
import time
import math
import json
import pandas as pd
from tqdm import tqdm

def query_aircraft(icao24):
    print(f"Getting aircraft data for flight {icao24}")
    auth = ""
    now = int(time.time())
    lastweek = now - 60 * 60 * 24 * 7 # one week ago
    cmd = f'curl -s "https://{auth}opensky-network.org/api/flights/aircraft?icao24={icao24}&begin={lastweek}&end={now}" | python -m json.tool > data/{icao24}.json'
    #print(subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout[:-1].decode('utf-8'))
    print(cmd)

def query_airport(airport_icao):
    print(f"Getting flight data for {airport_icao}")
    auth = ""
    now = int(time.time())
    lastweek = now - 60 * 60 * 24 * 7 # one week ago
    cmd = f'curl -s "https://{auth}opensky-network.org/api/flights/arrival?airport={airport_icao}&begin={lastweek}&end={now}" | python -m json.tool > data/arrivals/{airport_icao}.json'
    #print(subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout[:-1].decode('utf-8'))
    print(cmd)

def dict2file(dict, file_name, var_name):
    data = json.dumps(dict, sort_keys=True, indent=4)
    data = f"var {var_name} = `{data}`" # drop json in a js-variable for easier local testing
    with open(file_name, "w") as file:
        file.write(data)

class Dict2Level:

    def __init__(self):
        self.dict = {}

    def sort_keys(self, a, b):
        if type(a) != str or type(b) != str:
            return [None, None]
        return sorted([a, b])

    def add(self, a, b, value=1):
        a, b = self.sort_keys(a, b)
        if a is not None:
            if a in self.dict.keys():
                if b in self.dict[a].keys():
                    self.dict[a][b] += value
                else:
                    self.dict[a][b] = value
            else:
                self.dict[a] = {b: value}

    def get_dict(self):
        return self.dict

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
    data = json.dumps(dict, sort_keys=True, indent=4)
    data = data.replace("\'", "\\\'").replace("\"", "\\\"")
    data = f"var airport_data = `{data}`" # drop json in a js-variable for easier local testing
    with open('data_clean/airports.json', "w") as file:
        file.write(data)

    # df_airports.to_json("data_clean/airports.json", orient="index", force_ascii=False, indent=4)
    # with open('data_clean/airports.json', 'r', encoding='utf-8') as file:
    #    content = file.read()
    # content = content.replace("\'", "\\\'")
    # content = content.replace("\"", "\\\"")
    # content = f"var airport_data = `{content}`"
    # with open('data_clean/airports.json', 'w', encoding='utf-8') as file:
    #     file.write(content)

    return df_airports

def query_arrivals(df_airports):
    flights = Dict2Level()
    # query/parse airport arrivals from opensky network
    for row in df_airports.itertuples():
        if row.IATA:
            if not os.path.exists(f"data/arrivals/{row.ICAO}.json"):
                query_airport(row.ICAO)

            # load flight data
            print(f"Parsing arrivals data for {row.ICAO}")
            with open(f"data/arrivals/{row.ICAO}.json", "r") as file:
                data = file.read()
            if data: # sometimes the file is totally empty
                df_arrivals = pd.read_json(data, orient='records')
                for arr in df_arrivals.itertuples():
                    flights.add(arr.estDepartureAirport, arr.estArrivalAirport)
            else:
                pass
    dict2file(dict=flights.get_dict(), file_name="data_clean/flights.json", var_name="flights_data")

def parse_flight_data(file_src, name):
    print(f"Parsing flight data for {name}")

    # load flight data
    df_flights = pd.read_csv(file_src, sep=",")
    df_flights = df_flights.groupby(by=['origin', 'destination']).count()[['icao24']]#.reset_index()
    #data = df_flights.to_dict(orient='index')
    #df_flights = df_flights.set_index(keys="origin", drop=True)
    #tmp = df_flights.apply(lambda df: {df.name[1]: df.xs('icao24')}, axis=1)

    flights = Dict2Level()
    for origin in tqdm(df_flights.index.get_level_values(0).unique()):
        for destination in df_flights.xs(origin).index:
            value = int(df_flights.xs(origin).xs(destination).xs('icao24')) # need to convert to python-int (numpy-int64 is not JSON serializable)
            flights.add(origin, destination, value=value)

    dict2file(dict=flights.get_dict(), file_name=f'data_clean/{name}.json', var_name=f"{name}_data")

df_airports = parse_airports()
query_arrivals(df_airports)
parse_flight_data("data_covid_19/flightlist_20200101_20200131.csv", "flights_jan")
parse_flight_data("data_covid_19/flightlist_20200201_20200229.csv", "flights_feb")
parse_flight_data("data_covid_19/flightlist_20200301_20200331.csv", "flights_mar")
parse_flight_data("data_covid_19/flightlist_20200401_20200430.csv", "flights_apr")
parse_flight_data("data_covid_19/flightlist_20200501_20200531.csv", "flights_may")

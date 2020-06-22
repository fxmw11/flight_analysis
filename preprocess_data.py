import os
import pickle
import pandas as pd
from tqdm import tqdm
from aircrafts.aircrafts import parse_aircrafts, merge_mtow
from airports import parse_airports, query_flightdata_by_airport
from datamodel import Dict2Level, DictItem, dict2json, dict2csv


def query_arrivals(df_aircrafts, df_airports):
    print(f"Parsing flight data for last week queried from opensky-network.org")
    existing_ids = list(df_airports.ICAO)

    if not os.path.exists('data/flight_dict.pkl'):
        # query/parse airport arrivals from opensky network
        flights = Dict2Level()
        for row in df_airports.itertuples():
            if row.ICAO in existing_ids: # consider flights only if dest is given (is in europe, IATA given)
                if not os.path.exists(f"data/arrivals/{row.ICAO}.json"):
                    query_flightdata_by_airport(row.ICAO)

                # load flight data
                print(f"Parsing arrivals data for {row.ICAO}")
                with open(f"data/arrivals/{row.ICAO}.json", "r") as file:
                    data = file.read()
                if data: # sometimes the file is totally empty
                    df_arrivals = pd.read_json(data, orient='records')
                    for arr in df_arrivals.itertuples():
                        # consider flights only if origin is given too, avoid roundtrips
                        if arr.estDepartureAirport in existing_ids and arr.estDepartureAirport != arr.estArrivalAirport:
                            flights.add(arr.estDepartureAirport, arr.estArrivalAirport, {str(arr.icao24): 1})
                else:
                    pass
        with open('data/flight_dict.pkl', 'wb') as f:
            pickle.dump(flights, f)
    else:
        with open('data/flight_dict.pkl', 'rb') as f:
            flights = pickle.load(f)

    flights = merge_mtow(flights, df_aircrafts)

    dict2csv(dict=flights.get_dict(), file_name=f'data_clean/flights.csv', quantity='count')
    dict2csv(dict=flights.get_dict(), file_name=f'data_clean/flights_mtow.csv', quantity='mtow')
    dict2json(dict=flights.get_dict(), file_name="data_clean/flights.json", var_name="flights_data")


def parse_flight_data(file_src, name, df_aircrafts, df_airports):
    print(f"Parsing flight data for {name}")
    existing_ids = list(df_airports.ICAO)

    # load flight data
    if not os.path.exists(f'data/{name}_dict.pkl'):
        df_flights = pd.read_csv(file_src, sep=",")
        df_flights['count'] = 1
        df_flights = df_flights.groupby(by=['origin', 'destination', 'icao24']).sum()['count']
        #data = df_flights.to_dict(orient='index')
        #df_flights = df_flights.set_index(keys="origin", drop=True)
        #tmp = df_flights.apply(lambda df: {df.name[1]: df.xs('icao24')}, axis=1)

        flights = Dict2Level()
        for (origin, dst, icao24), count in tqdm(df_flights.items(), desc='Parsing flights for each airport'):
            # consider flights only if locations are given (=> its in europe, IATA given), avoid roundtrips
            if origin in existing_ids and dst in existing_ids and origin != dst:
                flights.add(origin, dst, values={icao24: count}, cnt=count)

        with open(f'data/{name}_dict.pkl', 'wb') as f:
            pickle.dump(flights, f)
    else:
        with open(f'data/{name}_dict.pkl', 'rb') as f:
            flights = pickle.load(f)

    flights = merge_mtow(flights, df_aircrafts)

    dict2csv(dict=flights.get_dict(), file_name=f'data_clean/{name}.csv', quantity='count')
    dict2csv(dict=flights.get_dict(), file_name=f'data_clean/{name}_mtow.csv', quantity='mtow')
    dict2json(dict=flights.get_dict(), file_name=f'data_clean/{name}.json', var_name=f"{name}_data")

df_airports = parse_airports()
df_aircrafts = parse_aircrafts(update=False)
query_arrivals(df_aircrafts, df_airports)
parse_flight_data("data_covid_19/flightlist_20200101_20200131.csv", "flights_jan", df_aircrafts, df_airports)
parse_flight_data("data_covid_19/flightlist_20200201_20200229.csv", "flights_feb", df_aircrafts, df_airports)
parse_flight_data("data_covid_19/flightlist_20200301_20200331.csv", "flights_mar", df_aircrafts, df_airports)
parse_flight_data("data_covid_19/flightlist_20200401_20200430.csv", "flights_apr", df_aircrafts, df_airports)
parse_flight_data("data_covid_19/flightlist_20200501_20200531.csv", "flights_may", df_aircrafts, df_airports)

import pandas as pd
import subprocess
import requests
import pickle
from tqdm import tqdm
import time
from datetime import datetime
import json
import os
import re
from aircrafts.dataframe_preparation import add_alternatives, drop_irrelevant_data
from datamodel import DictItem, json_dump


def query_aircraft_data(icao24):
    print(f"Getting aircraft data for flight {icao24}")
    auth = ""
    now = int(time.time())
    lastweek = now - 60 * 60 * 24 * 7 # one week ago
    cmd = f'curl -s "https://{auth}opensky-network.org/api/flights/aircraft?icao24={icao24}&begin={lastweek}&end={now}" | python -m json.tool > data/{icao24}.json'
    #print(subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout[:-1].decode('utf-8'))
    print(cmd)


def parse_aircrafts(update=False):

    if not os.path.exists('data/aircrafts.pkl'):
        update = True
        start = datetime.now()
        df_aircrafts_tech = load_aircrafts_tech()
        df_aircrafts = load_aircrafts()
        if 'MTOW' not in list(df_aircrafts):
            df_aircrafts['MTOW'] = ''
        print(f"Loading aircraft csv: {datetime.now() - start}")

        # import matplotlib.pyplot as plt
        # n, bins, patches = plt.hist(df_aircrafts_tech['MTOW'], [x*1000 for x in range(50)])
        # print(n)
        # print(bins)
        # plt.show()

        # should have no effect
        df_aircrafts_tech = df_aircrafts_tech.drop_duplicates(keep='first', ignore_index=True)
        df_aircrafts = df_aircrafts.drop_duplicates(keep='first', ignore_index=True)
    else:
        with open('data/aircrafts.pkl', 'rb') as f:
            data = pickle.load(f)
            df_aircrafts_tech, df_aircrafts = data

    if update:
        df_aircrafts = df_aircrafts.set_index(keys="icao24", drop=False)

        # drop manufacturers of small/light weight aircrafts or where we do not have any mtow data
        print(f"Dropping irrelevant data...", end=' ')
        start = datetime.now()
        df_aircrafts = drop_irrelevant_data(df_aircrafts, get_irrelevant_manu())
        print(f"{datetime.now() - start}")
        print(f"{len(df_aircrafts)} aircrafts left")

        # zero_mtow = df_aircrafts[df_aircrafts['MTOW'] == '']
        # grouped = zero_mtow.groupby(['manufacturername', 'model'])
        # count = grouped.count()
        # ranked = count.sort_values(by=['icao24'])

        # add some alternative (short) names for manufacturers and models in order to improve matching
        print(f"Adding alternative/short names...", end=' ')
        start = datetime.now()
        df_aircrafts = add_alternatives(df_aircrafts, 'manufacturername', 'model')
        df_aircrafts_tech = add_alternatives(df_aircrafts_tech, 'Manufacturer', 'Model')
        print(f"{datetime.now() - start}")

        print(f"Matching...", end=' ')
        def match(row):
            manu_val = [row.manufacturername, row.manu_alt]
            manu_val = [v for v in manu_val if v != '']
            model_val = [row.model, row.model_alt]
            model_val = [v for v in model_val if v != '']
            matches = df_aircrafts_tech.query("(Manufacturer in @manu_val or manu_alt in @manu_val) and (Model in @model_val or model_alt in @model_val)")
            if len(matches.index) == 1:
                row['MTOW'] = matches.iloc[0]['MTOW']
            elif len(matches.index) > 1:
                row['MTOW'] = matches.sort_values('MTOW').iloc[len(matches)//2]['MTOW']
            return row

        tqdm.pandas()
        df_aircrafts.loc[df_aircrafts['MTOW'] == ''] = df_aircrafts.loc[df_aircrafts['MTOW'] == ''].progress_apply(match, axis=1)
        print(f"Got {len(df_aircrafts.loc[df_aircrafts['MTOW'] != ''])} aircrafts with MTOW data")

        with open('data/aircrafts.pkl', 'wb') as f:
            pickle.dump([df_aircrafts_tech, df_aircrafts], f)

    return df_aircrafts


def merge_mtow(flight_dict, df_aircrafts, update_map=False):
    df_aircrafts_tech = load_aircrafts_tech()
    df_aircrafts_icao_map = load_aircrafts_icao24_map()
    existing_mtow = list(df_aircrafts.query("MTOW != ''").index)
    df_aircrafts_icao_map = df_aircrafts_icao_map.query("ModeS not in @existing_mtow")

    all_icao24 = set()
    no_mapping = set()
    no_mtow = set()
    for origin, dests in tqdm(flight_dict.get_dict().items(), desc='Merging MTOW data into flights for each airport'):
        for dst, data in dests.items():
            for icao24, n in data.values.items():
                # convert number in DictItem and add mtow
                item = DictItem({}, n)
                if icao24 in df_aircrafts.index and df_aircrafts.loc[icao24]['MTOW'] != '':
                    item.values['mtow'] = int(df_aircrafts.loc[icao24]['MTOW'] * 0.453592) # convert from lbs to kg
                else:
                    map = df_aircrafts_icao_map.query("ModeS == @icao24")
                    if update_map and len(map.index) == 0:
                        df_aircrafts_icao_map = update_icao24_map(df_aircrafts_icao_map, icao24)
                        map = df_aircrafts_icao_map.query("ModeS == @icao24")
                    if len(map.index):
                        matches = df_aircrafts_tech.query(f"`ICAO Code` == '{map['ICAOTypeCode'].iloc[0]}'")
                        if len(matches.index):
                            item.values['mtow'] = matches.sort_values('MTOW').iloc[len(matches)//2]['MTOW']
                        else:
                            item.values['mtow'] = 0
                            no_mtow.add((map['ICAOTypeCode'].iloc[0], icao24))
                    else:
                        item.values['mtow'] = 0
                        no_mapping.add(icao24)
                all_icao24.add(icao24)
                data.values[icao24] = item
            mtow = 0
            for icao24, aircraft_data in data.values.items():
                mtow += aircraft_data.values['mtow'] * aircraft_data.count
            data.values['mtow'] = mtow

    print(f"MTOW not available for {len(no_mtow) + len(no_mapping)}/{len(all_icao24)} aircrafts (from that {len(no_mapping)} ids seem invalid)")
    if update_map:
        with open('data/icao24_map.pkl', 'wb') as f:
            pickle.dump(df_aircrafts_icao_map, f)

    return flight_dict


def load_aircrafts_icao24_map():
    if not os.path.exists('data/icao24_map.pkl'):
        df = pd.read_csv("data/modes.tsv", sep="\t")
        df = df[['ModeS', 'ICAOTypeCode']]
        df['ModeS'] = df['ModeS'].str.lower()
        if os.path.exists('data/icao24_map.csv'):
            df_ext = pd.read_csv("data/icao24_map.csv", sep=",", comment='#')
            df = pd.concat([df, df_ext])
        with open('data/icao24_map.pkl', 'wb') as f:
            pickle.dump(df, f)
    else:
        with open('data/icao24_map.pkl', 'rb') as f:
            df = pickle.load(f)
    return df


def update_icao24_map(df, icao24):
    url = f"https://www.radarbox.com/data/mode-s/{icao24.upper()}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'}
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        html = result.content.decode()
        matches = re.search('/data/aircraft-models/([0-9A-Z]{4})', html)
        if matches:
            print(f"Updating icao24 to type mapping: {icao24} -> {matches.group(1)}")
            df = df.append({'ModeS': icao24, 'ICAOTypeCode': matches.group(1)}, ignore_index=True)
    return df


def load_aircrafts():
    df = pd.read_csv("data/aircraftDatabase.csv", sep=",")
    df = df[['icao24', 'manufacturername', 'model']]
    df = df.query("manufacturername != ''")
    df = df.query("not manufacturername.isnull().values")
    df = df.query("model != ''")
    df = df.query("not model.isnull().values")
    #dump_uniques(df['manufacturername'], 'dump.txt')
    return df


def load_aircrafts_tech():
    df = pd.read_excel("data/FAA-Aircraft-Char-Database-v2-201810.xlsx", sheet_name="Aircraft Database")
    df = df[['Manufacturer', 'Model', 'MTOW', 'ICAO Code']]
    df.loc[df.query("Manufacturer.str.contains('Airbus') and Model.str.startswith('A320neo')", engine='python').index, 'ICAO Code'] = 'A20N'
    df.loc[df.query("Manufacturer.str.contains('Airbus') and Model.str.startswith('A321neo')", engine='python').index, 'ICAO Code'] = 'A21N'
    df.loc[df.query("Manufacturer == 'Boeing' and Model == '777-200LR'").index, 'ICAO Code'] = 'B77L'
    df.loc[df.query("`ICAO Code` == 'CRJ7'").index, 'MTOW'] = 75000 # https://en.wikipedia.org/wiki/Bombardier_CRJ700_series
    df.loc[df.query("`ICAO Code` == 'CRJ9'").index, 'MTOW'] = 84500 # https://en.wikipedia.org/wiki/Bombardier_CRJ700_series
    df.loc[df.query("`ICAO Code` == 'CRJX'").index, 'MTOW'] = 91800 # https://en.wikipedia.org/wiki/Bombardier_CRJ700_series
    df.loc[df.query("Manufacturer.str.contains('Embraer') and Model.str.contains('Legacy 600', case=False)", engine='python').index, 'MTOW'] = 49604 # https://en.wikipedia.org/wiki/Embraer_Legacy_600
    df.loc[df.query("Manufacturer.str.contains('Embraer') and Model.str.contains('Legacy 650', case=False)", engine='python').index, 'MTOW'] = 53572 # https://en.wikipedia.org/wiki/Embraer_Legacy_600
    df.loc[df.query("Manufacturer.str.contains('Ilyushin') and Model.str.contains('IL-96', case=False)", engine='python').index, 'MTOW'] = 551000 # https://en.wikipedia.org/wiki/Ilyushin_Il-96
    df.loc[df.query("Model == 'Sukhoi Superjet 100'").index, 'ICAO Code'] = 'SU95' # https://en.wikipedia.org/wiki/Sukhoi_Superjet_100
    df.loc[df.query("Model == 'Sukhoi Superjet 100'").index, 'MTOW'] = 101150 # https://en.wikipedia.org/wiki/Sukhoi_Superjet_100
    df = df.query("MTOW != 'tbd'")
    #dump_uniques(df['Manufacturer'], 'dump_tech.txt')
    return df


def get_irrelevant_manu():
    df = pd.read_excel("data/FAA-Aircraft-Char-Database-v2-201810.xlsx", sheet_name="Aircraft Database")
    df = df[['Manufacturer', 'Model', 'MTOW']]
    df.loc[df['MTOW'] == 'tbd', 'MTOW'] = 0
    manu_mtow = df.groupby(by=['Manufacturer'])['MTOW'].sum()
    irrelevant_manu = manu_mtow[manu_mtow == 0]
    return list(irrelevant_manu.index)


def query_all_combinations(df, columns, values):
    values = [v for v in values if v != '']
    query = ''
    for col in columns:
        query += f"{col} in @values or "
    return df.query(query[:-4])


def dump_uniques(data, file):
    dump = data.unique()
    dump.sort()
    with open(file, 'w') as f:
        for v in list(dump):
            f.write(v + '\n')

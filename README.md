# Visualization of air traffic in europe
https://fxmw11.github.io/flight_analysis/

This repo contains a visualization of air traffic in europe based on flight data from https://opensky-network.org/.
Data displayed is from the [Covid-19 dataset](https://opensky-network.org/datasets/covid-19/) an from the week before creation of this repo.
Further data can be obtained from [CERN's Zenodo repository](https://zenodo.org/record/3901482).
The visualization is not limited to this data as arbitrary data can be requested using the [OpenSky-API](https://opensky-network.org/apidoc/rest.html) (see [preprocess_data.py](./blob/master/preprocess_data.py))

To recreate the json-files for the visualization execute
```bash
bash download.sh
python preprocess_data.py
```

For now only the **number of flights** and the accumulated **maximum takeoff weight (MTOW)** of all flights between selected airports is visualized.
Selected airports are the *large* and *medium* classified airports at [airportcodes.io](https://airportcodes.io/en/all-airports/?filters[continent]=EU)
for which have an IATA code assigned (mainly aiports frequently used for traveling) and position data is contained in the [GlobalAirportDatabase](http://www.partow.net/miscellaneous/airportdatabase/index.html).
MTOW is only considered according to the aircraft's entry in the [Aircraft Characteristics Database](https://www.faa.gov/airports/engineering/aircraft_char_database/) which is set for the majority of all major civil aircrafts (status: 2018).
For light (hobby) aircrafts MTOW data is usually missing in the database but these would not contribute to the overall traffic significantly anyway.
Also most military flights are not included in the statistics as military airports often have no IATA code.
In order to improve merging the data from *OpenSky* and the *Aircraft Characteristics Database* also information about aircrafts from [FlightAirMap](https://real.flightairmap.com/) and [Radarbox](https://www.radarbox.com) is used.

Future ideas:
- [x] visualize domestic flights
- [ ] visualize short distance flights
- [x] visualize the intercity-railways in europe
- [ ] compare railways and heavily used flight routes (time, distance, ecological footprint, ...)
- [x] join airplane data (weight) to get estimates of number of passengers travelling/ecological footprint

## Other Visualizations

### Number of flights
- [Flowmap Covid-19 January](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_jan.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 February](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_feb.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 March](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_mar.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 April](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_apr.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 May](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_may.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap 24.4. - 1.5.2020](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)

### Accumulated MTOW
- [Flowmap Covid-19 January](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_jan_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 February](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_feb_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 March](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_mar_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 April](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_apr_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap Covid-19 May](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_may_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)
- [Flowmap 24.4. - 1.5.2020](https://flowmap.blue/from-url?flows=https://fxmw11.github.io/flight_analysis/data_clean/flights_mtow.csv&locations=https://fxmw11.github.io/flight_analysis/data_clean/airports.csv)

# Visualization of air traffic in europe
https://fxmw11.github.io/flight_analysis/

This repo contains a visualization of air traffic in europe based on flight data from https://opensky-network.org/.
Data displayed is from the [Covid-19 dataset](https://opensky-network.org/datasets/covid-19/) an from the week before creation of this repo.
The visualization is not limited to this data as arbitrary data can be requested using the [OpenSky-API](https://opensky-network.org/apidoc/rest.html) (see [preprocess_data.py](./blob/master/preprocess_data.py))

To recreate the json-files for the visualization execute
```bash
bash download.sh
python preprocess_data.py
```

For now only the **number of flights** between selected airports is visualized. Selected airports are the *large* and *medium* classified airports at [airportcodes.io](https://airportcodes.io/en/all-airports/?filters[continent]=EU)
for which position data is contained in the [GlobalAirportDatabase](http://www.partow.net/miscellaneous/airportdatabase/index.html).

Future ideas:
- [x] visualize domestic flights
- [ ] visualize short distance flights
- [x] visualize the intercity-railways in europe
- [ ] compare railways and heavily used flight routes (time, distance, ecological footprint, ...)
- [ ] join airplane data to get estimates of number of passengers travelling/ecological footprint

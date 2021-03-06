DIR=data
mkdir $DIR
pushd $DIR
curl http://www.partow.net/downloads/GlobalAirportDatabase.zip > GlobalAirportDatabase.zip
unzip GlobalAirportDatabase.zip
rm GlobalAirportDatabase.zip
curl https://opensky-network.org/datasets/metadata/aircraftDatabase.csv > aircraftDatabase.csv
curl https://opensky-network.org/datasets/metadata/doc8643AircraftTypes.csv > doc8643AircraftTypes.csv
curl https://opensky-network.org/datasets/metadata/doc8643Manufacturers.csv > doc8643Manufacturers.csv
curl https://www.faa.gov/airports/engineering/aircraft_char_database/media/FAA-Aircraft-Char-Database-v2-201810.xlsx > FAA-Aircraft-Char-Database-v2-201810.xlsx
curl https://data.flightairmap.com/data/modes.tsv.gz > modes.tsv.gz
gunzip modes.tsv.gz
rm modes.tsv.gz
popd


DIR=data_covid_19
mkdir $DIR
pushd $DIR
curl https://opensky-network.org/datasets/covid-19/LICENSE.txt > LICENSE.txt
curl https://opensky-network.org/datasets/covid-19/readme.md > readme.md
curl https://opensky-network.org/datasets/covid-19/flightlist_20200101_20200131.csv.gz > flightlist_20200101_20200131.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200201_20200229.csv.gz > flightlist_20200201_20200229.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200301_20200331.csv.gz > flightlist_20200301_20200331.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200401_20200430.csv.gz > flightlist_20200401_20200430.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200501_20200531.csv.gz > flightlist_20200501_20200531.csv.gz
gunzip flightlist_20200101_20200131.csv.gz
gunzip flightlist_20200201_20200229.csv.gz
gunzip flightlist_20200301_20200331.csv.gz
gunzip flightlist_20200401_20200430.csv.gz
gunzip flightlist_20200501_20200531.csv.gz
rm flightlist_20200101_20200131.csv.gz
rm flightlist_20200201_20200229.csv.gz
rm flightlist_20200301_20200331.csv.gz
rm flightlist_20200401_20200430.csv.gz
rm flightlist_20200501_20200531.csv.gz
popd

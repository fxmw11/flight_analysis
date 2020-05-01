DIR=data
mkdir $DIR
pushd $DIR
curl http://www.partow.net/downloads/GlobalAirportDatabase.zip > GlobalAirportDatabase.zip
unzip GlobalAirportDatabase.zip
rm GlobalAirportDatabase.zip
curl https://opensky-network.org/datasets/metadata/aircraftDatabase.csv > aircraftDatabase.csv
curl https://opensky-network.org/datasets/metadata/doc8643AircraftTypes.csv > doc8643AircraftTypes.csv
curl https://opensky-network.org/datasets/metadata/doc8643Manufacturers.csv > doc8643Manufacturers.csv
popd


DIR=data_covid_19
mkdir $DIR
pushd $DIR
curl https://opensky-network.org/datasets/covid-19/LICENSE.txt > LICENSE.txt
curl https://opensky-network.org/datasets/covid-19/readme.md > readme.md
curl https://opensky-network.org/datasets/covid-19/flightlist_20200101_20200131.csv.gz > flightlist_20200101_20200131.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200201_20200229.csv.gz > flightlist_20200201_20200229.csv.gz
curl https://opensky-network.org/datasets/covid-19/flightlist_20200301_20200331.csv.gz > flightlist_20200301_20200331.csv.gz
gunzip flightlist_20200101_20200131.csv.gz
gunzip flightlist_20200201_20200229.csv.gz
gunzip flightlist_20200301_20200331.csv.gz
rm flightlist_20200101_20200131.csv.gz
rm flightlist_20200201_20200229.csv.gz
rm flightlist_20200301_20200331.csv.gz
popd

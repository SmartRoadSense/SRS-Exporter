# SmartRoadSense data exporter

This simple Python script is thought to make it easier to export SRS data for debugging and analysis purposes.

The script runs a query against the _raw_ or the _aggregated_ database. As the _raw_ database is concerned, by default it queries the _single_data_ table, but using the `--old` (or `-O`) option it can be set to use the _single_data_old_ table instead.
The _current_ table is queried by using the `--aggregate` flag.

It requires the following environmental variables set:
1. __SRS_EXPORTER_HOST__ (default is _127.0.0.1_)
2. __SRS_EXPORTER_DB_RAW__ (default is _srs_raw_db_)
3. __SRS_EXPORTER_DB_AGG__ (default is _srs_agg_db_)
4. __SRS_EXPORTER_USER__ (default is _postgres_)
5. __SRS_EXPORTER_PASS__ (default is _postgres_)
6. __SRS_EXPORTER_PORT__ (default is _5432_)
 
The script's usage is quite straight forward:

```
Usage:
  exporter.py [OPTIONS]

Usage examples:
  exporter.py -l 10
  exporter.py --longitude 12.92290593 --latitude 43.74830223 -d 1000
  exporter.py -T 56237 --meta
  exporter.py -a -l 10
  exporter.py -O -A 2018-04-01 --before 2018-04-02

Options:
  -d --distance <int>      Distance in meters used for range queries
                           (Default:100).
  -t --latitude <float>    Latitude used for range queries.
  -g --longitude <float>   Longitude used for range queries.
  -A --after <datetime>    Selected rows have to be created after this
                           specific datetime value.
  -B --before <datetime>   Selected rows have to be created before this
                           specific datetime value.
  -T --track <track_id>    Track id of selected rows.
  -m --meta                If specified rows will be exported with their
                           track's metadata (NOTE: cause a JOIN).
  -o --output <filename>   Filename/path where results have to be written.
  -a --aggregate           If specified data will be queried from
                           the "current" table in the aggregate database.
  -O --Old                 If specified data will be queried from
                           the "single_data_old" table in the raw database.
  -l --limit <int>         Limit If specified data will be queried from
                           the "single_data_old" table in the raw database.
  --debug                  Print debug information.
  -h --help                Print this help.
```




## Within Docker
Please consider using this script within a Docker container (see: Docker [smartroadsense/dataexporter](https://hub.docker.com/r/smartroadsense/dataexporter/) image)

When used within the Docker container linked above please note that the script will be in the `/tmp/` directory  and should be executed in this way in order to output results in the shared `/data` docker volume:
```
$ python exporter.py -o /data/data.csv [OTHER OPTIONS]
```

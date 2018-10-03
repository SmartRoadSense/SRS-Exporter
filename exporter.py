# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 17:31:00 2018

@author: Saverio Delpriori <saverio.delpriori@uniurb.it>
"""

import csv
import psycopg2
import getopt
import sys
from os import environ
import debug


def setup_config():
    # default connection variables
    conn_vars = {
        "host_raw": "localhost",
        "host_agg": "localhost",
        "raw_db": "srs_raw_db",
        "agg_db": "srs_agg_db",
        "user": "postgres",
        "password": "postgres",
    }

    # setup connection variables if set by user
    if "SRS_EXPORTER_RAW_HOST" in environ:
        conn_vars['host_raw'] = environ.get('SRS_EXPORTER_RAW_HOST')
    if "SRS_EXPORTER_AGG_HOST" in environ:
        conn_vars['host_agg'] = environ.get('SRS_EXPORTER_AGG_HOST')
    if "SRS_EXPORTER_DB_RAW" in environ:
        conn_vars['raw_db'] = environ.get('SRS_EXPORTER_DB_RAW')
    if "SRS_EXPORTER_DB_AGG" in environ:
        conn_vars['agg_db'] = environ.get('SRS_EXPORTER_DB_AGG')
    if "SRS_EXPORTER_USER" in environ:
        conn_vars['user'] = environ.get('SRS_EXPORTER_USER')
    if "SRS_EXPORTER_PASS" in environ:
        conn_vars['password'] = environ.get('SRS_EXPORTER_PASS')

    return conn_vars


def usage():
    print("""
SRS data exporter from single_data (default), single_data_old or current 
(aggregate db) table. It can perform queries based on geographical distance,
creation intervals and track_id.
    
Usage:
  {0} [OPTIONS]

Usage examples:
  {0} -l 10 
  {0} --longitude 12.92290593 --latitude 43.74830223 -d 1000 
  {0} -T 56237 --meta 
  {0} -a -l 10
  {0} -O -A 2018-04-01 --before 2018-04-02

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
  
""".format(sys.argv[0]))


class Query:
    def __init__(self):
        self.output = 'data.csv'
        self.after_date = None
        self.before_date = None
        self.track_id = None
        self.distance = 100
        self.limit = None
        self.p_lat = None
        self.p_lng = None
        self.track_metadata = False
        self.raw_db = True
        self.new_data = True

    def is_raw(self):
        return self.raw_db

    def is_agg(self):
        return not self.raw_db

    def is_distance_query(self):
        return True if self.p_lat and self.p_lng else False

    def is_date_query(self):
        return True if self.after_date or self.before_date else False

    def is_track_query(self):
        return self.track_id is not None

    def check(self):
        if self.is_agg() and (self.is_track_query() or self.track_metadata or self.__is_join_query()):
            return False

        return True

    def __get_raw_table_name(self):
        return "single_data" if self.new_data else "single_data_old"

    def get_table(self):
        if self.is_agg():
            return "current"
        else:
            return self.__get_raw_table_name()

    def __is_join_query(self):
        return self.track_metadata

    def __get_limit(self):
        if self.limit:
            return " LIMIT {0}".format(self.limit)

        return ""

    def __get_join(self):
        if self.__is_join_query():
            table_str = "single_data" if self.new_data else "single_data_old"
            return "LEFT JOIN track ON {0}.track_id = track.track_id".format(table_str)

        return ""

    def __get_selection_fields(self):
        select = ["ppe"]

        if self.is_raw():
            select += ["position",
                       "st_x(position) as longitude",
                       "st_y(position) as latitude",
                       "{0}.track_id".format(self.__get_raw_table_name()),
                       "{0}.date".format(self.__get_raw_table_name())]
        else:
            select += ["the_geom",
                       "st_x(the_geom) as longitude",
                       "st_y(the_geom) as latitude",
                       "updated_at"]

        if self.__is_join_query():
            select.append("track.metadata")

        return select

    def __get_where_clauses(self):
        clauses = ["TRUE"]

        if self.is_distance_query():
            point_str = "ST_MakePoint({0}, {1}, 4326)".format(self.p_lng, self.p_lat)
            position_str = 'position' if self.is_raw() else 'the_geom'
            distance_clause = "St_Distance_Sphere({0}, {1}) < {2}".format(position_str, point_str, self.distance)
            clauses.append(distance_clause)

        if self.is_track_query():
            track_clause = "{0}.track_id = {1}".format(self.__get_raw_table_name(), self.track_id)
            clauses.append(track_clause)

        if self.after_date:
            date_str = "{0}.date".format(self.__get_raw_table_name()) if self.is_raw() else "updated_at"
            after_date_str = "{0} > '{1}'".format(date_str, self.after_date)
            clauses.append(after_date_str)

        if self.before_date:
            date_str = "{0}.date".format(self.__get_raw_table_name()) if self.is_raw() else "updated_at"
            before_date_str = "{0} < '{1}'".format(date_str, self.before_date)
            clauses.append(before_date_str)

        return clauses

    def get_query(self):

        select_fields = ", ".join(self.__get_selection_fields())
        where_clauses = " AND ".join(self.__get_where_clauses())
        query_str = "SELECT {0} FROM {1} {2} WHERE {3} {4}" \
            .format(select_fields, self.get_table(), self.__get_join(), where_clauses, self.__get_limit())

        debug.print_debug(query_str)

        return query_str


def check_variables():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:t:g:A:B:T:mao:Ol:h",
                                   ["distance=", "latitude=", "longitude=",
                                    "after=", "before=", "track=", "meta",
                                    "aggregate", "output=", "old", "limit=", "help", "debug"])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    q = Query()

    for o, a in opts:

        if o in ("-d", "--distance"):
            # distance below {variable} in meters
            q.distance = a

        elif o in ("-t", "--latitude"):
            q.p_lat = a

        elif o in ("-g", "--longitude"):
            q.p_lng = a

        elif o in ("-A", "--after"):
            q.after_date = a

        elif o in ("-B", "--before"):
            q.before_date = a

        elif o in ("-T", "--track"):
            q.track_id = a

        elif o in ("-m", "--meta"):
            q.track_metadata = True

        elif o in ("-a", "--aggregate"):
            q.raw_db = False

        elif o in ("-o", "--output"):
            q.output = a

        elif o in ("-O", "--old"):
            q.new_data = False

        elif o in ("-l", "--limit"):
            q.limit = a

        elif o in "--debug":
            debug.debug = True

        elif o in ("-h", "--help"):
            usage()
            sys.exit()

    if not q.check():
        print("Wrong parameters!")
        usage()
        sys.exit(2)

    return q


def get_data(connection_data, query):
    conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'" \
        .format(connection_data['host_raw'] if query.is_raw() else connection_data['host_agg'],
                (connection_data['raw_db'] if query.is_raw() else connection_data['agg_db']),
                connection_data['user'],
                connection_data['password'])

    # print the connection string we will use to connect
    debug.print_debug("Connecting to database\n	-> {0}".format([conn_string]))

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # HERE IS THE IMPORTANT PART, by specifying a name for the cursor
    # psycopg2 creates a server-side cursor, which prevents all of the
    # records from being downloaded at once from the server.
    cursor = conn.cursor('cursor_unique_name')

    cursor.execute(query.get_query())
    return cursor


def export_data(cursor, filename='test.csv'):
    # Because cursor objects are iterable we can just call 'for - in' on
    # the cursor object and the cursor will automatically advance itself
    # each iteration.
    # This loop should run 1000 times, assuming there are at least 1000
    # records in 'my_table'
    with open(filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        row_count = 0
        for row in cursor:

            if row_count == 0:
                debug.print_debug("{0} results found".format(cursor.rowcount))
                col_names = [desc[0] for desc in cursor.description]
                csv_writer.writerow(col_names)

            row_count += 1
            csv_writer.writerow(row)

        if row_count == 0:
            print("No results found!".format(cursor.rowcount))
        else:
            print("{0} results exported to {1}".format(row_count, filename))


def main():
    conn_vars = setup_config()
    query = check_variables()
    cursor = get_data(conn_vars, query)
    export_data(cursor, filename=query.output)


if __name__ == "__main__":
    main()

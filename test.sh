#!/usr/bin/env bash

function assert {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "Error with $1" >&2
        exit;
    else
        echo "Test passed"
    fi
    return $status
}

function assert_not {
    "$@"
    local status=$?
    if [ $status -eq 0 ]; then
        echo "Error with $1" >&2
        exit;
    else
        echo "Test passed"
    fi
    return $status
}


# Weekly raw data table
echo -e "\n\n\npy.exe exporter.py -l 10\n"
assert py.exe exporter.py -l 10
echo -e "\n\n\npy.exe exporter.py -d 10\n"
assert py.exe exporter.py -d 10
echo -e "\n\n\npy.exe exporter.py -l 10 --debug \n"
assert py.exe exporter.py -l 10 --debug
echo -e "\n\n\npy.exe exporter.py -l 10 -d \n"
assert_not py.exe exporter.py -l 10 -d
echo -e "\n\n\npy.exe exporter.py -g 12.92290593\n"
assert py.exe exporter.py -g 12.92290593
echo -e "\n\n\npy.exe exporter.py --longitude 12.92290593 --latitude 43.74830223\n"
assert py.exe exporter.py --longitude 12.92290593 --latitude 43.74830223
echo -e "\n\n\npy.exe exporter.py -l 10 -m -o test.csv\n"
assert py.exe exporter.py -l 10 -m -o test.csv
echo -e "\n\n\npy.exe exporter.py -T 16 -m -o test_track.csv\n"
assert py.exe exporter.py -T 16 -m -o test_track.csv

echo -e "\n\n\npy.exe exporter.py -T 16 -m -o test_track.csv -c\n"
assert py.exe exporter.py -T 16 -m -o test_track.csv -c
echo -e "\n\n\npy.exe exporter.py -T 16 -m -o test_track.csv -c -w \"track.metadata::json->>'sdk' = 'LollipopMr1'\"\n"
assert py.exe exporter.py -T 16 -m -o test_track.csv -w "track.metadata::json->>'sdk' = 'LollipopMr1'"
echo -e "\n\n\npy.exe exporter.py -T 16 -m -o test_track.csv -c -s \"track.metadata::json->>'deviceManufacturer' as manufacturer\"\n"
assert py.exe exporter.py -T 16 -m -o test_track.csv -s "track.metadata::json->>'deviceManufacturer' as manufacturer"

echo -e "\n\n\npy.exe exporter.py -T 16 -m -o test_track.csv -c -s \"track.metadata::json->>'deviceManufacturer' as manufacturer\" -w \"track.metadata::json->>'sdk' = 'LollipopMr1'\" --query\n"
assert py.exe exporter.py -T 16 -m -o test_track.csv -s "track.metadata::json->>'deviceManufacturer' as manufacturer" -w "track.metadata::json->>'sdk' = 'LollipopMr1'" --query


# Old raw data table
echo -e "\n\n\npy.exe exporter.py -O -A 2018-04-01 --before 2018-04-02\n"
assert py.exe exporter.py -O -A 2018-04-01 --before 2018-04-02

# Aggregate table
echo -e "\n\n\npy.exe exporter.py -a -m\n"
assert_not py.exe exporter.py -a -m
echo -e "\n\n\npy.exe exporter.py -a -t 16\n"
assert_not py.exe exporter.py -a -T 16
echo -e "\n\n\npy.exe exporter.py -a -l 10\n"
assert py.exe exporter.py -a -l 10
echo -e "\n\n\npy.exe exporter.py --longitude 12.92290593 --latitude 43.74830223 -d 100 -l 10\n"
assert py.exe exporter.py -a --longitude 12.92290593 --latitude 43.74830223 -d 100 -l 10



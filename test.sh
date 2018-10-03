#!/usr/bin/env bash

 echo -e "\n\n\npy.exe exporter.py -l 10\n"
 py.exe exporter.py -l 10
 echo -e "\n\n\npy.exe exporter.py -d 10\n"
 py.exe exporter.py -d 10
 echo -e "\n\n\npy.exe exporter.py -g 12.92290593\n"
 py.exe exporter.py -g 12.92290593
 echo -e "\n\n\npy.exe exporter.py --longitude 12.92290593 --latitude 43.74830223\n"
 py.exe exporter.py --longitude 12.92290593 --latitude 43.74830223
 echo -e "\n\n\npy.exe exporter.py -l 10 -m -o test.csv\n"
 py.exe exporter.py -l 10 -m -o test.csv
 echo -e "\n\n\npy.exe exporter.py -t 16 -m -o test_track.csv\n"
 py.exe exporter.py -T 16 -m -o test_track.csv

 echo -e "\n\n\npy.exe exporter.py -a -m\n"
 py.exe exporter.py -a -m
 echo -e "\n\n\npy.exe exporter.py -a -t 16\n"
 py.exe exporter.py -a -T 16
 echo -e "\n\n\npy.exe exporter.py -a -l 10\n"
 py.exe exporter.py -a -l 10
 echo -e "\n\n\npy.exe exporter.py --longitude 12.92290593 --latitude 43.74830223 -d 1000 -l 100\n"
 py.exe exporter.py -a --longitude 12.92290593 --latitude 43.74830223 -d 1000 -l 100

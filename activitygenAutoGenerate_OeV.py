#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import csv
import os, sys
from string import digits
import geopy
from geopy import geocoders
import shapefile
import xml.etree.cElementTree as ET
import shapely
from shapely.geometry import Point, LineString
from shapely.ops import transform
from functools import partial
import pyproj
from itertools import groupby
import operator
import lxml.etree as etree

# find row, street-ID is written in
def lookUpLineNumber(lineID):
	zaehler = 0
	for record in records_lin:
		if record[1] == lineID:
			return zaehler
		zaehler += 1
# calculate length of segment for pointID, lineID, point-geometrie, linen-geometrie
def segmentLength(ptID, lineID, geomPT, geomLIN):
	ptShapes = geomPT.shapes()
	linShapes = geomLIN.shapes()
	lineNumber = int(lookUpLineNumber(str(lineID)) or 0)
	line = LineString(linShapes[lineNumber].points)
	point = Point(ptShapes[ptID].points[0][0],ptShapes[ptID].points[0][1])
	partLine = line.project(point)
	part = float(line.project(point))/float(line.length)
	# Geometry transform function based on pyproj.transform (in case length is in degree an not in meters
	project = partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init='EPSG:21781'))
	line2 = transform(project, line)
	return (float(line2.length)*part)

####### path to data ##############	
# go to data dir; read network geometry
os.chdir('HOME')
lin = shapefile.Reader('2_Netzwerk/activityNetwork1WGS.shp')
records_lin = lin.records()
#######

#### Prepare BUS informations
sf_bus = shapefile.Reader('3_Statistikdaten/r_bern_oev_takt_network')
fields_bus = sf_bus.fields
records_bus = sf_bus.records()
aBusStationDict = {}
aBusLineDict = {}
dictBusStation = {}
listBusStation = []
dictBusLine = {}
listBusLine = []
dictBusLineFrequencies = {}
listBusLineFrequencies = []
dictBusLineStation = {}
listBusLineStation = []
listStreet = []
listSchool = []
zaehler = 0

## BusStation
for record in records_bus:
	sL = segmentLength(zaehler, record[8], sf_bus, lin)
	aBusStationDict.update(dict([(record[4], [record[8], sL])]))
	zaehler += 1

#busStation-dict for statistics-XML-file
for k in aBusStationDict:
	listBusStation.append({'id': str(k), 'edge': str(aBusStationDict[k][0]), 'pos': str(aBusStationDict[k][1])}) 

## BusLine
for key, group in groupby(sorted(records_bus,key=operator.itemgetter(10,1,6)), lambda x: (x[1])): 
    stopsList = []
    freqency = ''
    attrBusLine= ''
    for busstops in group:
        stopsList.append({'refId': str(busstops[4])})
        freqency = {'begin': '1000', 'end': '80000', 'rate': str(int(busstops[3])*60)}
        tripLength = int(busstops[10]/8)
        attrBusLine = {'id': str(key), 'maxTripDuration': str(tripLength)}
    aBusLineDict.update(dict([(key, [attrBusLine, freqency, stopsList])]))
	

### Write statistics-XML-file 
dictBusLineRefStation = {}

## build XML hierarchy
city = ET.Element("city")
streets = ET.SubElement(city, "streets")
schools = ET.SubElement(city, "schools")
busStations = ET.SubElement(city, "busStations")
busLines = ET.SubElement(city, "busLines")

## fill in elements from above
for dict in listStreet:
	streetEdge = ET.SubElement(streets, "street", dict)
for dict in listSchool:
	schoolEdge = ET.SubElement(schools, "school", dict)
for dict in listBusStation:
	busStation = ET.SubElement(busStations, "busStation", dict)

for dictLine in aBusLineDict:
	busLine = ET.SubElement(busLines, "busLine", aBusLineDict[dictLine][0])
	busLineStations = ET.SubElement(busLine, "stations")
	zaehl = 0
	for k in aBusLineDict[dictLine][2]:
		busLineStation = ET.SubElement(busLineStations, "station", aBusLineDict[dictLine][2][zaehl])
		zaehl+=1
	busLineRefStations = ET.SubElement(busLine, "refStations")
	busLineFrequencies = ET.SubElement(busLine, "frequencies")
	busLineFreq = ET.SubElement(busLineFrequencies, "frequency", aBusLineDict[dictLine][1])

tree = ET.ElementTree(city)
tree.write("4_Nachfrage/statfile_auto.xml")
x = etree.parse("4_Nachfrage/statfile_auto.xml")
print etree.tostring(x, pretty_print = True)
prettyTree = etree.tostring(x, pretty_print = True)
f = open('4_Nachfrage/statfile_auto_pretty.xml', 'w')
f.write(prettyTree)
f.close()




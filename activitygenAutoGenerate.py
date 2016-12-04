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
lin = shapefile.Reader('2_Netzwerk/activityNetwork2WGS.shp')
records_lin = lin.records()
######

#### Prepare STREETS data (population and workposition)
# population to variable and create dict out of it
sf_bev = shapefile.Reader('3_Statistikdaten/r_bern_bevoelkerung_toNetwork')
fields_bev = sf_bev.fields
records_bev = sf_bev.records()
aBevDict = {}
for record in records_bev:
	if record[35] in aBevDict: 
		newValue = str(int(aBevDict[record[35]]) + int(record[3])) 
		aBevDict[record[35]] = newValue 
	else:
		aBevDict.update(dict([(record[35], record[3])])) 

# workposition to dict and create dict out of it
sf_unt = shapefile.Reader('3_Statistikdaten/r_bern_unternehmen_toNetwork') 
fields_unt = sf_unt.fields
records_unt = sf_unt.records()
aUntDict = {}
listStreet = []
for record in records_unt:
	if record[28] in aUntDict: 
		newValue = str(int(aUntDict[record[28]]) + int(record[3])) 
		aUntDict[record[28]] = newValue 
	else:
		aUntDict.update(dict([(record[28], record[3])]))

# merge population and workposition in streets-dict
aStreetsDict = {}

for k in aUntDict:
	if k not in aBevDict:
		aStreetsDict.update(dict([(k, [0, aUntDict[k]])]))
	else:
		aStreetsDict.update(dict([(k, [aBevDict[k], aUntDict[k]])]))
for k in aBevDict:
	if k not in aUntDict:
		aStreetsDict.update(dict([(k, [aBevDict[k], 0])]))

# build streets-dict for statistics-XML-file
for k in aStreetsDict:
	listStreet.append({'edge': str(k), 'population': str(aStreetsDict[k][0]), 'workPosition': str(aStreetsDict[k][1])})


#### Prepare SCHOOL	data
# school content to variable and create dict out of it
schoolList = ['3_Statistikdaten/Kindergarten_toNetwork.shp','3_Statistikdaten/Primarschule_toNetwork.shp','3_Statistikdaten/Oberstufe_toNetwork.shp','3_Statistikdaten/Gesamtschule_toNetwork.shp'] 
schoolKind = [32400,46800,5,6]
schoolPrim = [28800,28800,6,12]
schoolOber = [27000,57600,12,16]
schoolGesamt = [28800,28800,6,16]
aSchoolDict = {}
listSchool = []
for schoolType in schoolList:
	sf_school = shapefile.Reader(str(schoolType))
	fields_school = sf_school.fields
	records_school = sf_school.records()
	zaehler = 0
	for record in records_school:
		if record[4] in aSchoolDict: 
			newValue = str(int(aSchoolDict[record[4]][0]) + int(record[2]))
			aSchoolDict[record[4]][0] = newValue
		else:
			sL = segmentLength(zaehler, record[4], sf_school, lin)
			aSchoolDict.update(dict([(record[4], [record[2], sL])]))
		zaehler += 1
	# build school-dict for statistics-XML-file
	for k in aSchoolDict:
		if schoolType == '3_Statistikdaten/Kindergarten_toNetwork.shp':
			listSchool.append({'edge': str(k), 'pos': str(aSchoolDict[k][1]), 'beginAge': str(schoolKind[2]), 'endAge': str(schoolKind[3]), 'capacity': str(aSchoolDict[k][0]), 'opening': str(schoolKind[0]), 'closing': str(schoolKind[1])})
		elif schoolType == '3_Statistikdaten/Primarschule_toNetwork.shp':
			listSchool.append({'edge': str(k), 'pos': str(aSchoolDict[k][1]), 'beginAge': str(schoolPrim[2]), 'endAge': str(schoolPrim[3]), 'capacity': str(aSchoolDict[k][0]), 'opening': str(schoolPrim[0]), 'closing': str(schoolPrim[1])})
		elif schoolType == '3_Statistikdaten/Oberstufe_toNetwork.shp':
			listSchool.append({'edge': str(k), 'pos': str(aSchoolDict[k][1]), 'beginAge': str(schoolOber[2]), 'endAge': str(schoolOber[3]), 'capacity': str(aSchoolDict[k][0]), 'opening': str(schoolOber[0]), 'closing': str(schoolOber[1])})
		elif schoolType == '3_Statistikdaten/Gesamtschule_toNetwork.shp':
			listSchool.append({'edge': str(k), 'pos': str(aSchoolDict[k][1]), 'beginAge': str(schoolGesamt[2]), 'endAge': str(schoolGesamt[3]), 'capacity': str(aSchoolDict[k][0]), 'opening': str(schoolGesamt[0]), 'closing': str(schoolGesamt[1])})		


### Write statistics-XML-file 
dictBusLineRefStation = {}

## build XML hierarchy
city = ET.Element("city")
streets = ET.SubElement(city, "streets")
schools = ET.SubElement(city, "schools")

## fill in elements from above
for dict in listStreet:
	streetEdge = ET.SubElement(streets, "street", dict)
for dict in listSchool:
	schoolEdge = ET.SubElement(schools, "school", dict)

tree = ET.ElementTree(city)
tree.write("4_Nachfrage/statfile_auto.xml")
x = etree.parse("4_Nachfrage/statfile_auto.xml")
print etree.tostring(x, pretty_print = True)
prettyTree = etree.tostring(x, pretty_print = True)
f = open('4_Nachfrage/statfile_auto_pretty.xml', 'w')
f.write(prettyTree)
f.close()

	


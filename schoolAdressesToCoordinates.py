#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script to look for coordinates according to given adresses in school file received from Erzeihungsdirektion Bern
# writes new csv file with coordinates and amount of students

import urllib2
import json
import csv
import os, sys
from string import digits
import geopy
from geopy import geocoders

## function to geocode adresse
def getLatLon(parcity,parstreet):
	g = geopy.geocoders.GoogleV3(api_key='GoogleKey', domain='maps.googleapis.com', scheme='https', client_id=None, secret_key=None, timeout=1, proxies=None)
	location = g.geocode(parcity + '+' + parstreet)
	lat = (location.latitude)
	lon = (location.longitude)
	return [lat,lon]

## directory with school files
os.chdir('PathToSchoolData')
#'Gmde_nurGesamtschule2015.csv','Gmde_nurKindergarten2015.csv','Gmde_nurOberstufe2015.csv','Gmde_nurPrimarschule2015.csv'
schoolList = ['Gmde_nurOberstufe2015.csv']
for gde in schoolList:
	with open(gde, 'rb') as csvfile:
		schoolLine = csv.reader(csvfile, delimiter=',', quotechar='"')
		next(schoolLine)
		i = 0
		## fuer jede Adresse eine Koordinate abfragen 
		for row in schoolLine:
			street = ""
			city = ""
			streetCol = row[9]
			streetName = streetCol.lower()
			street = streetName
			city = row[12].lower()
			if street <> "" and city <> "":
				latlon = []
				latlon = getLatLon(str(city).translate(None, digits).replace(" ", "+").split("/")[0].split("-")[0],str(street).replace(" ", "+").split("/")[0].split("-")[0])
				if latlon <> []:
					## neues CSV file schreiben mit den Koordinaten und den Anzahl Schuelern
					fileToWrite = 'latlon_' + gde
					with open(fileToWrite, 'a') as writefile:
						stringToWriteLong = str(latlon[0]) + ", " + str(latlon[1]) + ", " + city.decode("utf8") + ", " + street.decode("utf8") + ", " + row[13]
						stringToWrite = str(latlon[0]) + ", " + str(latlon[1]) + ", " + row[13] + "\n"
						writefile.write(stringToWrite)  




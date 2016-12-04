#!/usr/bin/python
# -*- coding: utf-8 -*-
# evaluate numbers of entry and exit at bus and train stations. Every agent who travels by bus is projected onto the closest entry and exit station.

import xml.etree.cElementTree as ET
import pyproj
import os, sys
from collections import Counter
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree
from osgeo import ogr
import osgeo.osr as osr
import lxml.etree as etree
import xml.sax
import shapefile
sys.path.append('/Users/pascal/Dropbox/UNIGIS/Master/Programme/sumo/SUMO/tools')
import sumolib

##########################################################
## Parameter to filter the trips
# data directory
os.chdir('HOME')

## tripfile if not given in command line argument 
if len(sys.argv) < 2:
	# main tripfile (argument 1)
	mmTripfile = '4_Nachfrage/mainTripfile.xml'
	# only car tripfile (argument 2)
	carTripfile = '4_Nachfrage/carTripfile.xml'
	## result file if not given in command line argument
	# exit passengers (argument 3)
	resultfile = '8_Auswertung/busStationCount.csv'
else:
	mmTripfile = sys.argv[1]
	carTripfile = sys.argv[2]
	resultfile = sys.argv[3]

## Stations with passenger counts
passengerCountStations = ['8054','16161','4410','7002','7005','7006','8200','4489','16154','4117','4105','7077','7091']
##########################################################

# create dict from tripfile
def tripfileToDict(inputTripfile, chooseListDict, filterType):
	# Open network-plain-edge XML document using SAX parser
	listDictLine = []
	dictLine = {}
	## Create appropriate Handler
	class RouteHandler( xml.sax.ContentHandler ): 
		def __init__(self):
			self.CurrentData = ''
			self.id = ''
			self.type = ''
		### Call when an element starts
		def startElement(self, tag, attributes):
			self.CurrentData = tag
			if tag == 'trip':
				id = attributes['id']
				type = attributes['type']
				depart = attributes['depart']
				departPos = attributes['departPos']
				arrivalPos = attributes['arrivalPos']
				arrivalSpeed = attributes['arrivalSpeed']
				startEdge = attributes['from']
				endEdge = attributes['to'] 
				try:
					viaEdge = attributes['via']
				except:
					viaEdge = ''
				#### filter the desired vehicle type (filterType) and replace it with new vehicle type (replaceType)
				if type == filterType:
					if viaEdge == '':
						listDictLine.append({'id': str(id), 'type': str(type), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'to': str(endEdge)})	
						dictLine.update(dict([(str(id), [str(type), str(depart), str(departPos), str(arrivalPos), str(arrivalSpeed), str(startEdge), str(endEdge)])]))
					else:
						listDictLine.append({'id': str(id), 'type': str(type), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'via': str(viaEdge), 'to': str(endEdge)})
						dictLine.update(dict([(str(id), [str(type), str(depart), str(departPos), str(arrivalPos), str(arrivalSpeed), str(startEdge), str(viaEdge), str(endEdge)])]))
		### (brauchts beim Trip nicht) Call when an elements ends 
		def endElement(self, tag):
			if self.CurrentData == "id": print "hallo! Type:", self.id
			elif self.CurrentData == "type": print "Format:", self.type
		### (brauchts beim Trip nicht) Call when a character is read 
		def characters(self, content):
			if self.CurrentData == "id": self.id = content
			elif self.CurrentData == "type": self.type = content
	if ( __name__ == "__main__"): 
		# create an XMLReader 
		parser = xml.sax.make_parser()
		# turn off namepsaces 
		parser.setFeature(xml.sax.handler.feature_namespaces, 0)
		# override the default ContextHandler 
		Handler = RouteHandler() 
		parser.setContentHandler( Handler )
		parser.parse(inputTripfile)
		if chooseListDict == 'dict':
			return dictLine
		else:
			return listDictLine

def countPassengersPerStation(toFrom):
	if toFrom == 'to':
		rowNr = 5
	else:
		rowNr = 6
	sf_bus = shapefile.Reader('3_Statistikdaten/r_bern_oev_takt_network')
	sf_edges = shapefile.Reader('3_Statistikdaten/edges_toStationsRail')
	records_bus = sf_bus.records()
	records_edges = sf_edges.records()
	aBusStationList = []
	aEdgeStationDict = {}
	aEdgeList = []
	tripToBusStation = {}
	passengerList = []
	tripToBusStationCount = {}
	# compose list of all busstations if no busstation-selection given
	if passengerCountStations == []:
		for record in records_bus:
			aBusStationList.append(record[8])
	# compose bus list if busstation selection given, call edge assigned to station. And every edge only once
	else:
		for record in records_bus:
			if record[4] in passengerCountStations and record[8] not in aBusStationList:
				aBusStationList.append(record[8])
	
	
	# create Dict and List of all edges
	for record in records_edges:
		aEdgeStationDict.update(dict([(record[1], record[6])]))
		if record[6] in passengerCountStations:
			aEdgeList.append(record[1])
	# create dict containing stationID and edgeID pertained to the stationID
	zaehler = 1
	for trips in dictOev:
		if len(dictOev[trips]) == 8 and rowNr == 6:
			if dictOev[trips][rowNr + 1] in aEdgeList:
				tripToBusStation.update(dict([(zaehler, [aEdgeStationDict[dictOev[trips][rowNr + 1]], dictOev[trips][rowNr + 1]])]))
		else:
			if dictOev[trips][rowNr] in aEdgeList:
				tripToBusStation.update(dict([(zaehler, [aEdgeStationDict[dictOev[trips][rowNr]], dictOev[trips][rowNr]])]))
		zaehler+=1
	# create list with all station occurances and count them
	for passenger in tripToBusStation:
		passengerList.append(tripToBusStation[passenger][0])
	tripToBusStationCount = dict(Counter(passengerList))

	return tripToBusStationCount


### Calculate number of agents per station
mmDict = tripfileToDict(mmTripfile, 'dict', 'default')
carDict = tripfileToDict(carTripfile, 'dict', 'default')
dictOev = {}
# dict with all trips not listed in tripfile with bus

numberBusTrips = 0
aCarsList = []
aVehiclesList = []
aDiffList = []
aDiffListTemp = []
passengersPerStationDict = {}
# build list with trip ID containing type of vehicle, from and to edge for the list containing only car trips
for cars in carDict:
	aCarsList.append(cars)
# build list with trip ID containing type of vehicle, from and to edge for the list containing car and bus trips
for vehicles in mmDict:	
	aVehiclesList.append(vehicles)
# diferences between the two lists
aDiffListTemp = set(aCarsList).symmetric_difference(aVehiclesList)
for records in aDiffListTemp:
	try:
		dictOev.update(dict([(records, carDict[records])]))
	except:
		pass


passengersPerStationDictTo = countPassengersPerStation('to')
passengersPerStationDictFrom = countPassengersPerStation('from')
# delete existing files
f = open(resultfile, 'w')
f.close()
# write passenger counts to csv file
with open(resultfile, 'a') as toFile:
	for trips in passengersPerStationDictTo:
		toFile.write(str(trips) + ',' + str(passengersPerStationDictTo[trips]) + ','  + str(passengersPerStationDictFrom[trips]) + '\n')
		
print 'abgeschlossen'
###

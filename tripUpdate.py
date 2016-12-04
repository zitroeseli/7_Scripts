#!/usr/bin/python
# -*- coding: utf-8 -*-
# replace car-trip with bike-trip if bike travel time isn't too long and time loss compared to car isn't too big

import xml.etree.cElementTree as ET
import pyproj
import os, sys
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree
from osgeo import ogr
import osgeo.osr as osr
import lxml.etree as etree
import xml.sax
import shapefile
from shapely.geometry import Point
import shapely
from shapely.ops import transform
from functools import partial
sys.path.append('/home/pascal/shares/Programme/sumo/SUMO/tools')
import sumolib
import random

##########################################################
## parameters
# path to data
os.chdir('HOME')
inTripfile = '4_Nachfrage/mainTripfile2.xml'
outTripfile = '4_Nachfrage/mainTripfileUpdatedBike2.xml'
tempTripfile = '4_Nachfrage/tripfileTemp2.trip.xml'

# maximal distance between start and end edge in m
maxDistance = 5000
# probability of change to bike
p = 0.2
##########################################################

# not in use
def filterTripFile(inputTripfile,outputTripfile,filterType,replaceType):
	# Open network-plain-edge XML document using SAX parser
	listDictLine = []


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
						listDictLine.append({'id': str(id), 'type': str(replaceType), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'to': str(endEdge)})	
					else:
						listDictLine.append({'id': str(id), 'type': str(replaceType), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'via': str(viaEdge), 'to': str(endEdge)})

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
		parser.parse("Trip/mainTripfile.xml")
	
		wRoutes = ET.Element("routes")
		for elements in listDictLine:
			wTrip = ET.SubElement(wRoutes, "trip", elements)
		tree = ET.ElementTree(wRoutes)
		tree.write("Trip/tripfileTemp.trip.xml")
		tempTrip = etree.parse("Trip/tripfileTemp.trip.xml")
		prettyTree = etree.tostring(tempTrip, pretty_print = True)
		f = open('Trip/tripfileTemp.trip.xml', 'w')
		f.write(prettyTree)
		f.close()

# write tripfile to File
def dictToXML(dict):
	wRoutes = ET.Element("routes")
	for elements in dict:
		wTrip = ET.SubElement(wRoutes, "trip", elements)
	tree = ET.ElementTree(wRoutes)
	tree.write(tempTripfile)
	tempTrip = etree.parse(tempTripfile)
	prettyTree = etree.tostring(tempTrip, pretty_print = True)
	f = open(outTripfile, 'w')
	f.write(prettyTree)
	f.close()
	return prettyTree

# create dict from tripfile and replace type
def tripfileToDictReplace(inputTripfile, chooseListDict, replaceList, replaceType):
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
				#### replace the desired vehicle type (filterType) and replace it with new vehicle type (replaceType)
				if id in replaceList:
					if viaEdge == '':
						listDictLine.append({'id': str(id), 'type': str(replaceType), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'to': str(endEdge)})	
						dictLine.update(dict([(str(id), [str(replaceType), str(depart), str(departPos), str(arrivalPos), str(arrivalSpeed), str(startEdge), str(endEdge)])]))
					else:
						listDictLine.append({'id': str(id), 'type': str(type), 'depart': str(depart), 'departPos': str(departPos), 'arrivalPos': str(arrivalPos), 'arrivalSpeed': str(arrivalSpeed), 'from': str(startEdge), 'via': str(viaEdge), 'to': str(endEdge)})
						dictLine.update(dict([(str(id), [str(type), str(depart), str(departPos), str(arrivalPos), str(arrivalSpeed), str(startEdge), str(viaEdge), str(endEdge)])]))
				else:
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

# create dict from vehfile
def vehfileToDict(inputVehfile, chooseListDict):
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
			if tag == 'vehicle':
				id = attributes['id']
				type = attributes['type']
				depart = attributes['depart']
				try:
					arrival = attributes ['arrival']
				except:
					arrival = '' 				
				#### read xml in dict
				if arrival != '':
					listDictLine.append({'id': str(id), 'type': str(type), 'depart': str(depart), 'arrival': str(arrival)})
					dictLine.update(dict([(str(id), [str(type), str(depart), str(arrival)])]))	
		### (not needed for this function) Call when an elements ends 
		def endElement(self, tag):
			if self.CurrentData == "id": print "hallo! Type:", self.id
			elif self.CurrentData == "type": print "Format:", self.type
		### (not needed for this function) Call when a character is read 
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
		parser.parse(inputVehfile)
		if chooseListDict == 'dict':
			return dictLine
		else:
			return listDictLine

# create dict from tripfile
def tripfileToDict(inputTripfile, chooseListDict):
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

# returns the main coordinate of all the edges
def dictCoordEdges():
	sf_network = shapefile.Reader('2_Netzwerk/activityNetworkAllWGS')
	records_network = sf_network.records()
	shapes_network = sf_network.shapes()
	zaehler=0
	networkID = []
	dictLine = {}
	for record in records_network:
		networkID.append(record[1]) 
	for shapes in shapes_network:
		lenShape = len(shapes_network[zaehler].points)
		middleVertex = int(lenShape/2)
		coordShapeMainPoint = shapes_network[zaehler].points[middleVertex]
		dictLine.update(dict([(networkID[zaehler], coordShapeMainPoint)]))				
		zaehler+=1	
	return dictLine

def inDistance():
	sf_network = shapefile.Reader('2_Netzwerk/activityNetworkAllWGS')
	records_network = sf_network.records()
	shapes_network = sf_network.shapes()
	mainTripfileList = tripfileToDict(inTripfile, 'dict')
	tDistance = {}
	# edges and their coordinates
	edgeCoords = dictCoordEdges()
	# define start and end edge of trip
	za=0
	for trips in mainTripfileList:
		if len(mainTripfileList[trips]) == 7:
			tDepart = mainTripfileList[trips][5]
			tArrival = mainTripfileList[trips][6]
		else:
			tDepart = mainTripfileList[trips][5]
			tArrival = mainTripfileList[trips][7]
		if mainTripfileList[trips][0] == 'default':
			# Geometry transform function based on pyproj.transform (in case length is in degree an not in meters
			project = partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init='EPSG:21781'))
			try:
				# make point objects
				coordDepart = transform(project, Point(edgeCoords[tDepart][0], edgeCoords[tDepart][1]))
				coordArrival = transform(project,Point(edgeCoords[tArrival][0], edgeCoords[tArrival][1]))
				# create dict with edgeID as key and vehicle type and distance in m between them as value
				tDistance.update(dict([(trips, [mainTripfileList[trips][0],coordDepart.distance(coordArrival)])]))
				print "en cours" + str(za)
			except:
				print "func"
			za+=1
	return tDistance


dictInDistance = inDistance()
newList = []
for trips in dictInDistance:
	try:
		# if distance between start and end edge not too big and with a certain probability, change vehicle default to bicycle
		if dictInDistance[trips][0] == 'default' and dictInDistance[trips][1] < maxDistance and random.random() <= p:
			newList.append(trips)
		print trips
	except:
		print "dict"
mainTripfileList = tripfileToDictReplace(inTripfile, 'list', newList, 'bicycle')
print dictToXML(mainTripfileList)



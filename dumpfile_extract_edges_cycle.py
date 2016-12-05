#!/usr/bin/python
# -*- coding: utf-8 -*-
# extracts edge traffic data from model where count data are available

import xml.etree.cElementTree as ET
import pyproj

from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree
from osgeo import ogr
import osgeo.osr as osr
import lxml.etree as etree

import xml.sax
import csv

#####################
# sumo export file path
sumoFilepath = 'HOME/6_Simulation/main_sumo_export2_cycle.xml'

# csv file path with number of cars per edge per day 
csvExportpath = 'HOME/8_Auswertung/cycleCount2.csv'

# list which contains edges with reference data
referenceEdge = ['-328944730#0','328944730#0','25678026#3','-25678026#3','-46097076','46097076','-4878030','4878030','188142789','-307351478','167903209#2','196819395','313358788','206511546']
#######################

# Open network-plain-edge XML document using SAX parser
dictEdges = {}
dictAvNumber = {}
dictMessstellen = {}

## Create appropriate Handler
class RouteHandler( xml.sax.ContentHandler ): 
	def __init__(self):
		self.CurrentData = ''
		self.id = ''
		self.type = ''
	### Call when an element starts
	def startElement(self, tag, attributes):
		self.CurrentData = tag
		if tag == 'edge':
			id = attributes['id']
			sampledSeconds = attributes['sampledSeconds']
			departed = attributes['departed']
			arrived = attributes['arrived']
			entered = attributes['entered']
			left = attributes['left']
			laneChangedFrom = attributes['laneChangedFrom']
			laneChangedTo = attributes['laneChangedTo'] 
			try:
				traveltime = attributes['traveltime']
			except:
				traveltime = '0'
			try:
				density = attributes['density']
			except:
				density = '0'
			try:
				occupancy = attributes['occupancy']
			except:
				occupancy = '0'
			try:
				waitingTime = attributes['waitingTime']
			except:
				waitingTime = '0'
			try:
				speed = attributes['speed']
			except:
				speed = '0'
			if id in referenceEdge:
				dictEdges.update(dict([(str(id), str(float(speed)*float(density)*24*3.6))]))
				dictAvNumber.update(dict([(str(id), str(sampledSeconds))]))

	### (brauchts beim Trip nicht) Call when an elements ends 
	def endElement(self, tag):
		if self.CurrentData == "id": print "hallo! Type:", self.id
		elif self.CurrentData == "type": print "Format:", self.type
	### (brauchts beim Trip nicht) Call when a character is read 
	def characters(self, content):
		if self.CurrentData == "id": self.id = content
		elif self.CurrentData == "type": self.type = content
		
if ( __name__ == "__main__"): # create an XMLReader 
	parser = xml.sax.make_parser()
	# turn off namepsaces 
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	# override the default ContextHandler 
	Handler = RouteHandler() 
	parser.setContentHandler( Handler )
	parser.parse(sumoFilepath)

# order station ID and assign edge traffic to reference stations
dictMessstellen.update(dict([(str('AMessstelle'), str('Fahrzeuge pro 24h'))]))
for element in dictEdges:
	# V1 Tiefenaustrasse
	if element in ('-328944730#0','328944730#0'):
		if str('V1') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V1'])
			dictMessstellen['V1'] = newValue
		else:
			dictMessstellen.update(dict([(str('V1'), str(dictEdges[element]))])) 
	# V2 Schwarzengurgstrasse
	if element in ('25678026#3','-25678026#3'):
		if str('V2') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V2'])
			dictMessstellen['V2'] = newValue
		else:
			dictMessstellen.update(dict([(str('V2'), str(dictEdges[element]))])) 
	# V3 Kornhausstrasse
	if element in ('-46097076','46097076'):
		if str('V3') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V3'])
			dictMessstellen['V3'] = newValue
		else:
			dictMessstellen.update(dict([(str('V3'), str(dictEdges[element]))])) 
	# V4 Monbijoustrasse
	if element in ('-4878030','4878030'):
		if str('V4') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V4'])
			dictMessstellen['V4'] = newValue
		else:
			dictMessstellen.update(dict([(str('V4'), str(dictEdges[element]))])) 
	# V5 Kirchenfeldstrasse
	if element in ('188142789','-307351478'):
		if str('V5') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V5'])
			dictMessstellen['V5'] = newValue
		else:
			dictMessstellen.update(dict([(str('V5'), str(dictEdges[element]))])) 
	# V6 Weissensteinstrasse
	if element in ('167903209#2','196819395'):
		if str('V6') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V6'])
			dictMessstellen['V6'] = newValue
		else:
			dictMessstellen.update(dict([(str('V6'), str(dictEdges[element]))])) 
	# V7 Schlossstrasse, auswärts
	if element in ('313358788'):
		if str('V7') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V7'])
			dictMessstellen['V7'] = newValue
		else:
			dictMessstellen.update(dict([(str('V7'), str(dictEdges[element]))])) 
	# V8 Schlossstrasse einwärts
	if element in ('206511546'):
		if str('V8') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['V8'])
			dictMessstellen['V8'] = newValue
		else:
			dictMessstellen.update(dict([(str('V8'), str(dictEdges[element]))]))  




# write dict to csv file
with open(csvExportpath, 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in sorted(dictMessstellen.items()):
       writer.writerow([key, value])


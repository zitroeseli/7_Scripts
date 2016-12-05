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
sumoFilepath = 'HOME/6_Simulation/main_sumo_duaiterate_export.xml'

# csv file path with number of cars per edge per day 
csvExportpath = 'HOME/8_Auswertung/carCountDuaiterte.csv'

# list which contains edges with reference data
referenceEdge = ['44610923#1','58591673','-328944730#0','-44823284#0','57890915','25678026#3','43962531#0','-339294548','218643895#0','-75842027','43962529#0','-4817433','23603265','51971177','-203762445#0','368182998#0','-184746471','74704295','335085667','-171527349#2','25211072','173565348','-384145297#1','27546626#1','23586167','184171861','184719743','78135469#2',
'247952205','132046617','328944730#0','44823284#0','57890899','-25678026#3','-43962531#0','339294548','-218643895#0','75842027','-43962529#0','50055298','-48846008','-51971177','203762445#0','-368182998#0','73391787','-335085667','171527349#2','-317149409','-184162440#0','384145297#1',
'26209196#1','58591653','-57890908#0',
'58591690','313358788']
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
	# TBA04
	if element in ('44610923#1','247952205','26209196#1'):
		if str('TBA04') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA04'])
			dictMessstellen['TBA04'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA04'), str(dictEdges[element]))])) 
	# TBA08
	if element in ('58591673','132046617','58591653','58591690'):
		if str('TBA08') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA08'])
			dictMessstellen['TBA08'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA08'), str(dictEdges[element]))])) 
	# TBA11
	if element in ('-328944730#0','328944730#0'):
		if str('TBA11') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA11'])
			dictMessstellen['TBA11'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA11'), str(dictEdges[element]))])) 
	# TBA13
	if element in ('-44823284#0','44823284#0'):
		if str('TBA13') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA13'])
			dictMessstellen['TBA13'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA13'), str(dictEdges[element]))])) 
	# TBA15
	if element in ('57890915','57890899','-57890908#0','313358788'):
		if str('TBA15') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA15'])
			dictMessstellen['TBA15'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA15'), str(dictEdges[element]))])) 
	# TBA18
	if element in ('25678026#3','-25678026#3'):
		if str('TBA18') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA18'])
			dictMessstellen['TBA18'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA18'), str(dictEdges[element]))])) 
	# TBA34
	if element in ('43962531#0','-43962531#0'):
		if str('TBA34') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA34'])
			dictMessstellen['TBA34'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA34'), str(dictEdges[element]))])) 
	# TBA44
	if element in ('-339294548','339294548'):
		if str('TBA44') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA44'])
			dictMessstellen['TBA44'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA44'), str(dictEdges[element]))])) 
	# TBA68
	if element in ('218643895#0','-218643895#0'):
		if str('TBA68') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA68'])
			dictMessstellen['TBA68'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA68'), str(dictEdges[element]))])) 
	# TBA71
	if element in ('-75842027','75842027'):
		if str('TBA71') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA71'])
			dictMessstellen['TBA71'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA71'), str(dictEdges[element]))])) 
	# TBA77
	if element in ('43962529#0','-43962529#0'):
		if str('TBA77') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA77'])
			dictMessstellen['TBA77'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA77'), str(dictEdges[element]))])) 
	# TBA81
	if element in ('-4817433','50055298'):
		if str('TBA81') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA81'])
			dictMessstellen['TBA81'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA81'), str(dictEdges[element]))])) 
	# TBA82
	if element in ('23603265','-48846008'):
		#print element
		if str('TBA82') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA82'])
			dictMessstellen['TBA82'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA82'), str(dictEdges[element]))])) 
	# TBA88
	if element in ('51971177','-51971177'):
		#print element
		if str('TBA88') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['TBA88'])
			dictMessstellen['TBA88'] = newValue
		else:
			dictMessstellen.update(dict([(str('TBA88'), str(dictEdges[element]))])) 
	# BE11
	if element in ('-203762445#0','203762445#0'):
		#print element
		if str('BE11') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE11'])
			dictMessstellen['BE11'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE11'), str(dictEdges[element]))])) 
	# BE12
	if element in ('368182998#0','-368182998#0'):
		#print element
		if str('BE12') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE12'])
			dictMessstellen['BE12'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE12'), str(dictEdges[element]))])) 
	# BE13
	if element in ('-184746471','73391787'):
		#print element
		if str('BE13') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE13'])
			dictMessstellen['BE13'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE13'), str(dictEdges[element]))])) 
	# BE13N
	if element in ('74704295'):
		#print element
		if str('BE13N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE13N'])
			dictMessstellen['BE13N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE13N'), str(dictEdges[element]))])) 
	# BE132
	if element in ('335085667','-335085667'):
		#print element
		if str('BE132') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE132'])
			dictMessstellen['BE132'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE132'), str(dictEdges[element]))])) 
	# BE134
	if element in ('-171527349#2','171527349#2'):
		#print element
		if str('BE134') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE134'])
			dictMessstellen['BE134'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE134'), str(dictEdges[element]))])) 
	# BE187
	if element in ('25211072','-317149409'):
		#print element
		if str('BE187') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE187'])
			dictMessstellen['BE187'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE187'), str(dictEdges[element]))])) 
	# BE305
	if element in ('173565348','-184162440#0'):
		#print element
		if str('BE305') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE305'])
			dictMessstellen['BE305'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE305'), str(dictEdges[element]))])) 
	# BE554
	if element in ('-384145297#1','384145297#1'):
		#print element
		if str('BE554') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE554'])
			dictMessstellen['BE554'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE554'), str(dictEdges[element]))]))  
	# BE852N
	if element in ('27546626#1'):
		#print element
		if str('BE852N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE852N'])
			dictMessstellen['BE852N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE852N'), str(dictEdges[element]))])) 
	# BE944N
	if element in ('23586167'):
		#print element
		if str('BE944N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE944N'])
			dictMessstellen['BE944N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE944N'), str(dictEdges[element]))])) 
	# BE946N
	if element in ('184171861'):
		#print element
		if str('BE946N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE946N'])
			dictMessstellen['BE946N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE946N'), str(dictEdges[element]))])) 
	# BE947N
	if element in ('184719743'):
		#print element
		if str('BE947N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE947N'])
			dictMessstellen['BE947N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE947N'), str(dictEdges[element]))])) 
	# BE950N
	if element in ('78135469#2'):
		#print element
		if str('BE950N') in dictMessstellen:
			newValue = float(dictEdges[element]) + float(dictMessstellen['BE950N'])
			dictMessstellen['BE950N'] = newValue
		else:
			dictMessstellen.update(dict([(str('BE950N'), str(dictEdges[element]))])) 




# write dict to csv file
with open(csvExportpath, 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in sorted(dictMessstellen.items()):
       writer.writerow([key, value])


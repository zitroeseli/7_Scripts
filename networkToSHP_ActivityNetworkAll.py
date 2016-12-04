#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from shapely.geometry import Point, LineString
from shapely.ops import transform
import pyproj

from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree
from osgeo import ogr
import osgeo.osr as osr



# Prepare ESRI Shapefile   
driver = ogr.GetDriverByName('Esri Shapefile')
# for activityNetwork2:
ds = driver.CreateDataSource('HOME/2_Netzwerk/activityNetworkAll.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(32632)
layer = ds.CreateLayer('volcanoes', srs, ogr.wkbLineString)
# Add attributes
layer.CreateField(ogr.FieldDefn('oid', ogr.OFTInteger))
layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))

# Open network-plain-nod XML document using minidom parser
DOMTreeNode = xml.dom.minidom.parse('HOME/2_Netzwerk/activityNetwork.net.xml.nod.xml')
nodes = DOMTreeNode.documentElement
node = nodes.getElementsByTagName('node')
dictPointsNode = {}
for elements in node:
	id = elements.getAttribute('id')
	x = elements.getAttribute('x')
	y = elements.getAttribute('y')
	dictPointsNode.update(dict([(id, [x,y])]))
# Open network-plain-edge XML document using minidom parser
DOMTree = xml.dom.minidom.parse('HOME/2_Netzwerk/activityNetwork.net.xml.edg.xml')
edges = DOMTree.documentElement
edge = edges.getElementsByTagName('edge')
listShapePoints = []
dictShapeLine = {}
dictLine = {}
indi = 0
# Fill id and shape of networkfile to dictionary
for elements in edge:
	id = elements.getAttribute('id')
	shape = elements.getAttribute('shape')
	allow = elements.getAttribute('allow')
	tto = elements.getAttribute('to')
	ffrom = elements.getAttribute('from')
	if shape == '':
		xct = dictPointsNode[tto][0]
		yct = dictPointsNode[tto][1]
		xcf = dictPointsNode[ffrom][0]
		ycf = dictPointsNode[ffrom][1]
		cc = str(xct) + ',' + str(yct) + ' ' + str(xcf) + ',' + str(ycf)
		listShapePoints = cc.split(' ')
	else:
		listShapePoints = shape.split(' ')

	dictShapeLine.update(dict([(id, listShapePoints)])) 
# Create polyline with x/y values in shape attribute
for lines in dictShapeLine:
	pointList = []
	for coord in dictShapeLine[lines]:
		if  ',' in coord:
			xcoord = str(long(float(coord.split(',')[0])) + 356139.90)
			ycoord = str(long(float(coord.split(',')[1])) + 5166322.33)
			pp = Point(float(xcoord),float(ycoord))
			pointList.append(pp)
	if pointList <> []:			
		ls = LineString(pointList).wkt
		# Create a new feature (attribute and geometry)
		feature = ogr.Feature(layer.GetLayerDefn())
		feature.SetField('oid', indi)
		feature.SetField('id', str(lines))
		# Make a geometry, from Shapely object
		geom = ogr.CreateGeometryFromWkt(ls)
		feature.SetGeometry(geom)
		layer.CreateFeature(feature)
		feature = geom = None  # destroy these
		dictLine.update(dict([(lines, ls)]))
		indi+=1

print 'abgeschlossen'

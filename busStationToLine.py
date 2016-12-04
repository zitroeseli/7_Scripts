#!/usr/bin/python
# -*- coding: utf-8 -*-
# Assigns Bus- and Raillines zu Bus- and Railstations

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
from osgeo import ogr
import osgeo.osr as osr

os.chdir('Datenfile_OeV-Linien')
# Read Bus- and Raillines
busLineGeom = shapefile.Reader('buslinien_takt')
railLineGeom = shapefile.Reader('bahnlinien_takt')
records_busLineGeom = busLineGeom.records()
records_railLineGeom = railLineGeom.records()

# Prepare ESRI Shapefile Bus  
driver = ogr.GetDriverByName('Esri Shapefile')
ds = driver.CreateDataSource('bus_takt.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
layer = ds.CreateLayer('volcanoes', srs, ogr.wkbPoint)
# Add attributes
layer.CreateField(ogr.FieldDefn('oid', ogr.OFTInteger))
layer.CreateField(ogr.FieldDefn('lin_nr', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('lin_name', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('lin_takt', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('halt_nr', ogr.OFTString))
layer.CreateField(ogr.FieldDefn('halt_name', ogr.OFTString))

# Prepare ESRI Shapefile Rail  
driverRail = ogr.GetDriverByName('Esri Shapefile')
dsRail = driverRail.CreateDataSource('bahn_takt.shp')
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
layerRail = dsRail.CreateLayer('volcanoes', srs, ogr.wkbPoint)
# Add attributes
layerRail.CreateField(ogr.FieldDefn('oid', ogr.OFTInteger))
layerRail.CreateField(ogr.FieldDefn('lin_nr', ogr.OFTString))
layerRail.CreateField(ogr.FieldDefn('lin_name', ogr.OFTString))
layerRail.CreateField(ogr.FieldDefn('lin_takt', ogr.OFTString))
layerRail.CreateField(ogr.FieldDefn('halt_nr', ogr.OFTString))
layerRail.CreateField(ogr.FieldDefn('halt_name', ogr.OFTString))

records_busLineList = []
for record in records_busLineGeom:
	records_busLineList.append(record)
records_railLineList = []
for record in records_railLineGeom:
	records_railLineList.append(record)

# Read Bus- and Railstations
busStationGeom = shapefile.Reader('bushaltestellen')
railStationGeom = shapefile.Reader('bahnhaltestellen')
records_busStationGeom = busStationGeom.records()
records_railStationGeom = railStationGeom.records()

records_busStationList = []
for record in records_busStationGeom:
	records_busStationList.append(record)
records_railStationList = []
for record in records_railStationGeom:
	records_railStationList.append(record)


# Which stations adjoin the bus- and raillines
ptShapesBus = busStationGeom.shapes()
linShapesBus = busLineGeom.shapes()
lineNrBus = 0
ptShapesRail = railStationGeom.shapes()
linShapesRail = railLineGeom.shapes()
lineNrRail = 0

for line in linShapesBus:
	lineS = LineString(line.points)
	pointNr = 0
	if str(records_busLineList[lineNrBus][0]) <> '':
		for point in ptShapesBus:
			pointS = Point(point.points[0])
			pp = ""
			if lineS.buffer(0.0004).intersects(pointS):
				part = float(lineS.project(pointS))/float(lineS.length)
				# Geometry transform function based on pyproj.transform (in case length is in degree an not in meters
				project = partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init='EPSG:21781'))
				line2 = transform(project, lineS)
				point2 = transform(project, pointS)
				pp = line2.project(point2)

				# Create a new feature (attribute and geometry)
				feature = ogr.Feature(layer.GetLayerDefn())
				feature.SetField('oid', lineNrBus)
				feature.SetField('lin_nr', str(records_busLineList[lineNrBus][0]))
				feature.SetField('lin_name', str(records_busLineList[lineNrBus][1]))
				feature.SetField('lin_takt', str(records_busLineList[lineNrBus][8]))
				feature.SetField('halt_nr', str(records_busStationList[pointNr][10]))
				feature.SetField('halt_name', str(records_busStationList[pointNr][1]))
				# Make a geometry, from Shapely object
				geom = ogr.CreateGeometryFromWkt(str(pointS))
				feature.SetGeometry(geom)
				layer.CreateFeature(feature)
				feature = geom = None  # destroy these
	
			pointNr+=1
	lineNrBus+=1

for line in linShapesRail:
	lineS = LineString(line.points)
	pointNr = 0
	if str(records_railLineList[lineNrRail][0]) <> '':
		for point in ptShapesRail:
			pointS = Point(point.points[0])
			pp = ""
			if lineS.buffer(0.0004).intersects(pointS):
				part = float(lineS.project(pointS))/float(lineS.length)
				# Geometry transform function based on pyproj.transform (in case length is in degree an not in meters
				project = partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init='EPSG:21781'))
				line2 = transform(project, lineS)
				point2 = transform(project, pointS)
				pp = line2.project(point2)

				# Create a new feature (attribute and geometry)
				featureRail = ogr.Feature(layerRail.GetLayerDefn())
				featureRail.SetField('oid', lineNrRail)
				featureRail.SetField('lin_nr', str(records_railLineList[lineNrRail][0]))
				featureRail.SetField('lin_name', str(records_railLineList[lineNrRail][1]))
				featureRail.SetField('lin_takt', str(records_railLineList[lineNrRail][8]))
				featureRail.SetField('halt_nr', str(records_railStationList[pointNr][10]))
				featureRail.SetField('halt_name', str(records_railStationList[pointNr][1]))
				# Make a geometry, from Shapely object
				geom = ogr.CreateGeometryFromWkt(str(pointS))
				featureRail.SetGeometry(geom)
				layerRail.CreateFeature(featureRail)
				featureRail = geom = None  # destroy these
	
			pointNr+=1

	lineNrRail+=1


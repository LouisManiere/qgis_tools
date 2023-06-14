# Author : Louis Manière - Hydraulique Sans Frontières
# creation date : 26/10/2022
# PyQGIS 3.22
# encoding utf-8
# plugins ETL_LOAD SAGA 7

# description
# watershed automation

# libraries
import os
from qgis.core import *
import processing
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QAction

####### variables #######
wd_path = "/home/louis/Documents/HSF/Ambohimangakely/SIG/projet/"
channel_initiation_threshold = 200000

####### paths #######
# discharge_points = wd_path + 'data/discharge_points_test2.shp'
dem = wd_path + 'data/srtm_zone_etude_3857.tif'
output_folder = wd_path + 'data/watershed/'
output_watershed = output_folder + 'watershed.shp'
output_chanel_network = output_folder + 'chanel_network.shp'
output_discharge_points = output_folder + 'discharge_points.shp'

# Run Fill(Wang&Liu)
fill_wl = processing.run('saga:fillsinkswangliu',
                           {'ELEV' : dem,
                            'FDIR' : 'TEMPORARY_OUTPUT', 
                            'FILLED' : 'TEMPORARY_OUTPUT',
                            'MINSLOPE' : 0.01, 
                            'WSHED' : 'TEMPORARY_OUTPUT'
                            })
filled_dem = fill_wl['FILLED']
flowdir = fill_wl['FDIR']

# Catchment Area
catchment_area = processing.run('saga:catchmentarea',
                           {'ELEVATION' : filled_dem,
                            'FLOW' : 'TEMPORARY_OUTPUT',
                            'METHOD' : 0 })['FLOW']

# Channel Network
chanel_network = processing.run('saga:channelnetwork',
                           { 'CHNLNTWRK' : 'TEMPORARY_OUTPUT',
                            'CHNLROUTE' : 'TEMPORARY_OUTPUT',
                            'DIV_CELLS' : 10, 'DIV_GRID' : None,
                            'ELEVATION' :  filled_dem,
                            'INIT_GRID' : catchment_area,
                            'INIT_METHOD' : 2,
                            'INIT_VALUE' : channel_initiation_threshold,
                            'MINLEN' : 1,
                            'SHAPES' : 'TEMPORARY_OUTPUT',
                            'SINKROUTE' : None,
                            'TRACE_WEIGHT' : None })

# extract order >=3
chanel_extract = processing.run('qgis:extractbyattribute',
                           {'FIELD' : 'Order',
                            'INPUT' : chanel_network['SHAPES'], 
                            'OPERATOR' : 3, 
                            'OUTPUT' : 'TEMPORARY_OUTPUT', 
                            'VALUE' : '3' })['OUTPUT']

# regroup
chanel_regroup = processing.run("native:dissolve",
    { 'FIELD' : [],
    'INPUT' : chanel_extract,
    'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']

# split
chanel_cut = processing.run("native:splitwithlines",
    {'INPUT' : chanel_regroup,
     'LINES' : chanel_regroup,
     'OUTPUT' : 'TEMPORARY_OUTPUT'})['OUTPUT']

# length
chanel_length = processing.run("qgis:exportaddgeometrycolumns",
    {'CALC_METHOD' : 0, 
     'INPUT' : chanel_cut, 
     'OUTPUT' : 'TEMPORARY_OUTPUT'})['OUTPUT']

# points avant l'intersection
discharge_pts = processing.run("native:pointsalonglines",
    {'DISTANCE' : QgsProperty.fromExpression('"length_2"-50'), 
     'END_OFFSET' : 0, 
     'INPUT' : chanel_length, 
     'OUTPUT' : 'TEMPORARY_OUTPUT', 
     'START_OFFSET' : QgsProperty.fromExpression('"length_2"-50')})['OUTPUT']

# order increment field
discharge_order = processing.run("qgis:addautoincrementalfield",
    { 'FIELD_NAME' : 'order',
    'GROUP_FIELDS' : [],
    'INPUT' : discharge_pts,
    'OUTPUT' : 'TEMPORARY_OUTPUT',
    'SORT_ASCENDING' : True,
    'SORT_EXPRESSION' : '',
    'SORT_NULLS_FIRST' : False,
    'START' : 1 })['OUTPUT']

# extract max id value
idx = discharge_order.fields().indexFromName('order')
max_id = discharge_order.maximumValue(idx)-1

# select by ID iteration
for i in range(0, max_id):
    i=i+1
    print(i)
    # start point
    point_start = processing.run("qgis:extractbyattribute",
    {'INPUT':discharge_order,
    'FIELD': 'order',
    'OPERATOR': 0,
    'VALUE': i,
    'OUTPUT': 'TEMPORARY_OUTPUT'})
    
    # extract x an y coordinate
    for f in point_start['OUTPUT'].getFeatures():
        geom = f.geometry()
        x = geom.asPoint().x()
        y = geom.asPoint().y()
    
    # 2. Run UpSlopeArea
    Upslope_Area = processing.run('saga:upslopearea',
                                   {'AREA' : 'TEMPORARY_OUTPUT',
                                    'CONVERGE' : 1.1,
                                    'ELEVATION' : filled_dem,
                                    'METHOD' : 0,
                                    'SINKROUTE' : None,
                                    'TARGET' : None,
                                    'TARGET_PT_X' : x,
                                    'TARGET_PT_Y' : y })['AREA']
    
    # 3. Run Polygonize
    Initial_Watershed = processing.run('gdal:polygonize',
                   {'BAND' : 1,
                    'EIGHT_CONNECTEDNESS' : False,
                    'EXTRA' : '',
                    'FIELD' : 'DN',
                    'INPUT' : Upslope_Area,
                    'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']
    
    # 4. Fix any invalid geometries in the vectorized watershed
    Watershed = processing.run('native:fixgeometries',
                               {'INPUT' : Initial_Watershed,
                                'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']
    
    # 4a. Dissolve the Watershed layer, so that if the actual watershed is split into pieces, they are stitched together and the algorithm runs correctly
    Watershed_Dissolved = processing.run('native:dissolve',
                       { 'FIELD' : ['DN'],
                        'INPUT' : Watershed,
                        'OUTPUT' : 'TEMPORARY_OUTPUT' })['OUTPUT']
    
    # 5. Filter the watershed layer, keep only the needed watershed
    Filter_Res = processing.run('geomel_watershed:geomelWAttributes',
                               {'Watershed':  Watershed_Dissolved,
                               'Filtered_Watershed': 'TEMPORARY_OUTPUT',
                               'pour_point': str(x) + ',' + str(y),
                               'Area_Perimeter': 'TEMPORARY_OUTPUT'})
    
    Filtered_Watershed = Filter_Res['Filtered_Watershed']
    
    if i==1:
        # save in shapefile
        QgsVectorFileWriter.writeAsVectorFormat(
            Filtered_Watershed,
            output_watershed,
            "utf-8",
            Filtered_Watershed.crs(),
            "ESRI Shapefile")
    else:
        #append layer
        processing.run("etl_load:appendfeaturestolayer", {
                        'ACTION_ON_DUPLICATE' : 0,
                        'SOURCE_FIELD' : None,
                        'SOURCE_LAYER' : Filtered_Watershed,
                        'TARGET_FIELD' : None,
                        'TARGET_LAYER' : output_watershed})

# save in shapefile
QgsVectorFileWriter.writeAsVectorFormat(
    chanel_cut,
    output_chanel_network,
    "utf-8",
    chanel_cut.crs(),
    "ESRI Shapefile")

# save in shapefile
QgsVectorFileWriter.writeAsVectorFormat(
    discharge_order,
    output_discharge_points,
    "utf-8",
    discharge_order.crs(),
    "ESRI Shapefile")



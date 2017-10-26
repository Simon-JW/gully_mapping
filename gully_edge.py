#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon Walker
#
# Created:     22/10/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
################################################################################
#Take ~1-2 mins per sub-catchment.

#Requires:

#Creates:


################################################################################

# Imports
import arcpy
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import os
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.


################################################################################
#Set directories.
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
out_folder = drive + ":\PhD\junk"

################################################################################
#Set sub-catchments file and corresponding DEM.
catchments_shape = 'marshm1.shp'
input_catchments = os.path.join(root_dir, catchments_shape)
target_basin = 1339 #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas" #Short for basin. Is the name of the feature layer created by arcpy.MakeFeatureLayer_management below.

################################################################################
#Function for extracting extents of shapes for defining clipping geometry.
def extents(fc):
    extent = arcpy.Describe(fc).extent
    west = extent.XMin
    south = extent.YMin
    east = extent.XMax
    north = extent.YMax
    width = extent.width
    height = extent.height
    return west, south, east, north, width, height

# Obtain extents of two shapes
#w1, s1, e1, n1, wid1, hgt1 = extents(shape1)
#w2, s2, e2, n2, wid2, hgt2 = extents(shape2)

################################################################################

# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
#Look at what field names are in the shape file table.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print fields
cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3]])

################################################################################
#Clip DEM according to specific sub-catchment specified.
for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)) #. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        tempEnvironment0 = arcpy.env.snapRaster
        arcpy.env.snapRaster = "X:\\PhD\\junk\\mary_5m"
        tempEnvironment1 = arcpy.env.extent
        arcpy.env.extent = str(left - 25.0) + ' ' + str(bottom - 25.0) + ' ' + str(right + 25.0) + ' ' + str(top + 25.0)
        output = os.path.join(out_folder, 'temp' + str(row[0]))
        arcpy.PolygonToRaster_conversion(area_shape, "FID", output, "CELL_CENTER", "NONE", "5")
        arcpy.env.snapRaster = tempEnvironment0
        arcpy.env.extent = tempEnvironment1
        expand_raster = os.path.join(root_dir, 'exp' + str(row[0]))#Output for expand operator below.
        print 'Going into expand loop...';
        ################################################################################
        #This is only required because the expand tool will not take values > 4
        #when using arcpy. So this just performs expand within a loop, always only
        #expanding by a value of 1 at a time.
        for i in range(0, 4):
            print 'Sleeping for 5 seconds...'; time.sleep(5)
            print 'expand number: ' + str(i)
            if i == 0: #For the first loop iteration, the file to be expanded will just be the input stream order file (or one stream order from that file).
                input_expand = output #This is the file created by the Con statement above.
                output_expand = os.path.join(root_dir, expand_raster + str(i))#Name the expanded raster to be created.
                arcpy.gp.Expand_sa(input_expand, output_expand,  '1', "1")#Create the expanded raster.
            elif i > 0:
                input_expand = os.path.join(root_dir, expand_raster + str(i - 1))
                output_expand = os.path.join(root_dir, expand_raster + str(i))
                arcpy.gp.Expand_sa(input_expand, output_expand,  '1', "1")

        ################################################################################


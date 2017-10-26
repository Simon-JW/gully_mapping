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
target_basin = "SC #463" #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas" #Short for basin. Is the name of the feature layer created by arcpy.MakeFeatureLayer_management below.

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
    FID_val = row[0]
    arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
    arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)) #. Use this to save all of the shape files.
    area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
    print area_shape
    left, bottom, right, top, width, height = extents(area_shape)
    print (left, bottom, right, top, width, height)
    new = os.path.join(out_folder, dem_file[:3] + target_basin[4:])
    extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
    arcpy.Clip_management(DEM, extent, new, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
    print new

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon Walker
#
# Created:     10/10/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
################################################################################
#Take ~1-2 mins per sub-catchment.

#Requires:
# 1.Shapefile of single area or catchment. 'area' variable requires shapefile with
    #name >= 3 charaters (not including '.shp').
# 2. DEM to be clipped by shapefile area.

#Creates:
# 1. Stream order raster with background of NoData.
# 2. A filled DEM.

import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################
#Set the working directory.
drive = 'C'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
out_folder = drive + ":\PhD\junk"
area = 'weany_ck.shp'
dem_file = 'wean1m'
target_basin = 0 #For single shape this will always 0.
flow_acc_value = 10000
#target_stream_ord = 4

################################################################################
# Local variables:
input_catchments = os.path.join(root_dir, area)
bas = "bas"
dem = os.path.join(root_dir, dem_file)

#------------------------------------------------------------------------------#
#Create a feature layer to do stuff with using arcpy.
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print len(fields)
print fields
cursor = arcpy.da.SearchCursor(bas, [fields[0]])
#cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3]])

#------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------#
#Main program.
for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, area[:3] + '_' + str(FID_val))#. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, area[:3] + '_' + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        new = os.path.join(root_dir, dem_file[:3] + str(target_basin))
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(dem, extent, new, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
        print new
        #----------------------------------------------------------------------#
        #Setup local variables.
        fill_dem = os.path.join(root_dir, area[0:3] + 'f')
        flow_dir = os.path.join(root_dir, area[0:3] +'dir')
        flow_acc = os.path.join(root_dir, area[0:3] +'acc')
        streams = os.path.join(root_dir, area[0:3] +'strms')
        stream_order = os.path.join(root_dir, area[0:3] + '_' + str(target_basin) + '_' +'ord')
        filt_stream_order = os.path.join(root_dir, area[0:3] +'f_ord')
        null_filt_stream_order = os.path.join(root_dir, area[0:3] +'nf_ord')
        expand_filt_streams = os.path.join(root_dir, area[0:3] +'ef_ord')
        #----------------------------------------------------------------------#
#Syntax for extracting extent of raster.

        #dem_raster = arcpy.sa.Raster(dem)
        #clip_shape = bas
        #left = int(dem_raster.extent.XMin)
        #right = int(dem_raster.extent.XMax)
        #top = int(dem_raster.extent.YMax)
        #bottom = int(dem_raster.extent.YMin)

        #----------------------------------------------------------------------#
        # Main program
        arcpy.gp.Fill_sa(new, fill_dem, ""); print 'fill works'
        arcpy.gp.FlowDirection_sa(fill_dem, flow_dir, "NORMAL", ""); print 'flow direction works'
        arcpy.gp.FlowAccumulation_sa(flow_dir, flow_acc, "", "FLOAT"); print 'flow accumulation works'
        flow_acc_rast = arcpy.Raster(flow_acc); print 'flow accumulation raster saved'
        strms  = Con(flow_acc_rast >= flow_acc_value,1,0); print 'Raster calculator for streams =>' + str(flow_acc_value) +  'works'
        strms.save(streams); print 'stream raster saved'
        arcpy.gp.StreamOrder_sa(streams, flow_dir, stream_order, "STRAHLER"); print 'stream orders work'
        stream_ord_rast = arcpy.Raster(stream_order); print 'stream order raster saved'
        #flt_strm_ord = Con(stream_ord_rast >= target_stream_ord,1,0); print 'stream order >= threshold filtered out'
        #fil_or_st = flt_strm_ord.save(filt_stream_order); print 'filtered stream orders saved'
        #fil_or_st_rast = arcpy.Raster(filt_stream_order);
        #null_strm_ord = SetNull(fil_or_st_rast == 0, fil_or_st_rast)
        #nul_or_st = null_strm_ord.save(null_filt_stream_order); print 'nulled filtered stream orders saved'
        #arcpy.gp.Expand_sa(null_filt_stream_order, expand_filt_streams, "2", "1")

#------------------------------------------------------------------------------#
#Clean up unwanted files.
print 'Deleting streams delineated from flow accumulation'; arcpy.Delete_management(streams);
print 'Deleting clipped out area'; arcpy.Delete_management(new);
print 'Deleting flow accumulation raster'; arcpy.Delete_management(flow_acc);
print 'Deleting flow direction raster'; arcpy.Delete_management(flow_dir);

#------------------------------------------------------------------------------#
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


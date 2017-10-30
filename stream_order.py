# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# stream_order.py
# Created on: 2017-08-19 14:12:34.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: stream_order <Expand_raste1> <rastercalc1> <StreamO_rast1> <rastercalc> <Output_accumulation_raster> <Output_flow_direction_raster> <Fill_don_501> <don_50>
# Description:
# ---------------------------------------------------------------------------
#Take ~30 seconds per sub-catchment.

#Requires:
# 1. Shapefile with multiple sub-catchments that can be selected individually.
# 2. DEM covering extent of all catchments in shapefile.

#Creates:
# 1. Stream order raster with background of NoData.
# 2. New DEM clipped to area of target sub-catchment.

#Note: other components are created in the process of delineating streams and
#then deleted at thye bottom. The delete row can be hashtagged out to keep a given
#file if required.

#Imports.
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
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
out_folder = drive + ":\PhD\junk"

# Local variables:
dem_file = "mary_5m"
catchments_shape = 'Mary_subcatchments_mgaz56.shp'
target_basin = 38 #This is the FID value of the subcatchment of interest.
flow_acc_value = 1000

################################################################################
#Automatically sets paths to files.
bas = "bas"
dem = os.path.join(root_dir, dem_file)
input_catchments = os.path.join(root_dir, catchments_shape)

#------------------------------------------------------------------------------#
#Function for extracting extent from shapefiles.
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
# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print len(fields); print fields
cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3], fields[4]])

#------------------------------------------------------------------------------#

for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)) #. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        clipped_dem = os.path.join(out_folder, dem_file[:3] + '_' + str(target_basin) + '_DEM')
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        if arcpy.Exists(clipped_dem):
            print 'This file - ' + str(clipped_dem) + ' already exists'
        else:
            arcpy.Clip_management(dem, extent, clipped_dem, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
        print clipped_dem
        #----------------------------------------------------------------------#
        #Syntax for taking extents of rasters.

        #dem_raster = arcpy.sa.Raster(dem)
        #clip_shape = bas
        #left = int(dem_raster.extent.XMin)
        #right = int(dem_raster.extent.XMax)
        #top = int(dem_raster.extent.YMax)
        #bottom = int(dem_raster.extent.YMin)
        #----------------------------------------------------------------------#
        input_dem = clipped_dem # provide a default value if unspecified
        fill_dem = os.path.join(root_dir, dem_file[:3] + 'f')
        flow_dir = os.path.join(root_dir, dem_file[:3] +'dir')
        flow_acc = os.path.join(root_dir, dem_file[:3] +'fa')
        streams = os.path.join(root_dir, dem_file[:3] +'str')
        stream_order = os.path.join(root_dir, dem_file[:3] +'_' + str(target_basin) + '_' +'ord')
        filt_stream_order = os.path.join(root_dir, dem_file[:3] +'f_ord')
        null_filt_stream_order = os.path.join(root_dir, dem_file[:3] +'nf_ord')
        expand_filt_streams = os.path.join(root_dir, dem_file[:3] +'ef_ord')
        #----------------------------------------------------------------------#
        arcpy.gp.Fill_sa(input_dem, fill_dem, ""); print 'fill works'
        arcpy.gp.FlowDirection_sa(fill_dem, flow_dir, "NORMAL", ""); print 'flow direction works'
        arcpy.gp.FlowAccumulation_sa(flow_dir, flow_acc, "", "FLOAT"); print 'flow accumulation works'
        flow_acc_rast = arcpy.Raster(flow_acc); print 'flow accumulation raster saved'
        strms  = Con(flow_acc_rast >= flow_acc_value,1,0); print 'Raster calculator for streams => 1000 works'
        stream = strms.save(streams); print 'stream raster saved'
        arcpy.gp.StreamOrder_sa(streams, flow_dir, stream_order, "STRAHLER"); print 'stream orders work'
        stream_ord_rast = arcpy.Raster(stream_order); print 'stream order raster saved'
        #flt_strm_ord = Con(stream_ord_rast >= 5,1,0); print 'stream order >= threshold filtered out'
        #fil_or_st = flt_strm_ord.save(filt_stream_order); print 'filtered stream orders saved'
        #fil_or_st_rast = arcpy.Raster(filt_stream_order);
        #null_strm_ord = SetNull(fil_or_st_rast == 0, fil_or_st_rast)
        #nul_or_st = null_strm_ord.save(null_filt_stream_order); print 'nulled filtered stream orders saved'
        #arcpy.gp.Expand_sa(null_filt_stream_order, expand_filt_streams, "2", "1")
        time.sleep(1); print 'Sleeping for 1 second...'
        print 'Deleting the filled DEM'; arcpy.Delete_management(fill_dem);
        print 'Deleting flow direction raster'; arcpy.Delete_management(flow_dir);
        print 'Deleting flow accumulation raster'; arcpy.Delete_management(flow_acc);
        print 'Deleting filtered stream orders'; arcpy.Delete_management(filt_stream_order);
        print 'Deleting nulled filtered stream orders'; arcpy.Delete_management(null_filt_stream_order);
        print 'Deleting expanded filtered stream orders'; arcpy.Delete_management(expand_filt_streams);
        print 'Deleting streams'; arcpy.Delete_management(streams);
        print 'Deleting target catchment shape'; arcpy.Delete_management(area_shape);

#------------------------------------------------------------------------------#
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


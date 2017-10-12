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
root_dir = (r'C:\\PhD\\junk')
os.chdir(root_dir)

################################################################################
# Local variables:
area = 'weany_ck.shp'
input_catchments = os.path.join(root_dir, area)
target_basin = 0 #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas"
Use_Input_Features_for_Clipping_Geometry = "true"
dem_file = 'wean1m'
dem = os.path.join(root_dir, dem_file)
Statistics_type = "MINIMUM"
flowdir = os.path.join(root_dir, dem_file[:3] + 'fdir')
sink = os.path.join(root_dir, dem_file[:3] + 'sink')
watershed = os.path.join(root_dir, dem_file[:3] + 'wshd')
min_h = os.path.join(root_dir, dem_file[:3] + 'min')
max_h = os.path.join(root_dir, dem_file[:3] + 'max')
sink_depth = os.path.join(root_dir, dem_file[:3] + 'dpth')
flow_acc_value = 10000
target_stream_ord = 4
expand = "2"
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print len(fields)
print fields
cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3]])

################################################################################
#Main program.
for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        #arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)). Use this to save all of the shape files.
        dem_raster = arcpy.sa.Raster(dem)
        clip_shape = bas
        left = int(dem_raster.extent.XMin)
        right = int(dem_raster.extent.XMax)
        top = int(dem_raster.extent.YMax)
        bottom = int(dem_raster.extent.YMin)
        new = os.path.join(root_dir, dem_file[:3] + str(target_basin))
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(dem, extent, new, clip_shape, "-999", Use_Input_Features_for_Clipping_Geometry, "NO_MAINTAIN_EXTENT")
        print new
        ################################################################################
        #Setup local variables.
        Output_drop_raster = ""
        Method_of_stream_ordering = "STRAHLER"
        fill_dem = os.path.join(root_dir, area[0:3] + 'f')
        flow_dir = os.path.join(root_dir, area[0:3] +'dir')
        flow_acc = os.path.join(root_dir, area[0:3] +'acc')
        streams = os.path.join(root_dir, area[0:3] +'strms')
        stream_order = os.path.join(root_dir, area[0:3] +'ord')
        filt_stream_order = os.path.join(root_dir, area[0:3] +'f_ord')
        null_filt_stream_order = os.path.join(root_dir, area[0:3] +'nf_ord')
        expand_filt_streams = os.path.join(root_dir, area[0:3] +'ef_ord')

        ################################################################################
        # Main program
        arcpy.gp.Fill_sa(new, fill_dem, ""); print 'fill works'
        arcpy.gp.FlowDirection_sa(fill_dem, flow_dir, "NORMAL", Output_drop_raster); print 'flow direction works'
        arcpy.gp.FlowAccumulation_sa(flow_dir, flow_acc, "", "FLOAT"); print 'flow accumulation works'
        flow_acc_rast = arcpy.Raster(flow_acc); print 'flow accumulation raster saved'
        strms  = Con(flow_acc_rast >= flow_acc_value,1,0); print 'Raster calculator for streams =>' + str(flow_acc_value) +  'works'
        strms.save(streams); print 'stream raster saved'
        arcpy.gp.StreamOrder_sa(streams, flow_dir, stream_order, Method_of_stream_ordering); print 'stream orders work'
        stream_ord_rast = arcpy.Raster(stream_order); print 'stream order raster saved'
        #flt_strm_ord = Con(stream_ord_rast >= target_stream_ord,1,0); print 'stream order >= threshold filtered out'
        #fil_or_st = flt_strm_ord.save(filt_stream_order); print 'filtered stream orders saved'
        #fil_or_st_rast = arcpy.Raster(filt_stream_order);
        #null_strm_ord = SetNull(fil_or_st_rast == 0, fil_or_st_rast)
        #nul_or_st = null_strm_ord.save(null_filt_stream_order); print 'nulled filtered stream orders saved'
        #arcpy.gp.Expand_sa(null_filt_stream_order, expand_filt_streams, expand, "1")

################################################################################
#Clean up unwanted files.
print 'Deleting watershed'; arcpy.Delete_management(watershed);
print 'Deleting first flow direction'; arcpy.Delete_management(flowdir);
print 'Deleting min sink layer'; arcpy.Delete_management(min_h);
print 'Deleting max sink layer'; arcpy.Delete_management(max_h);
print 'Deleting sink depth'; arcpy.Delete_management(sink_depth);
print 'Deleting streams delineated from flow accumulation'; arcpy.Delete_management(streams);
print 'Deleting clipped out area'; arcpy.Delete_management(new);

################################################################################
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


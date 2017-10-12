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
        arcpy.gp.FlowDirection_sa(new, flowdir, "NORMAL")#Here 'new' becomes my new dem for input into hydrological analysis.
        arcpy.gp.Sink_sa(flowdir, sink)
        # Process: Watershed
        arcpy.gp.Watershed_sa(flowdir, sink, watershed, "VALUE")
        # Process: Zonal Fill
        arcpy.gp.ZonalFill_sa(watershed, new, max_h)
        # Process: Zonal Statistics
        arcpy.gp.ZonalStatistics_sa(watershed, "VALUE", new, min_h, Statistics_type, "DATA")
        # Process: Minus
        arcpy.gp.Minus_sa(max_h, min_h, sink_depth)
        sink_max = arcpy.GetRasterProperties_management(sink_depth, "MAXIMUM")
        max_value = sink_max.getOutput(0)
        print max_value
################################################################################
#Fill DEM according to calculated individual sink depths.
sinkmax = arcpy.GetRasterProperties_management(sink_depth, "MAXIMUM")
sinkm = sinkmax.getOutput(0)
print sinkm
out_fill_file = dem_file + 'fill.tif'
filled_dem = os.path.join(root_dir, out_fill_file) # provide a default value if unspecified
Z_limit = str(float(sinkm) + 0.3)
arcpy.gp.Fill_sa(dem, filled_dem, Z_limit)

################################################################################

################################################################################
#Clean up unwanted files.
print 'Deleting watershed'; arcpy.Delete_management(watershed);
print 'Deleting first flow direction'; arcpy.Delete_management(flowdir);
print 'Deleting min sink layer'; arcpy.Delete_management(min_h);
print 'Deleting max sink layer'; arcpy.Delete_management(max_h);
print 'Deleting sink depth'; arcpy.Delete_management(sink_depth);
print 'Deleting clipped out area'; arcpy.Delete_management(new);

################################################################################
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


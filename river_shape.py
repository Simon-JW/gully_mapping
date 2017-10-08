#-------------------------------------------------------------------------------
# Name:        Delineating large streams / rivers from DEM
# Purpose:      This script is used to create shapefiles of large streams and rivers
#               that can be used to train optical data for some kind of classification
#               analysis.
#
# Author:      walkers
#
# Created:     04/10/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Import arcpy module
import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################
# Local variables:
root_dir = "X:\\PhD\\junk"; os.chdir(root_dir)
filename = 'ordtest'
in_raster = os.path.join(root_dir, filename) # This should be a clipped shape from the large stream order raster.

################################################################################
#Find the highest stream order in the raster.
max_order = arcpy.GetRasterProperties_management(in_raster, "MAXIMUM")
largest_stream = int(max_order.getOutput(0))#This gets change to int so that it
#can be used as an input into value range below.
print "Highest stream order present: " + str(largest_stream)
if largest_stream <= 4:
    print 'No streams large enough.'

################################################################################
#Find all unique stream order values and create a new list containing only
#those values > 4.
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

stream_orders_present = unique_values(in_raster, 'VALUE')

streams_above_order_4 = []
for stream in stream_orders_present:
    if stream > 4:
        streams_above_order_4.append(stream)

################################################################################
# Filtering streams.
stream_order_list = []
for item in streams_above_order_4:
    order_value = item; #This is the stream order > that we want to call river.
    output = in_raster + str(item) + '_riv'; #Name of output file to be created.
    Input_true_raster_or_constant_value = "1"; #What value should the selected range become.
    arcpy.gp.Con_sa(in_raster, Input_true_raster_or_constant_value, output, "", "\"VALUE\" =" + str(item))
    diss_shp = in_raster + str(item) + "_ds"#Output for dissolve operator below.
    init_shp = "X:\\PhD\\junk\\init" + str(item) + ".shp"  # This will just be a temporary file.
    expand_raster = in_raster + str(item)  + 'exp'#Output for expand operator below.
    # Expand (in_raster, number_cells, zone_values)
    arcpy.gp.Expand_sa(output, expand_raster,  str(item - 4), "1")
    # Process: Raster to Polygon
    arcpy.RasterToPolygon_conversion(expand_raster, init_shp, "SIMPLIFY", "VALUE")
    # Process: Dissolve
    arcpy.Dissolve_management(init_shp, diss_shp, "", "", "MULTI_PART", "DISSOLVE_LINES")
    stream_order_list.append(diss_shp)#Creating a list to use for into into megre operator below.
    arcpy.Delete_management(output)
    arcpy.Delete_management(expand_raster)
    arcpy.Delete_management(init_shp)

################################################################################
#Figure out whether there are streams > order 4 for the target area. If so how many
#different orders exist > 4.
for item in stream_order_list:
    print item
    number_of_items = len(stream_order_list)

print str(number_of_items) + ' different stream classes.'

merged_streams = os.path.join(root_dir, filename[0:3] + 'm') #Output for merge operator below.
print merged_streams

#Can use the oder value to only merge correct streams i.e. 5 & 8 or 6 & 8 etc.

#Select the correct arrangement based on number of streams > order 4
if number_of_items == 1:
    print "Only one stream > order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp'], merged_streams)
elif number_of_items == 2:
    print "Two streams > order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp'], merged_streams)
elif number_of_items == 3:
    print "Three streams > order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp'], merged_streams)
elif number_of_items == 4:
    print "Four streams > order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp'], merged_streams)
elif number_of_items == 5:
    print "Four streams > order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp', str(stream_order_list[4]) + '.shp'], merged_streams)

diss_merge = merged_streams + 'ds' + ".shp"  # This will just be a temporary file.
in_diss = merged_streams + '.shp'
arcpy.Dissolve_management(in_diss, diss_merge, "", "", "MULTI_PART", "DISSOLVE_LINES")

################################################################################
#Clean up unwanted data.
#os.chdir(root_dir)
#for (dirpath, dirnames, filenames) in os.walk('.'):
#    for file in filenames:
#        if file[-7:-4] == '_ds':
#            print "This file will be deleted " + str(file)
#            arcpy.Delete_management(file)

################################################################################
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

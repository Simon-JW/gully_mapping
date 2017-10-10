#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon Walker
#
# Created:     09/10/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------


#Take ~10-15 mins per sub-catchment.

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
#Set sub-catchments file and corresponding DEM.
filename = 'filord'
root_dir = r"C:\PhD\junk"; os.chdir(root_dir)
out = r"C:\PhD\junk"
DEM = os.path.join(root_dir, filename)
LessThan = os.path.join(root_dir, 'LessThan')
SetNull = os.path.join(root_dir, 'SetNull')
Times = os.path.join(root_dir, 'Times')
desired_stream_orders = 4 # This is then number <= the stream order of interest.

################################################################################

#arcpy.FeatureClassToFeatureClass_conversion (catchments, out, "W")
in_raster = os.path.join(root_dir, DEM) # This should be a clipped shape from the large stream order raster.
################################################################################
#This part is required because the function below needs the raster to have
#an attribute table and can only build and attribute table on single band
#8-bit file.
Pixel_Type = "8_BIT_SIGNED"
conv = os.path.join(root_dir, filename + 'u' + '.tif')
arcpy.CopyRaster_management(in_raster, conv, "", "", "-9.990000e+002", "NONE", "NONE", Pixel_Type, "NONE", "NONE", "", "NONE")
Input_raster_or_constant_value_2 = "0"
Input_false_raster_or_constant_value = "1"
arcpy.gp.LessThan_sa(conv, Input_raster_or_constant_value_2, LessThan)
arcpy.gp.SetNull_sa(LessThan, Input_false_raster_or_constant_value, SetNull, "")
arcpy.gp.Times_sa(conv, SetNull, Times)
arcpy.BuildRasterAttributeTable_management(Times, "Overwrite")
################################################################################
#Find the highest stream order in the raster.
min_order = arcpy.GetRasterProperties_management(in_raster, "MINIMUM")
smallest_stream = int(min_order.getOutput(0))#This gets change to int so that it
#can be used as an input into value range below.
print "Lowest stream order present: " + str(smallest_stream)
if smallest_stream > desired_stream_orders:
    print 'No streams small enough.'

################################################################################
#Find all unique stream order values and create a new list containing only
#those values > 4.
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

stream_orders_present = unique_values(Times, 'VALUE')

streams_below_order_4 = []
for stream in stream_orders_present:
    if stream <= desired_stream_orders:
        streams_below_order_4.append(stream)

################################################################################
# Filtering streams.
stream_order_list = []
for item in streams_below_order_4:
    order_value = item; #This is the stream order > that we want to call river.
    output = os.path.join(root_dir, filename + str(item) + '_riv'); #Name of output file to be created.
    Input_true_raster_or_constant_value = "1"; #What value should the selected range become.
    arcpy.gp.Con_sa(in_raster, Input_true_raster_or_constant_value, output, "", "\"VALUE\" =" + str(item))
    diss_shp =  os.path.join(root_dir, filename + str(item) + "_ds") #Output for dissolve operator below.
    init_shp = os.path.join(root_dir, 'init' + str(item) + ".shp")  # This will just be a temporary file.
    expand_raster = os.path.join(root_dir, filename + str(item)  + 'exp')#Output for expand operator below.
    # Expand (in_raster, number_cells, zone_values)
    arcpy.gp.Expand_sa(output, expand_raster,  '1', "1")
    #Expand doesn't work for values > 2 so maybe try loop to expand by 1 each time.
#    for i in range(0,10):
#        expand_raster = os.path.join(root_dir, filename + str(i)  + 'exp')
#        arcpy.gp.Expand_sa(output, expand_raster,  '1', "1")
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
    print "Only one stream <= order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp'], merged_streams)
elif number_of_items == 2:
    print "Two streams <= order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp'], merged_streams)
elif number_of_items == 3:
    print "Three streams <= order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp'], merged_streams)
elif number_of_items == 4:
    print "Four streams <= order 4"
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp'], merged_streams)

diss_merge = os.path.join(root_dir, filename[0:3] + 'm' + 'ds' + ".shp") # This will just be a temporary file.
in_diss = os.path.join(root_dir, filename[0:3] + 'm' + '.shp')
arcpy.Dissolve_management(in_diss, diss_merge, "", "", "MULTI_PART", "DISSOLVE_LINES")

################################################################################
#Clean up unwanted data.
#os.chdir(root_dir)
#for (dirpath, dirnames, filenames) in os.walk('.'):
#    for file in filenames:
#        if file[-7:-4] == '_ds':
#            print "This file will be deleted " + str(file)
#            arcpy.Delete_management(file)

arcpy.Delete_management(LessThan)
arcpy.Delete_management(Times)
arcpy.Delete_management(SetNull)

################################################################################
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

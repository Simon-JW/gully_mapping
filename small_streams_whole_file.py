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
#Take ~10-15 seconds per sub-catchment.

#Requires:
# 1. Stream order raster for target area.

#Creates:
# 1. Clipped DEM of target catchment.
# 2. Clipped shape of target area named according to FID of that shape.
# 3. One shapefile for each stream order <= target stream order.
# 4. One shapefile combining all speerate stream order shapefiles.

################################################################################

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
#Set working directories.
root_dir = r"X:\PhD\junk"; os.chdir(root_dir)
out = r"X:\PhD\junk"
filename = 'marord'

################################################################################
# Local variables:
#Set sub-catchments file and corresponding DEM.
DEM = os.path.join(root_dir, filename)
LessThan = os.path.join(root_dir, 'LessThan')
SetNull = os.path.join(root_dir, 'SetNull')
Times = os.path.join(root_dir, 'Times')
desired_stream_orders = 2 # This is then number <= the stream order of interest.

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
#Just check for 0 at this point and if it's 0 then SetNull
conv = os.path.join(root_dir, filename + 'u' + '.tif')
arcpy.gp.LessThanEqual_sa(conv, "0", LessThan)
arcpy.gp.SetNull_sa(LessThan, "1", SetNull, "")
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

min_ord_streams = []
for stream in stream_orders_present:
    print stream
    if stream <= desired_stream_orders:
        min_ord_streams.append(stream)

################################################################################
# Filtering streams.
arcpy.env.overwriteOutput = True
stream_order_list = []
for item in min_ord_streams:
    print 'Looking at stream order: ' + str(item)
    #arcpy.env.workspace = os.path.join(root_dir, 'junk.gdb')
    #arcpy.env.scratchWorkspace = os.path.join(root_dir, 'junk.gdb')
    order_value = item; #This is the stream order > that we want to call river.
    output = os.path.join(root_dir, filename + str(item) + '_riv'); #Name of output file to be created.
    Input_true_raster_or_constant_value = "1"; #What value should the selected range become.
    arcpy.gp.Con_sa(in_raster, Input_true_raster_or_constant_value, output, "", "\"VALUE\" =" + str(item))
    diss_shp =  os.path.join(root_dir, filename + str(item) + "_ds") #Output for dissolve operator below.
    init_shp = os.path.join(root_dir, 'init' + str(item) + ".shp")  # This will just be a temporary file.
    expand_raster = os.path.join(root_dir, 'exp' + filename + str(item))#Output for expand operator below.
    print 'Going into expand loop...';
    ################################################################################
    #This is only required because the expand tool will not take values > 4
    #when using arcpy. So this just performs expand within a loop, always only
    #expanding by a value of 1 at a time.

    for i in range(0, item + 1):
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
    # Process: Raster to Polygon
    arcpy.RasterToPolygon_conversion(output_expand, init_shp, "SIMPLIFY", "VALUE")
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
    print "Only one stream <= " + str(desired_stream_orders)
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp'], merged_streams)
elif number_of_items == 2:
    print "Two streams <= " + str(desired_stream_orders)
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp'], merged_streams)
elif number_of_items == 3:
    print "Three streams <= " + str(desired_stream_orders)
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp'], merged_streams)
elif number_of_items == 4:
    print "Four streams <= " + str(desired_stream_orders)
    arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp'], merged_streams)

diss_merge = os.path.join(root_dir, filename[0:3] + 'm' + 'ds' + "sml" + ".shp") # This will just be a temporary file.
in_diss = os.path.join(root_dir, filename[0:3] + 'm' + '.shp')
arcpy.Dissolve_management(in_diss, diss_merge, "", "", "MULTI_PART", "DISSOLVE_LINES")

################################################################################
#Clean up unwanted data.
#root_dir = r"C:\PhD\junk"; os.chdir(root_dir)
for (dirpath, dirnames, filenames) in os.walk('.'):
    for file in filenames:
        if file.startswith('exp'):
            print "This file will be deleted " + str(file)
            #arcpy.Delete_management(file)

#root_dir = r"C:\PhD\junk"; os.chdir(root_dir)
for (dirpath, dirnames, filenames) in os.walk('.'):
    for dir in dirnames:
        if dir[:3] == 'exp':
            print dir
            print "This directory will be deleted " + str(dir)
            arcpy.Delete_management(dir)

arcpy.Delete_management(LessThan)
arcpy.Delete_management(Times)
arcpy.Delete_management(SetNull)
arcpy.Delete_management(in_diss)
arcpy.Delete_management(conv)

################################################################################
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
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
in_raster = "X:\\PhD\\junk\\mary_ord" # This should be a clipped shape from the large stream order raster.

################################################################################
#Find the highest stream order in the raster.
max_order = arcpy.GetRasterProperties_management(in_raster, "MAXIMUM")
largest_stream = int(max_order.getOutput(0))#This gets change to int so that it
#can be used as an input into value range below.
print largest_stream

################################################################################
# Filtering streams.
#Range starts at 1 less than my target value because this script will look for
#anything greater than i.

for i in range(4, largest_stream):
    order_value = i; #This is the stream order >= that we want to call river.
    output = in_raster + str(i + 1) + '_riv'; #Name of output file to be created.
    Input_true_raster_or_constant_value = "1"; #What value should the selected range become.
    arcpy.gp.Con_sa(in_raster, Input_true_raster_or_constant_value, output, "", "\"VALUE\" >" + str(i))
    diss_shp = in_raster + str(i + 1) + "_ds"
    init_shp = "X:\\PhD\\junk\\init" + str(i + 1) + ".shp"  # This will just be a temporary file.
    expand_raster = in_raster + 'exp' + str(i + 1)
    # Expand (in_raster, number_cells, zone_values)
    arcpy.gp.Expand_sa(output, expand_raster,  str(i - 3), "1")

    #Maybe need four different filtered datasets. One for order 5, one for order 6,
    #one for order 7, and one for order >=7. These would then be expanded by different
    #amounts (5 == least expansion >=7 == largest expansion) before being dissolved and merged into one.

    # Process: Raster to Polygon
    arcpy.RasterToPolygon_conversion(expand_raster, init_shp, "SIMPLIFY", "VALUE")

    # Process: Dissolve
    arcpy.Dissolve_management(init_shp, diss_shp, "", "", "MULTI_PART", "DISSOLVE_LINES")

################################################################################
#Clean up unwanted files.
os.chdir(root_dir)
#Delete clipped Landsat bands used to create 456 image.
for (dirpath, dirnames, filenames) in os.walk('.'):
    for file in filenames:
        if file[-9:-5] == 'init':
            print 'this file will be deleted' + '' + file
            arcpy.Delete_management(file)
#        elif file

################################################################################
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

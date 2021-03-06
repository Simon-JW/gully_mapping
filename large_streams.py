#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     09/10/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#Take ~5-10 mins per sub-catchment.

import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
import shutil
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################
#Set working directories.
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
large_streams_files = 'large_streams_files'
#Set sub-catchments file and corresponding DEM.
area = 'Mary_subcatchments_mgaz56.shp'
target_basin = 38 #Needs to be FID of target shape.
ord_file = 'mar_38_ord'
delete_ancillary_files = "no" # Either yes or no.

################################################################################
# Automatically set up input files and directories.
out_folder = os.path.join(root_dir, large_streams_files)
os.mkdir(out_folder)
DEM = os.path.join(root_dir, ord_file)
input_catchments = os.path.join(root_dir, area)
bas = "bas" #Short for basin.

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
# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
#Look at what field names are in the shape file table.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print fields
#cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3], fields[4]])
cursor = arcpy.da.SearchCursor(bas, [fields[0]])

#------------------------------------------------------------------------------#
#Clip DEM according to specific sub-catchment specified.
for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val))#. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        clipped_ord = os.path.join(out_folder, ord_file[0:3] + str(target_basin))
        print clipped_ord
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(DEM, extent, clipped_ord, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
        print clipped_ord

        #----------------------------------------------------------------------#
#Syntax for extracting extent of raster.

        #dem_raster = arcpy.sa.Raster(DEM)
        #clip_shape = bas
        #left = int(dem_raster.extent.XMin)
        #right = int(dem_raster.extent.XMax)
        #top = int(dem_raster.extent.YMax)
        #bottom = int(dem_raster.extent.YMin)

        #----------------------------------------------------------------------#
        #This part is required because the function below needs the raster to have
        #an attribute table and can only build and attribute table on single band
        #8-bit file.
        in_raster = os.path.join(root_dir, clipped_ord) # This should be a clipped shape from the large stream order raster.
        Pixel_Type = "8_BIT_SIGNED"
        conv = in_raster + 'u' + '.tif'
        arcpy.CopyRaster_management(in_raster, conv, "", "", "-9.990000e+002", "NONE", "NONE", Pixel_Type, "NONE", "NONE", "", "NONE")
        arcpy.BuildRasterAttributeTable_management(conv, "Overwrite")
        #----------------------------------------------------------------------#
        #Find the highest stream order in the raster.
        max_order = arcpy.GetRasterProperties_management(in_raster, "MAXIMUM")
        largest_stream = int(max_order.getOutput(0))#This gets change to int so that it
        #can be used as an input into value range below.
        print "Highest stream order present: " + str(largest_stream)
        if largest_stream <= 4:
            print 'No streams large enough.'
            exit()#This just stops the script running if there's no suitable streams.

        #----------------------------------------------------------------------#
        #Find all unique stream order values and create a new list containing only
        #those values > 4.
        def unique_values(table, field):
            with arcpy.da.SearchCursor(table, [field]) as cursor:
                return sorted({row[0] for row in cursor})

        stream_orders_present = unique_values(conv, 'VALUE')

        max_ord_streams = []
        for stream in stream_orders_present:
            if stream > 4:
                max_ord_streams.append(stream)

        #----------------------------------------------------------------------#
        # Filtering streams.
        stream_order_list = []
        for item in max_ord_streams:
            print item
            order_value = item; #This is the stream order > that we want to call river.
            output = in_raster + str(item) + '_riv'; #Name of output file to be created.
            Input_true_raster_or_constant_value = "1"; #What value should the selected range become.
            arcpy.gp.Con_sa(in_raster, Input_true_raster_or_constant_value, output, "", "\"VALUE\" =" + str(item))
            diss_shp = in_raster + str(item) + "_ds"#Output for dissolve operator below.
            init_shp = os.path.join(out_folder, 'init' + str(item) + ".shp")  # This will just be a temporary file.
            expand_raster = in_raster + str(item)  + 'exp'#Output for expand operator below.
            arcpy.gp.Expand_sa(output, expand_raster,  str(item - 4), "1")
            arcpy.RasterToPolygon_conversion(expand_raster, init_shp, "SIMPLIFY", "VALUE")
            arcpy.Dissolve_management(init_shp, diss_shp, "", "", "MULTI_PART", "DISSOLVE_LINES")
            stream_order_list.append(diss_shp)#Creating a list to use for into into megre operator below.
            arcpy.Delete_management(output)
            arcpy.Delete_management(expand_raster)
            arcpy.Delete_management(init_shp)

        #----------------------------------------------------------------------#
        #Figure out whether there are streams > order 4 for the target area. If so how many
        #different orders exist > 4.
        for item in stream_order_list:
            print item
            number_of_items = len(stream_order_list)
        print str(number_of_items) + ' different stream classes.'
        merged_streams = os.path.join(out_folder, ord_file[0:3] + 'm') #Output for merge operator below.
        print merged_streams
        #Can use the oder value to only merge correct streams i.e. 5 & 8 or 6 & 8 etc.
        #Select the correct arrangement based on number of streams > order 4
        if number_of_items == 1:
            print "Only one order > order 4 present"
            arcpy.Merge_management([str(stream_order_list[0]) + '.shp'], merged_streams)
        elif number_of_items == 2:
            print "Two orders > order 4 present"
            arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp'], merged_streams)
        elif number_of_items == 3:
            print "Three orders > order 4 present"
            arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp'], merged_streams)
        elif number_of_items == 4:
            print "Four orders > order 4 present"
            arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp'], merged_streams)
        elif number_of_items == 5:
            print "Four orders > order 4 present"
            arcpy.Merge_management([str(stream_order_list[0]) + '.shp', str(stream_order_list[1]) + '.shp', str(stream_order_list[2]) + '.shp', str(stream_order_list[3]) + '.shp', str(stream_order_list[4]) + '.shp'], merged_streams)

        diss_merge = os.path.join(root_dir, 'lge_strms' + ".shp")  # This will just be a temporary file.
        in_diss = merged_streams + '.shp'
        arcpy.Dissolve_management(in_diss, diss_merge, "", "", "MULTI_PART", "DISSOLVE_LINES")

#------------------------------------------------------------------------------#
#Clean up unwanted data.
time.sleep(1)
os.chdir(out_folder)
if delete_ancillary_files == 'yes':
    os.chdir(out_folder)
    for (dirpath, dirnames, filenames) in os.walk('.'):
        for file in filenames:
            print 'this file will be deleted ' + '' + file
            arcpy.Delete_management(file)

    for (dirpath, dirnames, filenames) in os.walk('.'):
        for dir in dirnames:
            print dir
            print "This directory will be deleted " + str(dir)
            shutil.rmtree(dir)
else:
    print 'Keeping all files.'
    exit()#This just stops the script running if not deleting ancillary data.

os.chdir(root_dir)
print 'Deleting this folder' + ' - ' + out_folder; os.rmdir(out_folder)


################################################################################
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

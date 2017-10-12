#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon Walker
#
# Created:     12/10/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#Take ~5-10 mins per sub-catchment.

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
input_catchments = "X:\PhD\junk\Mary_subcatchments_mgaz56.shp"
target_basin = "SC #463" #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas" #Short for basin.
filename = 'mary_ord'
Use_Input_Features_for_Clipping_Geometry = "true"
root_dir = r"X:\PhD\junk"; os.chdir(root_dir)
out = r"X:\PhD\junk"
DEM = os.path.join(root_dir, filename)

################################################################################
# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.
#Look at what field names are in the shape file table.
fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.
print fields
cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3], fields[4]])

################################################################################
#Clip DEM according to specific sub-catchment specified.
for row in cursor:
    if row[4] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        #arcpy.FeatureClassToFeatureClass_conversion (bas, out, "area" + str(FID_val)). Use this to save all of the shape files.
        dem_raster = arcpy.sa.Raster(DEM)
        clip_shape = bas
        left = int(dem_raster.extent.XMin)
        right = int(dem_raster.extent.XMax)
        top = int(dem_raster.extent.YMax)
        bottom = int(dem_raster.extent.YMin)
        new = os.path.join(out, filename[0:3] + target_basin[4:])
        print new
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(DEM, extent, new, clip_shape, "-999", Use_Input_Features_for_Clipping_Geometry, "NO_MAINTAIN_EXTENT")
        print new
        #arcpy.FeatureClassToFeatureClass_conversion (catchments, out, "W")
        in_raster = os.path.join(root_dir, new) # This should be a clipped shape from the large stream order raster.
        ################################################################################
        #This part is required because the function below needs the raster to have
        #an attribute table and can only build and attribute table on single band
        #8-bit file.
        Pixel_Type = "8_BIT_SIGNED"
        conv = in_raster + 'u' + '.tif'
        arcpy.CopyRaster_management(in_raster, conv, "", "", "-9.990000e+002", "NONE", "NONE", Pixel_Type, "NONE", "NONE", "", "NONE")
        arcpy.BuildRasterAttributeTable_management(conv, "Overwrite")
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

        stream_orders_present = unique_values(conv, 'VALUE')

        streams_above_order_4 = []
        for stream in stream_orders_present:
            if stream > 4:
                streams_above_order_4.append(stream)

        ################################################################################
        # Filtering streams.
        stream_order_list = []
        for item in streams_above_order_4:
            print item
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

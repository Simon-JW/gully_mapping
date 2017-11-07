#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     28/10/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#Take ~1-2 mins per sub-catchment.

#Requires:

#Creates:

# Imports
import arcpy
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import os
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################
#Set directories.
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
gully_edge_files = 'gully_edge_files';
catchments_shape = 'test_gul2.shp'
snapRaster = "X:\\PhD\\junk\\mary_5m"
curvature_layer = "X:\\PhD\\junk\mar_7_scpro1"
delete_ancillary_files = 'no' #Either yes or no.

################################################################################
#Set sub-catchments file and corresponding DEM.
out_folder = os.path.join(root_dir, gully_edge_files)
os.mkdir(out_folder)
input_catchments = os.path.join(root_dir, catchments_shape)
target_feature = 0 #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas" #Short for basin. Is the name of the feature layer created by arcpy.MakeFeatureLayer_management below.

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
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

#------------------------------------------------------------------------------#
#Clip DEM according to specific sub-catchment specified.
for row in cursor:
    values = []
    if row[0] == target_feature:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)) #. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        tempEnvironment0 = arcpy.env.snapRaster
        arcpy.env.snapRaster = snapRaster
        tempEnvironment1 = arcpy.env.extent
        arcpy.env.extent = str(left - 25.0) + ' ' + str(bottom - 25.0) + ' ' + str(right + 25.0) + ' ' + str(top + 25.0)
        output = os.path.join(out_folder, 'r' + str(row[0]))
        arcpy.PolygonToRaster_conversion(area_shape, "FID", output, "CELL_CENTER", "NONE", "5")
        arcpy.env.snapRaster = tempEnvironment0
        arcpy.env.extent = tempEnvironment1
        #----------------------------------------------------------------------#
        output_null = os.path.join(out_folder, output + 'n')
        arcpy.gp.IsNull_sa(output, output_null)
        inverse_output_null = os.path.join(out_folder, output + 'n' + 'in')
        arcpy.gp.Minus_sa(1, output_null, inverse_output_null)

        #----------------------------------------------------------------------#
        expand_raster = os.path.join(out_folder, 'exp' + str(row[0]))#Output for expand operator below.
        shrink_raster = os.path.join(out_folder, 'shr' + str(row[0]))#Output for shrink operator below.
        arcpy.gp.Shrink_sa(output, shrink_raster, "1", "1")#also shrinking the inital raster by one at the same time.
        shrink_null = os.path.join(out_folder, shrink_raster + 'n')#Name the expanded raster to be created.
        arcpy.gp.IsNull_sa(shrink_raster, shrink_null)
        inverse_shrink_null = os.path.join(out_folder, shrink_raster + 'n' + 'in')
        arcpy.gp.Minus_sa(1, shrink_null, inverse_shrink_null)

        #----------------------------------------------------------------------#
        #Now subtract the shrink raster from the inital raster.
        initial_edge = os.path.join(out_folder, output + 'ed')
        arcpy.gp.Minus_sa(inverse_output_null, inverse_shrink_null, initial_edge)
        initial_edge_null = os.path.join(out_folder, initial_edge + 'n')
        arcpy.gp.Con_sa(initial_edge, "0", initial_edge_null, "", "\"VALUE\" =" + '1')
        initial_edge_shape = os.path.join(out_folder, initial_edge_null + 's')
        arcpy.RasterToPolygon_conversion(initial_edge_null, initial_edge_shape, "NO_SIMPLIFY", "VALUE")
        initial_edge_curvature = os.path.join(out_folder, initial_edge + 'ft')
        arcpy.gp.ZonalStatistics_sa(initial_edge_shape + '.shp', "Id", curvature_layer, initial_edge_curvature, "MEAN", "DATA")
        edge_curv_value = arcpy.GetRasterProperties_management(initial_edge_curvature, "MEAN")
        min_value = edge_curv_value.getOutput(0)
        values.append(min_value)
        print values

        #----------------------------------------------------------------------#
        print 'Going into expand loop...';

        #----------------------------------------------------------------------#
        #This is only required because the expand tool will not take values > 4
        #when using arcpy. So this just performs expand within a loop, always only
        #expanding by a value of 1 at a time.
        for i in range(0, 4):
            #print 'Sleeping for 5 seconds...'; time.sleep(5)
            print 'expand number: ' + str(i)
            if i == 0: #For the first loop iteration, the file to be expanded will just be the input stream order file (or one stream order from that file).
                input_expand = output #This is the file created by the Con statement above.
                output_expand = os.path.join(out_folder, expand_raster + str(i))#Name the expanded raster to be created.
                arcpy.gp.Expand_sa(input_expand, output_expand,  '1', "1")#Create the expanded raster.
                expand_null = os.path.join(out_folder, expand_raster + str(i) + 'n')#Name the expanded raster to be created.
                arcpy.gp.IsNull_sa(output_expand, expand_null)
                inverse_expand_null = os.path.join(out_folder, expand_raster + str(i) + 'n' + 'in')
                arcpy.gp.Minus_sa(1, expand_null, inverse_expand_null)
                edge_curvature = os.path.join(out_folder, initial_edge + 'ft')
                edge = os.path.join(out_folder, expand_raster + str(i) + 'ed')
                arcpy.gp.Minus_sa(inverse_expand_null, inverse_output_null, edge)
                edge_null = os.path.join(out_folder, edge + 'n')
                arcpy.gp.Con_sa(edge, "0", edge_null, "", "\"VALUE\" =" + '1')
                edge_shape = os.path.join(out_folder, edge_null + 's')
                arcpy.RasterToPolygon_conversion(edge_null, edge_shape, "NO_SIMPLIFY", "VALUE")

                #--------------------------------------------------------------#
                edge_curvature = os.path.join(out_folder, edge + 'ft')
                arcpy.gp.ZonalStatistics_sa(edge_shape + '.shp', "Id", curvature_layer, edge_curvature, "MEAN", "DATA")
                edge_curv_value = arcpy.GetRasterProperties_management(edge_curvature, "MEAN")
                min_value = edge_curv_value.getOutput(0)
                values.append(min_value)
                print values
                print 'Sleeping for one second...'; time.sleep(1)

                #--------------------------------------------------------------#
            elif i > 0:
                input_expand = os.path.join(out_folder, expand_raster + str(i - 1))
                output_expand = os.path.join(out_folder, expand_raster + str(i))
                arcpy.gp.Expand_sa(input_expand, output_expand,  '1', "1")
                expand_null = os.path.join(out_folder, expand_raster + str(i) + 'n')#Name the expanded raster to be created.
                arcpy.gp.IsNull_sa(output_expand, expand_null)
                inverse_expand_null = os.path.join(out_folder, expand_raster + str(i) + 'n' + 'in')
                arcpy.gp.Minus_sa(1, expand_null, inverse_expand_null)
                edge = os.path.join(out_folder, expand_raster + str(i) + 'ed')
                arcpy.gp.Minus_sa(inverse_expand_null, os.path.join(out_folder, expand_raster + str(i - 1) + 'n' + 'in'), edge)
                edge_null = os.path.join(out_folder, edge + 'n')
                arcpy.gp.Con_sa(edge, "0", edge_null, "", "\"VALUE\" =" + '1')
                edge_shape = os.path.join(out_folder, edge_null + 's')
                arcpy.RasterToPolygon_conversion(edge_null, edge_shape, "NO_SIMPLIFY", "VALUE")

                #--------------------------------------------------------------#
                edge_curvature = os.path.join(out_folder, edge + 'ft')
                arcpy.gp.ZonalStatistics_sa(edge_shape + '.shp', "Id", curvature_layer, edge_curvature, "MEAN", "DATA")
                edge_curv_value = arcpy.GetRasterProperties_management(edge_curvature, "MEAN")
                min_value = edge_curv_value.getOutput(0)
                values.append(min_value)
                print values
                print 'Sleeping for one second...'; time.sleep(1)
#------------------------------------------------------------------------------#
#Clean up unwanted data.
if delete_ancillary_files == 'yes':
    os.chdir(out_folder)
    for (dirpath, dirnames, filenames) in os.walk('.'):
        for file in filenames:
            print "This file will be deleted " + str(file)
            arcpy.Delete_management(file)

    for (dirpath, dirnames, filenames) in os.walk('.'):
        for dir in dirnames:
            print dir
            print "This directory will be deleted " + str(dir)
            arcpy.Delete_management(dir)

else:
    print 'Keeping all files.'

#------------------------------------------------------------------------------#
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

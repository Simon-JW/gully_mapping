#-------------------------------------------------------------------------------
# Name:        Divide a DEM by subcatchment.
# Purpose:      Create clipped DEM and RGB of target area to do further analysis on.
#
# Author:      Simon Walker
#
# Created:     06/09/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>

#Take ~30 seconds per sub-catchment.
#Requires:
# 1. DEM file.
# 2. Shapefile of broader area with multiple subcatchments to select from.
# 3. Landsat or other optical satellite data with at least three bands.

#Creates:
# 1. Clipped DEM of target subcatchment.
# 2. Clipped Landsat RGB of target subcatchment.
#-------------------------------------------------------------------------------
# Imports
import arcpy
import os
import time
t0 = time.time()

################################################################################
#Set directories.
drive = 'C'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
subcatchment_files = 'subcatchment_files';

#Set sub-catchments file and corresponding DEM.
dem_file = 'wean1m'
catchments_shape = 'weany_ck.shp'
landsat ='LS8_OLI_TIRS_NBAR_P54_GANBAR01-032_090_078_20140726\scene01'
target_basin = 84 #This is the FID value of the subcatchment of interest.
delete_ancillary_files = "yes" # Either yes or no.

################################################################################
#Automatically sets paths to files.
out_folder = os.path.join(root_dir, subcatchment_files)
os.mkdir(out_folder)
DEM = os.path.join(root_dir, dem_file)
landsat_files = os.path.join(root_dir, landsat)
input_catchments = os.path.join(root_dir, catchments_shape)
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
cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3]])

#------------------------------------------------------------------------------#
#Clip DEM according to specific sub-catchment specified.
for row in cursor:
    if row[0] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)) #. Use this to save all of the shape files.
        area_shape = os.path.join(out_folder, "area" + str(FID_val) + '.shp')
        print area_shape
        left, bottom, right, top, width, height = extents(area_shape)
        print (left, bottom, right, top, width, height)
        clipped_dem = os.path.join(root_dir, dem_file[:3] + '_' + str(target_basin) + '_DEM')
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(DEM, extent, clipped_dem, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
        print clipped_dem

#------------------------------------------------------------------------------#
#Syntax for extracting extent of raster.

        #dem_raster = arcpy.sa.Raster(DEM)
        #clip_shape = bas
        #left = int(area_shape.extent.XMin); print left # This is the syntax for getting raster extents.
        #right = int(area_shape.extent.XMax); print right # This is the syntax for getting raster extents.
        #top = int(area_shape.extent.YMax); print top # This is the syntax for getting raster extents.
        #bottom = int(area_shape.extent.YMin); print bottom # This is the syntax for getting raster extents.

#------------------------------------------------------------------------------#
#Set landsat output file names.
band_1 = 'B4'
band_2 = 'B5'
band_3 = 'B6'
rgb_inputs = os.path.join(out_folder,
        dem_file[:3] + '_' + str(target_basin) + '_' + band_1 + '.tif') +';' + os.path.join(out_folder,
        dem_file[:3] + '_' + str(target_basin) + '_' + band_2 + '.tif') + ';' + os.path.join(out_folder,
        dem_file[:3] + '_' + str(target_basin) + '_' + band_3 + '.tif')

rgb_out = dem_file[:3] + '_' + str(target_basin) + '_' + str(band_1[-1:]) + str(band_2[-1:]) + str(band_3[-1:]) + '.tif'
rgb_file = os.path.join(root_dir, rgb_out)
#landsat_files = r"C:\PhD\junk\LS8_OLI_TIRS_NBAR_P54_GANBAR01-032_090_078_20140726\scene01"
os.chdir(landsat_files)

#------------------------------------------------------------------------------#
#Clip satellite imagery.
for (dirpath, dirnames, filenames) in os.walk('.'):
    for file in filenames:
        if file.endswith('.tif'):
            new_rgb = os.path.join(out_folder, dem_file[:3] + str(target_basin) + file[-7:])
            extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
            arcpy.Clip_management(file, extent, new_rgb, area_shape, "-999", "true", "NO_MAINTAIN_EXTENT")
            print new_rgb

arcpy.CompositeBands_management(rgb_inputs, rgb_file)
#------------------------------------------------------------------------------#
#Syntax for extracting extent of raster.

            #image_raster = arcpy.sa.Raster(file)
            #left = int(image_raster.extent.XMin)
            #right = int(image_raster.extent.XMax)
            #top = int(image_raster.extent.YMax)
            #bottom = int(image_raster.extent.YMin)

#------------------------------------------------------------------------------#
#Clean up unwanted files.
time.sleep(1)
#Delete clipped Landsat bands used to create 456 image.
if delete_ancillary_files == 'yes':
    os.chdir(out_folder)
    for (dirpath, dirnames, filenames) in os.walk('.'):
        for file in filenames:
            if file.startswith(dem_file[:3] + str(target_basin) + '_B'):
                print 'this file will be deleted ' + '' + file
                arcpy.Delete_management(file)
                arcpy.Delete_management(area_shape)
else:
    print 'Keeping all files.'
    exit()#This just stops the script running if not deleting ancillary data.

os.chdir(root_dir)
print 'Deleting this folder' + ' - ' + out_folder; os.rmdir(out_folder)

#Delete larger DEM used for clipping sub-catchment.
#arcpy.Delete_management(DEM)

#------------------------------------------------------------------------------#
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

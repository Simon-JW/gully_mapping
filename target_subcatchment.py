#-------------------------------------------------------------------------------
# Name:        Divide a DEM by subcatchment.
# Purpose:
#
# Author:      Simon Walker
#
# Created:     06/09/2017
# Copyright:   (c) Simon Walker 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Imports
import arcpy
import os
import time
t0 = time.time()

################################################################################
#Data

#Need input subcatchment shape.

#Convert to feature layer.

#Use to clip DEM.


input_catchments = "D:\PhD\gully_mapping\Mary\Mary_subcatchments_mgaz56.shp"
bas = "bas"
DEM = r"D:\\PhD\\5m_DEM\\QLD\\z56\\mary_5m"
Use_Input_Features_for_Clipping_Geometry = "true"
root = r"D:\PhD\junk"
out = r"D:\PhD\junk"
os.chdir(root)

################################################################################

# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.

#Look at what field names are in the shape file table.

fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.

print len(fields)

print fields

cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3], fields[4]])

target_basin = "SC #463" #Needs to be full basin code e.g. 'SC #420' as a string.

################################################################################

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
        new = os.path.join(out, DEM[-7:-3] + target_basin[4:])
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(DEM, extent, new, clip_shape, "-999", Use_Input_Features_for_Clipping_Geometry, "NO_MAINTAIN_EXTENT")
        #print new
        print new

#arcpy.FeatureClassToFeatureClass_conversion (catchments, out, "W")

#Now I need to see if I can use the selected area to clip the DEM without having tro first convert the selected area to its own shape.

################################################################################
band_1 = 'B4'
band_2 = 'B5'
band_3 = 'B6'
rgb_inputs = os.path.join(out, clip_shape[-10:-4] + '_' + band_1 + '.tif') +';' + os.path.join(out, clip_shape[-10:-4] + '_' + band_2 + '.tif') + ';' + os.path.join(out, clip_shape[-10:-4] + '_' + band_3 + '.tif')
rgb_out = clip_shape[-10:-4] + '_' + str(band_1[-1:]) + str(band_2[-1:]) + str(band_3[-1:]) + '.tif'
rgb_file = os.path.join(out, rgb_out)
root = r"D:\PhD\Landsat\LS8_OLI_TIRS_NBAR_P54_GANBAR01-032_090_078_20160512\scene01"
os.chdir(root)
################################################################################

for (dirpath, dirnames, filenames) in os.walk('.'):
    for file in filenames:
        if file.endswith('.tif'):
            image_raster = arcpy.sa.Raster(file)
            left = int(image_raster.extent.XMin)
            right = int(image_raster.extent.XMax)
            top = int(image_raster.extent.YMax)
            bottom = int(image_raster.extent.YMin)
            new = os.path.join(out, clip_shape[-10:-4] + file[-7:])
            extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
            arcpy.Clip_management(file, extent, new, clip_shape, "-999", Use_Input_Features_for_Clipping_Geometry, "NO_MAINTAIN_EXTENT")
            print new

arcpy.CompositeBands_management(rgb_inputs, rgb_file)


print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

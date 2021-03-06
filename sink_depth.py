# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# sink_depth.py
# Created on: 2017-09-13 10:01:22.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: sink_depth <Output_drop_raster> <mary_km_km2_tif> <FlowDir_mary_km1_tif> <Sink_FlowDir_ma1_tif> <Watersh_FlowDir1_tif> <ZonalSt_Watersh1_tif> <ZonalFi_Watersh1_tif> <Minus_ZonalFi_W1_tif>
# Description:
# ---------------------------------------------------------------------------

#Runtime is ~6 minutes.

# Import arcpy module
import arcpy
import os
import time
t0 = time.time()
arcpy.CheckOutExtension("Spatial")

# Local variables:
input_catchments = "C:\PhD\junk\Mary_subcatchments_mgaz56.shp"
target_basin = "SC #463" #Needs to be full basin code e.g. 'SC #420' as a string.
bas = "bas"
Use_Input_Features_for_Clipping_Geometry = "true"
dem = "C:\\PhD\\junk\\mary_5m"
root = r"C:\\PhD\\junk"
out_folder = "C:\\PhD\\junk"
os.chdir(root)
Statistics_type = "MINIMUM"
Output_drop_raster = os.path.join(out_folder, dem[-7:-3] + 'drop')
flowdir = os.path.join(out_folder, dem[-7:-3] + 'fdir')
sink = os.path.join(out_folder, dem[-7:-3] + 'sink')
watershed = os.path.join(out_folder, dem[-7:-3] + 'wshd')
min_h = os.path.join(out_folder, dem[-7:-3] + 'min')
max_h = os.path.join(out_folder, dem[-7:-3] + 'max')
sink_depth = os.path.join(out_folder, dem[-7:-3] + 'dpth')

# Process: Make Feature Layer
arcpy.MakeFeatureLayer_management(input_catchments, bas, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;Id Id VISIBLE NONE;gridcode gridcode VISIBLE NONE")
#This is required because SelectByFeature and SelectByAttribute do not work on shape files using arcpy. Hence they need to first be convereted to feature layers.

#Look at what field names are in the shape file table.

fields = [f.name for f in arcpy.ListFields(bas)]#Just tells me what field names the data has.

print len(fields)

print fields

cursor = arcpy.da.SearchCursor(bas, [fields[0], fields[1], fields[2], fields[3], fields[4]])

################################################################################

for row in cursor:
    if row[4] == target_basin:
        FID_val = row[0]
        arcpy.SelectLayerByAttribute_management(bas, "NEW_SELECTION", "\"FID\" = " + str(FID_val))
        #arcpy.FeatureClassToFeatureClass_conversion (bas, out_folder, "area" + str(FID_val)). Use this to save all of the shape files.
        dem_raster = arcpy.sa.Raster(dem)
        clip_shape = bas
        left = int(dem_raster.extent.XMin)
        right = int(dem_raster.extent.XMax)
        top = int(dem_raster.extent.YMax)
        bottom = int(dem_raster.extent.YMin)
        new = os.path.join(out_folder, dem[-7:-3] + target_basin[4:])
        extent = str(left) + ' ' + str(bottom) + ' ' + str(right) + ' ' + str(top)
        arcpy.Clip_management(dem, extent, new, clip_shape, "-999", Use_Input_Features_for_Clipping_Geometry, "NO_MAINTAIN_EXTENT")
        #print new
        print new
        # Process: Flow Direction
        arcpy.gp.FlowDirection_sa(new, flowdir, "NORMAL", Output_drop_raster)#Here 'new' becomes my new dem for input into hydrological analysis.
        # Process: Sink
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


print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


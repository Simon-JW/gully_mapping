#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     10/11/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy


# Local variables:
mar_38_dem = "X:\\PhD\\junk\\mar_38_dem"
#Reclassification = "3.138347 6.982469 1;6.982469 10.986762 2;10.986762 14.350369 3;14.350369 15.952086 4;15.952086 17.393632 5;17.393632 19.475864 6;19.475864 23.480158 7;23.480158 28.765825 8;28.765825 33.731148 9;33.731148 44.142311 10"
#Reclass_mar_38_1_tif = "X:\\PhD\\junk\\Reclass_mar_38_1.tif"

# Process: Reclassify
#arcpy.gp.Reclassify_sa(mar_38_dem, "VALUE", Reclassification, Reclass_mar_38_1_tif, "DATA")

min = arcpy.GetRasterProperties_management(mar_38_dem, "MINIMUM")
#Get the elevation standard deviation value from geoprocessing result object
min_v = min.getOutput(0)
min_f = float(min_v)
max = arcpy.GetRasterProperties_management(mar_38_dem, "MAXIMUM")
max_v = max.getOutput(0)
max_f = float(max_v)
value_range = max_f - min_f
bins = value_range / 10.0

for i in range(1,11):
    print 'finding start bin ' + str(i)
    start_bin = min_f + (bins * (i - 1))
    end_bin = min_f + (bins * i)
    print 'bin range ' + str(start_bin) + ' - ' + str(end_bin)



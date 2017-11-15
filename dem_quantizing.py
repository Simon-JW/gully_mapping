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
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import os
import numpy as np
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

# Local variables:
mar_38_dem = "X:\\PhD\\junk\\mar_38_dem"
#Reclassification = "3.138347 6.982469 1;6.982469 10.986762 2;10.986762 14.350369 3;14.350369 15.952086 4;15.952086 17.393632 5;17.393632 19.475864 6;19.475864 23.480158 7;23.480158 28.765825 8;28.765825 33.731148 9;33.731148 44.142311 10"
Reclass_out = "X:\\PhD\\junk\\Reclass.tif"

min = arcpy.GetRasterProperties_management(mar_38_dem, "MINIMUM")
#Get the elevation standard deviation value from geoprocessing result object
number_of_bins = 10.0
min_v = min.getOutput(0)
min_f = float(min_v)
max = arcpy.GetRasterProperties_management(mar_38_dem, "MAXIMUM")
max_v = max.getOutput(0)
max_f = float(max_v)
value_range = max_f - min_f
bins = value_range / number_of_bins

rows = int(number_of_bins)
print 'Number of bins == ' + str(rows)
array_input = float(rows)
bin_array = np.zeros([array_input, 3], dtype=float)
print bin_array

range_max = int(number_of_bins + 1)
print range_max
bin_list = []
for i in range(1,range_max):
    print 'finding start bin ' + str(i)
    start_bin = min_f + (bins * (i - 1))
    end_bin = min_f + (bins * i)
    print 'bin range ' + str(start_bin) + ' - ' + str(end_bin)
    bin_array[i-1,0] = str(start_bin)
    bin_array[i-1,1] = str(end_bin)
    bin_array[i-1,2] = i
    bin_size = str(start_bin) + ' ' + str(end_bin) + ' ' + str(i) + ';'
    bin_list.append(bin_size)

print len(bin_list)
my_lst_str = ''.join(map(str, bin_list))
print(my_lst_str)
Reclassification = my_lst_str

# Process: Reclassify
arcpy.gp.Reclassify_sa(mar_38_dem, "VALUE", Reclassification, Reclass_out, "DATA")







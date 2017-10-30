# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# windows.py
# Created on: 2017-06-26 15:28:29.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: windows <fitz_f12_tif> <Foc_test>
# Description:
# ---------------------------------------------------------------------------
#Take ~1-2 mins per sub-catchment.

#Requires:
# 1. DEM.

#Creates:
# 1.

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
#Set working directory.
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
out_folder = drive + ":\PhD\junk"
filename = 'mar_90_dem' #This is the input DEM.

#Set parameters.
mean_threshold = -0.5 # Highest elevation anomaly to be preserved.
stdev_threshold = -0.5 # Highest elevation anomaly to be preserved.
iteration_factor = 5 #This is the value to adjust the window size for each iteration.
range_len = 3 #This is the numer of times you want the loop to iterate through
                #different window sizes. Because Python indexes from 0, the
                #number of files you create will always be 1 less than this value.

################################################################################
# Local variables:
in_rast = os.path.join(root_dir, filename) # provide a default value if unspecified
shape = 'Rectangle ' #Name desired shape exactly with one space before closing quotes.
units = 'CELL' # or 'MAP', no space after
mean = "MEAN" #Can be any of the acceptable operations depending on data type (float or int)
standard_deviation = "STD"

#------------------------------------------------------------------------------#
#Main program.
for i in range(1,range_len):
    height = str(i * iteration_factor) + ' '
    width = str(i * iteration_factor) + ' '
    #--------------------------------------------------------------------------#
    #Window mean.
    mean_out = filename[:2] + '_' + 'm' + '_'  + str(i*iteration_factor)#
    new_m = os.path.join(root_dir,mean_out)
    Neighborhood = str(shape + height + width + units)
    print ('Window specifications', Neighborhood)
    print ('mean raster', new_m)
    # Process: Focal Statistics
    arcpy.gp.FocalStatistics_sa(in_rast, new_m, Neighborhood, mean, "true")
    outName_mean = os.path.join(root_dir, mean_out + 'anom')
    time.sleep(5); print 'sleeping for 5 seconds'
    win_mean = arcpy.gp.Minus_sa(in_rast, new_m, outName_mean)
    final_mean_mask = os.path.join(root_dir, filename[:2] + 'mmask' + str(i*iteration_factor))
    mean_thold= arcpy.gp.LessThanEqual_sa(win_mean, mean_threshold, final_mean_mask)
    final_mean = os.path.join(root_dir, filename[:2] + 'fim'+ str(i*iteration_factor))
    arcpy.gp.Times_sa(final_mean_mask, outName_mean, final_mean)

    #--------------------------------------------------------------------------#
    #Window standarised anomalies.
    stdev_out = filename[:2] + '_' + 's' + '_'  + str(i*iteration_factor)
    new_s = os.path.join(root_dir,stdev_out)
    print ('standard deviation raster', new_s)
    # Process: Focal Statistics
    arcpy.gp.FocalStatistics_sa(in_rast, new_s, Neighborhood, standard_deviation, "true")
    outName_stdev = os.path.join(root_dir, stdev_out + '_r')
    time.sleep(5); print 'sleeping for 5 seconds'
    win_std = arcpy.gp.Divide_sa(win_mean, new_s, outName_stdev)
    final_std_mask = os.path.join(root_dir, filename[:2] + 'smask'+ str(i*iteration_factor))
    std_thold = arcpy.gp.LessThanEqual_sa(win_mean, mean_threshold, final_std_mask)
    final_std = os.path.join(root_dir, filename[:2] + 'fis'+ str(i*iteration_factor))
    arcpy.gp.Times_sa(final_std_mask, outName_stdev, final_std)

    #--------------------------------------------------------------------------#
    #Clean up unwanted standardised anomaly files.
    arcpy.Delete_management(new_s)
    arcpy.Delete_management(outName_stdev)
    #arcpy.Delete_management(final_std)
    #--------------------------------------------------------------------------#
    #Clean up unwanted anomaly files.
    arcpy.Delete_management(new_m)
    arcpy.Delete_management(outName_mean)
    #arcpy.Delete_management(final_mean)

#------------------------------------------------------------------------------#
    #Other optional operations.
    filt_m = arcpy.Raster(final_mean)
    filt_s = arcpy.Raster(final_std)
    bool_m = SetNull(filt_m == 0, 1)
    bool_s = SetNull(filt_s == 0, 1)
    mask_mean = os.path.join(root_dir, filename[:3] + 'b_m'+ str(i))
    mask_stdev = os.path.join(root_dir, filename[:3] + 'b_s'+ str(i))
    bool_m.save(mask_mean)
    bool_s.save(mask_stdev)
    meandiffgul = os.path.join(root_dir, filename[:3] + 'shm'+ str(i))
    stddiffgul = os.path.join(root_dir, filename[:3] + 'shs'+ str(i))
    arcpy.RasterToPolygon_conversion(mask_mean, meandiffgul, "NO_SIMPLIFY", "VALUE")
    arcpy.RasterToPolygon_conversion(mask_stdev, stddiffgul, "NO_SIMPLIFY", "VALUE")

#------------------------------------------------------------------------------#
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))


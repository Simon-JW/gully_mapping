#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     03/11/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#Imports.
import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################

drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
subcatchment_files = 'subcatchment_files'
spectral_files = 'spectral_indices';
subcatchment = 'wea_0'
Band_3 = subcatchment + '_B3.tif' # Green
Band_5 = subcatchment + '_B5.tif' # NIR
Band_6 = subcatchment + '_B6.tif' # SWIR 1
Band_7 = subcatchment + '_B7.tif' # SWIR 2
delete_ancillary_files = 'no' #Either yes or no.
mndwi_threshold = 0.09 # Taken from (H. Xu, 2006)
awei_threshold = 0.0 # Taken from (Feyisa et al., 2014)

################################################################################
#
out_folder = os.path.join(root_dir, spectral_files)
os.mkdir(out_folder)
green = os.path.join(root_dir, subcacthment_files, Band_3)
nir = os.path.join(root_dir, subcacthment_files, Band_5)
swir_1 = os.path.join(root_dir, subcacthment_files, Band_6)
swir_2 = os.path.join(root_dir, subcacthment_files, Band_7)

#------------------------------------------------------------------------------#
# Set up spectral band files.
green_float = os.path.join(out_folder, Band_3[:8] + 'flt')
nir_float = os.path.join(out_folder, Band_5[:8] + 'flt')
swir_1_float = os.path.join(out_folder, Band_6[:8] + 'flt')
swir_2_float = os.path.join(out_folder, Band_7[:8] + 'flt')

arcpy.gp.Times_sa(green, "1.0", green_float); print str(green_float) + '-' + 'conversion to float works.'
arcpy.gp.Times_sa(nir, "1.0", nir_float); print str(nir_float) + '-' +'conversion to float works.'
arcpy.gp.Times_sa(swir_1, "1.0", swir_1_float); print str(swir_1_float) + '-' +'conversion to float works.'
arcpy.gp.Times_sa(swir_2, "1.0", swir_2_float); print str(swir_2_float) + '-' +'conversion to float works.'

green_rast = arcpy.Raster(green_float)
nir_rast = arcpy.Raster(nir_float)
swir_1_rast = arcpy.Raster(swir_1_float)
swir_2_rast = arcpy.Raster(swir_2_float)

#------------------------------------------------------------------------------#
# Modified Normalized Difference Water Index
MNDWI_file = 'MNDWI'
MNDWI_name = os.path.join(out_folder, MNDWI_file)
MNDWI_calculation  = (green_rast - swir_1_rast) / (green_rast + swir_1_rast); print 'MNDWI calculation works'
MNDWI = MNDWI_calculation.save(MNDWI_name); print 'MNDWI raster saved'
MNDWI_rast = arcpy.Raster(MNDWI_name)
MNDWI_water = os.path.join(out_folder, 'MNDWI_water')
MNDWI_filter  = Con(MNDWI_rast >= mndwi_threshold,1,0); print 'Raster calculator for MNDWI works'
MNDWI_output = MNDWI_filter.save(MNDWI_water); print 'stream raster saved.'

#------------------------------------------------------------------------------#
#Automated Water Extraction Index
AWEI_file = 'AWEI'
AWEI_name = os.path.join(out_folder, AWEI_file)

AWEI_calculation  = 4 * (green_rast - swir_1_rast) / ((0.25 * nir_rast) + (2.75 * swir_2_rast)); print 'AWEI calculation works'
AWEI = AWEI_calculation.save(AWEI_name); print 'AWEI raster saved'
AWEI_rast = arcpy.Raster(AWEI_name)
AWEI_water = os.path.join(out_folder, 'AWEI_water')
AWEI_filter  = Con(AWEI_rast >= awei_threshold,1,0); print 'Raster calculator for AWEI works'
AWEI_output = AWEI_filter.save(AWEI_water); print 'stream raster saved.'

#------------------------------------------------------------------------------#
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

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
spectral_files = 'spectral_indices';
Band_a = 'mar29_B3.tif'
Band_b = 'mar29_B6.tif'
delete_ancillary_files = 'no' #Either yes or no.

################################################################################
#
out_folder = os.path.join(root_dir, spectral_files)
os.mkdir(out_folder)
green = os.path.join(root_dir, Band_a)
swir = os.path.join(root_dir, Band_b)

#------------------------------------------------------------------------------#
#
green_float = os.path.join(out_folder, Band_a[:8] + 'flt')
swir_float = os.path.join(out_folder, Band_b[:8] + 'flt')

arcpy.gp.Times_sa(green, "1.0", green_float); print 'conversion to float works.'
arcpy.gp.Times_sa(swir, "1.0", swir_float); print 'conversion to float works.'

green_rast = arcpy.Raster(green_float)
swir_rast = arcpy.Raster(swir_float)

MNDWI_file = 'MNDWI'
MNDWI = os.path.join(out_folder, MNDWI_file)

MNDWI_calculation  = (green_rast - swir_rast) / (green_rast + swir_rast); print 'MNDWI calculation works'
MNDWI = MNDWI_calculation.save(MNDWI); print 'MNDWI raster saved'

#------------------------------------------------------------------------------#
#Time taken.
print ""
print "Time taken:"
print "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))

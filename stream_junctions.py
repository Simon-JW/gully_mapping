#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     05/04/2018
# Copyright:   (c) walkers 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#Take ~x seconds per sub-catchment.

#Requires:
# 1.
# 2.
#Creates:
# 1.
# 2. .

#Note:

#Imports.
import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.
arcpy.env.overwriteOutput = True
import shutil

################################################################################
#Section 1: Set the working directory.
drive = 'X'
root_dir = drive + ":\PhD\junk"; os.chdir(root_dir)
stream_junction_files = 'stream_junction_files';

# Local variables:
stream_order_file = "mar_54_ord"

delete_ancillary_files = "no" # Either yes or no.

################################################################################
# Local variables:
in_rast = os.path.join(root_dir, stream_order_file) # provide a default value if unspecified
shape = 'Circle' #Name desired shape exactly with one space before closing quotes.
units = 'CELL' # or 'MAP', no space after
statistic = "VARIETY" #Can be any of the acceptable operations depending on data type (float or int)
out_folder = os.path.join(root_dir, stream_junction_files)
os.mkdir(out_folder)

#------------------------------------------------------------------------------#

radius = str(1)

#------------------------------------------------------------------------------#
# Setup window parameters.
variety_out = stream_order_file[:2] + '_' + 'v' + '_'  + radius#
new_v = os.path.join(out_folder, variety_out)
neighborhood = str(shape + ' ' + radius + ' ' + units)
print ('Window specifications', neighborhood)
print 'mean raster ' + 'for window size ' + radius + ' ' +  new_v

#------------------------------------------------------------------------------#

# Process: Focal Statistics
arcpy.gp.FocalStatistics_sa(in_rast, new_v, neighborhood, statistic, "true")
junctions = os.path.join(out_folder, stream_order_file[:3] +'jun')
junctions_rast = arcpy.Raster(new_v);
junct  = Con(junctions_rast >= 2,1,0);
junction_file = junct.save(junctions)

output_expand = os.path.join(out_folder, 'exp' + '_' + 'junct')
arcpy.gp.Expand_sa(junct, output_expand,  '3', "1")#Create the expanded raster.

print 'stream raster saved'
print ""
print "Time taken: " "hours: %i, minutes: %i, seconds: %i" %(int((time.time()-t0)/3600), int(((time.time()-t0)%3600)/60), int((time.time()-t0)%60))




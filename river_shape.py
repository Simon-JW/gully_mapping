#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      walkers
#
# Created:     04/10/2017
# Copyright:   (c) walkers 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
from arcpy import env
from arcpy.sa import Con
from arcpy.sa import *
import time; t0 = time.time()
import sys
arcpy.CheckOutExtension("Spatial")#Make sure spatial analyst is activated.

################################################################################

# Local variables:
in_raster = "X:\\PhD\\junk\\mary_ord" # This should be a clipped shape from the large stream order raster.

################################################################################
# Conditional syntax.

mary_ord = "X:\\PhD\\junk\\mary_ord"
Input_true_raster_or_constant_value = "1"
Con_mary = "X:\\PhD\\junk\\con_mary"

# Process: Con
arcpy.gp.Con_sa(mary_ord, Input_true_raster_or_constant_value, Con_mary, "", "\"VALUE\" >=5")

################################################################################

diss_shp = in_raster + "_ds"
init_shp = "X:\\PhD\\junk\\init.shp" # This will just be a temporary file.
print diss_shp
# Process: Raster to Polygon
arcpy.RasterToPolygon_conversion(in_raster, init_shp, "SIMPLIFY", "VALUE")

# Process: Dissolve
arcpy.Dissolve_management(init_shp, diss_shp, "", "", "MULTI_PART", "DISSOLVE_LINES")


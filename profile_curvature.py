# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# profile_curvature.py
# Created on: 2017-09-27 18:16:37.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: profile_curvature <curve> <pro_curve> <plan_curve> <Input_raster_or_constant_value_2> <Input_raster_or_constant_value_2__2_> <pprocurve> <nprocurve> <Z_factor>
# Description:
# ---------------------------------------------------------------------------

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

curve = "C:\\PhD\\junk\\curve"

pro_curve = "C:\\PhD\\junk\\pro_curve"

Input_raster_or_constant_value_2 = "-3.0"
Input_raster_or_constant_value_2__2_ = "3.0"

pprocurve = "C:\\PhD\\junk\\pprocurve"

nprocurve = "C:\\PhD\\junk\\nprocurve"

Z_factor = "1"

# Local variables:
mary462 = "C:\\PhD\\junk\\mary462"
p_plus_n = "C:\\PhD\\junk\\p_plus_n"
Delete_succeeded = "true"
Delete_succeeded__2_ = "true"
Delete_succeeded__3_ = "true"
filtprocurve = "C:\\PhD\\junk\\filtprocurve"
Input_raster_or_constant_value_1 = "1"
inverse = "C:\\PhD\\junk\\inverse"
Input_false_raster_or_constant_value = "1"
nullprocurve = "C:\\PhD\\junk\\nullprocurve"
Delete_succeeded__4_ = "true"

# Process: Curvature
arcpy.gp.Curvature_sa(mary462, curve, Z_factor, pro_curve, plan_curve)

# Process: Greater Than Equal
arcpy.gp.GreaterThanEqual_sa(pro_curve, Input_raster_or_constant_value_2__2_, pprocurve)

# Process: Less Than Equal
arcpy.gp.LessThanEqual_sa(pro_curve, Input_raster_or_constant_value_2, nprocurve)

# Process: Plus
arcpy.gp.Plus_sa(pprocurve, nprocurve, p_plus_n)

# Process: Delete
arcpy.Delete_management(pprocurve, "")

# Process: Delete (2)
arcpy.Delete_management(nprocurve, "")

# Process: Delete (3)
arcpy.Delete_management(curve, "")

# Process: Times
arcpy.gp.Times_sa(p_plus_n, pro_curve, filtprocurve)

# Process: Minus
arcpy.gp.Minus_sa(Input_raster_or_constant_value_1, p_plus_n, inverse)

# Process: Set Null
arcpy.gp.SetNull_sa(inverse, Input_false_raster_or_constant_value, nullprocurve, "")

# Process: Delete (4)
arcpy.Delete_management(inverse, "")


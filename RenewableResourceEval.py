#=================================
# RenewableResourceEval
#
# Last updated 12/5/2018
# Created by Jeff Bennett (jab6ft@virginia.edu)
#
# Method based on: Hermann S (KTH), Miketa A (IRENA), Fichaux N (IRENA). (2014) Estimating the Renewable Energy Potential in Africa: A GIS-based approach
# http://www.irena.org/publications/2014/Aug/Estimating-the-Renewable-Energy-Potential-in-Africa-A-GIS-based-approach
#
# Code compatible with ArcMap v10.5.1
#=================================


# Begin Program
import arcpy
from arcpy.sa import *

def Run_RenewableResourceEval_V2(analysisTypes, analysisOptions, databases, namingConv):
                    
	#-------------
	# Unpack Inputs
	print "Step 1 - Unpack Inputs"
	#-------------
	
	# Analysis Types
	analyzeSolar 	= analysisTypes[0]
	analyzeWind 	= analysisTypes[1]
	analyzeBiomass 	= analysisTypes[2]

	# Analysis Options
	usePopulation 		= analysisOptions[0]
	useProtect 			= analysisOptions[1]
	populationFilter 	= analysisOptions[2]
	populationRadius 	= analysisOptions[3]
	skipExclusionZone	= analysisOptions[4]

	# Geodatabases
	preGdb 		= databases[0]
	interGdb 	= databases[1]
	resultsGdb 	= databases[2]

	# Pre-processing Naming Convention (all files are expected in the Pre-processing Geodatabase, preGdb)
	LULC_project_name 		= namingConv[0]
	DEM_project_name 		= namingConv[1]
	Protect_project_name 	= namingConv[2]
	population_project_name = namingConv[3]
	Solar_project_name 		= namingConv[4]
	Wind_project_name 		= namingConv[5]
	Outline_project_name 	= namingConv[6]

	#-------------
	# File Management
	print "Step 2 - File Management"
	#-------------
	
	# Check if intermediate and results geodatabases exist, if not create them
	# arcpy.CreateFileGDB_management("C:/output", "fGDB.gdb")
	# arcpy.CreateFileGDB_management("C:/output", "fGDB.gdb")

	# Pre-processing Inputs (all files are expected in the Pre-processing Geodatabase, preGdb)
	Outline_project 				= preGdb + "\\" + Outline_project_name
	population_project 				= preGdb + "\\" + population_project_name
	LULC_project 					= preGdb + "\\" + LULC_project_name
	DEM_project 					= preGdb + "\\" + DEM_project_name
	Protect_project 				= preGdb + "\\" + Protect_project_name
	Wind_project 					= preGdb + "\\" + Wind_project_name
	Solar_project 					= preGdb + "\\" + Solar_project_name

	# Intermediate Outputs:
	DEM_Resample 					= interGdb + "\\" + "DEM_Resample"
	population_extract 				= interGdb + "\\" + "population_extract"
	population_points 				= interGdb + "\\" + "population_points"
	population_buffer 				= interGdb + "\\" + "population_buffer"
	population_buffer_dissolve 		= interGdb + "\\" + "population_buffer_dissolve"
	population_bufferToR 			= interGdb + "\\" + "population_bufferToR"
	population_buffer_resample 		= interGdb + "\\" + "population_buffer_resample"
	Protect_Resample				= interGdb + "\\" + "Protect_resample"
	Slope 							= interGdb + "\\" + "Slope"
	Solar_Include_Resample 			= interGdb + "\\" + "Solar_Include_Resample"
	Solar_Resource_Convert 			= interGdb + "\\" + "Solar_Resource_Convert"
	Wind_Full_Load_Hours 			= interGdb + "\\" + "Wind_Full_Load_Hours"
	Wind_Full_Load_Hours_filtered 	= interGdb + "\\" + "Wind_Full_Load_Hours_filtered"
	Wind_Include_Resample 			= interGdb + "\\" + "Wind_Include_Resample"

	# Results Outputs:
		# Inclusion/Exclusion Zones
	Incl_Population 				= resultsGdb + "\\" + "Incl_Population"
	Excl_Slope 						= resultsGdb + "\\" + "Excl_Slope"
	Excl_Water 						= resultsGdb + "\\" + "Excl_Water"
	Excl_Cities 					= resultsGdb + "\\" + "Excl_Cities"
	Excl_Crops 						= resultsGdb + "\\" + "Excl_Crops"
	Excl_Forest 					= resultsGdb + "\\" + "Excl_Forest"
	Excl_Protect 					= resultsGdb + "\\" + "Excl_Protect"
	Solar_Include 					= resultsGdb + "\\" + "Solar_Include"
	Wind_Include 					= resultsGdb + "\\" + "Wind_Include"
		# Resources
	Solar_Resource 					= resultsGdb + "\\" + "Solar_Resource"
	Solar_Generation_Potential_TWh 	= resultsGdb + "\\" + "Solar_Generation_Potential_TWh"
	Wind_Resource 					= resultsGdb + "\\" + "Wind_Resource"
	Wind_Generation_Potential_TWh 	= resultsGdb + "\\" + "Wind_Generation_Potential_TWh"

	if skipExclusionZone != "Y":
		#-------------
		# Retrieve Cell Sizes of LULC to use as basis for resampling exclusion zones
		print "Step 3 - Unpack Inputs"
		#-------------
		ResampleBasis_X = arcpy.GetRasterProperties_management(LULC_project, "CELLSIZEX")
		ResampleBasis_Y = arcpy.GetRasterProperties_management(LULC_project, "CELLSIZEY")
		Resample_expr = str(ResampleBasis_X[0]) + " " + str(ResampleBasis_Y[0])

		#-------------
		# Process Population
		print "Step 4 - Process Population"
		#-------------
		if usePopulation == "Y":
			# Find areas with population above populationFilter
			expr = "VALUE > " + populationFilter
			arcpy.gp.ExtractByAttributes_sa(population_project, expr, population_extract)

			# Process: Raster to Point
			arcpy.RasterToPoint_conversion(population_extract, population_points, "Value")

			# Process: Graphic Buffer
			expr = populationRadius + " Kilometers"
			arcpy.GraphicBuffer_analysis(population_points, population_buffer, expr, "ROUND", "MITER", "10", "0 Meters")

			# Process: Dissolve
			arcpy.Dissolve_management(population_buffer, population_buffer_dissolve, "", "", "MULTI_PART", "DISSOLVE_LINES")

			# Process: Polygon to Raster
			arcpy.PolygonToRaster_conversion(population_buffer_dissolve, "OBJECTID", population_bufferToR, "CELL_CENTER", "NONE", "18000")

			# Resample raster to match LULC
			arcpy.Resample_management(population_bufferToR, population_buffer_resample, Resample_expr, "NEAREST")

			# Process: Reclassify - in case there are multiple areas
			n_pop_areas = arcpy.GetRasterProperties_management (population_buffer_resample, "UNIQUEVALUECOUNT")
			if n_pop_areas[0] > 1:
				expr = arcpy.sa.RemapRange([[0,float(n_pop_areas[0]),1]])
			else:
				expr = arcpy.sa.RemapRange([[0,1,1]])
			temp = arcpy.sa.Reclassify(population_buffer_resample, "Value", expr, "DATA")
			temp.save(Incl_Population)

		#-------------
		# Calculate Slope and classify
		print "Step 5 - Calculate Slope and classify"
		#-------------
		# Resample DEM to match LULC
		arcpy.Resample_management(DEM_project, DEM_Resample, Resample_expr, "NEAREST")

		# Calculate Slope
		arcpy.gp.Slope_sa(DEM_Resample, Slope, "DEGREE", "1", "PLANAR", "METER")

		# Reclassify for acceptable slopes
		slope_filter = 45
		max_slope = arcpy.GetRasterProperties_management (Slope, "MAXIMUM")
		if float(max_slope[0]) > slope_filter:
			expr = arcpy.sa.RemapRange([[0,slope_filter,0],[slope_filter,float(max_slope[0]),1]])
			print expr
		else:
			expr = arcpy.sa.RemapRange([[0,slope_filter,0]])
			print expr
		temp = arcpy.sa.Reclassify(Slope, "VALUE", expr, "DATA")
		temp.save(Excl_Slope)

		#-------------
		# LULC Exclusion Zones
		print "Step 6 - LULC Exclusion Zones"
		#-------------

		# Water
		expr = arcpy.sa. RemapValue([[0,1],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0],[13,0],[14,0],[15,0],[16,0]])
		temp = arcpy.sa.Reclassify(LULC_project, "Value", expr, "DATA")
		temp.save(Excl_Water)

		# Cities / Urban Areas
		expr = arcpy.sa. RemapValue([[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0],[13,1],[14,0],[15,0],[16,0]])
		temp = arcpy.sa.Reclassify(LULC_project, "Value", expr,"DATA")
		temp.save(Excl_Cities)

		# Crops
		expr = arcpy.sa. RemapValue([[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,1],[13,0],[14,0],[15,0],[16,0]])
		temp = arcpy.sa.Reclassify(LULC_project, "Value", expr, "DATA")
		temp.save(Excl_Crops)

		# Forest
		expr = arcpy.sa. RemapValue([[0,0],[1,1],[2,1],[3,1],[4,1],[5,1],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0],[13,0],[14,0],[15,0],[16,0]])
		temp = arcpy.sa.Reclassify(LULC_project, "Value", expr, "DATA")
		temp.save(Excl_Forest)
		
		if useProtect == "Y":
			#-------------
			# Protected Exclusion Zones
			print "Step 7 - Protected Exclusion Zones"
			#-------------
			# Resample Protect to match LULC
			arcpy.Resample_management(Protect_project, Protect_Resample, Resample_expr, "NEAREST")
		
			# Save as Exclusion Zone
			temp = Raster(Protect_Resample)
			temp.save(Excl_Protect)
	#-------------
	# Solar Resource Evaluation
	print "Step 8 - Solar Resource Evaluation"
	#-------------
	if analyzeSolar == "Y":

		# Retrieve Cell Sizes
		Solar_Cell_X = arcpy.GetRasterProperties_management (Solar_project, "CELLSIZEX")
		Solar_Cell_Y = arcpy.GetRasterProperties_management (Solar_project, "CELLSIZEY")

		# Determine inclusion zone
		if useProtect == "Y":
			print "useProtect == Y"
			if usePopulation == "Y":
				temp = Raster(Incl_Population) - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Crops)  |  Raster(Excl_Forest) |  Raster(Excl_Protect))
			else:
				temp = 1 - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Crops)  |  Raster(Excl_Forest) |  Raster(Excl_Protect))
		else:	
			if usePopulation == "Y":
				temp = Raster(Incl_Population) - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Crops)  |  Raster(Excl_Forest))
			else:
				temp = 1 - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Crops)  |  Raster(Excl_Forest))
		temp.save(Solar_Include)

		# Resample inclusion zone raster to match resource map
		expr = str(Solar_Cell_X[0]) + " " + str(Solar_Cell_Y[0])
		arcpy.Resample_management(Solar_Include, Solar_Include_Resample, expr, "NEAREST")

		# Apply inclusion zone to resource map
		temp = Raster(Solar_Include_Resample) * Raster(Solar_project)
		temp.save(Solar_Resource)

		# Convert resource map from to KWh/m^2/day to KWh/m^2/yr
		temp = Raster(Solar_Resource) * 365.25
		temp.save(Solar_Resource_Convert)

		# Calculate Annual Power Production in TWh per cell (Assumes cell dimensions are in meters)
		cell_area_m2 = (float(Solar_Cell_X[0]) * float(Solar_Cell_Y[0]))   # [m^2]
		cell_area_km2 = (float(Solar_Cell_X[0]) * float(Solar_Cell_Y[0])) / (1000 * 1000)  # [km^2]
		print "Solar Cell Area [km^2]: " + str(cell_area_km2)
		PV_efficiency = 0.165
		spacing_factor = 5
		MW_per_km2 = 5
		kWh_to_TWh = 1E-9
		temp = Raster(Solar_Resource_Convert) * cell_area_m2 * PV_efficiency / spacing_factor * kWh_to_TWh
		temp.save(Solar_Generation_Potential_TWh)

	#-------------
	# Wind Resource Evaluation
	print "Step 9 - Wind Resource Evaluation"
	#-------------
	if analyzeWind == "Y":

		# Retrieve Cell Sizes
		Wind_Cell_X = arcpy.GetRasterProperties_management (Wind_project, "CELLSIZEX")
		Wind_Cell_Y = arcpy.GetRasterProperties_management (Wind_project, "CELLSIZEY")

		# Determine inclusion zone
		if useProtect == "Y":
			print "useProtect == Y"
			if usePopulation == "Y":
				temp = Raster(Incl_Population) - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Forest)|  Raster(Excl_Protect))
			else:
				temp = 1 - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Forest)|  Raster(Excl_Protect))
		else:
			if usePopulation == "Y":
				temp = Raster(Incl_Population) - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Forest))
			else:
				temp = 1 - ( Raster(Excl_Slope)  |  Raster(Excl_Water)  |  Raster(Excl_Cities)  |  Raster(Excl_Forest))
		temp.save(Wind_Include)

		# Resample inclusion zone raster to match resource map
		expr = str(Wind_Cell_X[0]) + " " + str(Wind_Cell_Y[0])
		arcpy.Resample_management(Wind_Include, Wind_Include_Resample, expr, "NEAREST")

		# Apply inclusion zone to resource map
		temp = Raster(Wind_Include_Resample) * ( Wind_project)
		temp.save(Wind_Resource)

		# Calculate # of Full Load Hours
		temp = 565 * Raster(Wind_Resource) - 1745
		temp.save(Wind_Full_Load_Hours)

		# Filter Full Load Hours, acceptable range 0-4000
		min_range = 800
		max_range = 4000
		# arcpy.gp.RasterCalculator_sa("Con(\"%Wind_Full_Load_Hours%\">4000,4000,Con(\"%Wind_Full_Load_Hours%\"<800,0,\"%Wind_Full_Load_Hours%\"))", Wind_Full_Load_Hours__2_)
		temp = Con(Raster(Wind_Full_Load_Hours) < min_range, 0, Con(Raster(Wind_Full_Load_Hours) > max_range, max_range, Raster(Wind_Full_Load_Hours)))
		temp.save(Wind_Full_Load_Hours_filtered)

		# Calculate Annual Power Production in TWh per cell (Assumes cell dimensions are in meters)
		cell_area = (float(Wind_Cell_X[0]) * float(Wind_Cell_Y[0])) / (1000 * 1000)  # [km^2]
		print "Wind Cell Area [km^2]: " + str(cell_area)
		MW_per_km2 = 5
		MWh_to_TWh = 1E-6
		temp = cell_area * MW_per_km2 * Raster(Wind_Full_Load_Hours_filtered) * MWh_to_TWh
		temp.save(Wind_Generation_Potential_TWh)
		
	#-------------
	# End of Program
	print "End of Program"
	#-------------
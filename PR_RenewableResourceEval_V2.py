#=================================
# User Inputs
#=================================
# Location of Script
scriptDir = "C:\\Users\\Jeffrey\\Google Drive\\PR_GIS\\2_Tool"

# Analysis Types
analyzeSolar 	= "Y"
analyzeWind 	= "Y"
analyzeBiomass 	= "N" # Not Currently Available

# Analysis Options
usePopulation 		= "Y" 		# Y or N
useProtect 			= "Y" 		# Y or N
populationFilter 	= "5000" 	# Population per cell
populationRadius 	= "200"  	# Kilometers
skipExclusionZone   = "Y"		# Y or N - Only use if this step has already been completed

# Pre-processing Geodatabase
preGdb 		= "C:\\Users\\Jeffrey\\Google Drive\\PR_GIS\\1_preProcessing\\PR_PreProcessing.gdb"

# Intermediate Geodatabase
interGdb 	= "C:\\Users\\Jeffrey\\Google Drive\\PR_GIS\\2_Tool\\Intermediate.gdb"

# Results Geodatabase
resultsGdb 	= "C:\\Users\\Jeffrey\\Google Drive\\PR_GIS\\2_Tool\\Results.gdb"

# Pre-processing Naming Convention (all files are expected in the Pre-processing Geodatabase, preGdb)
LULC_project_name 		= "LULC_project"			# Always req'd
DEM_project_name 		= "DEM_project"				# Always req'd
Protect_project_name 	= "Protect_project"			# Req'd if useProtect = "Y"
population_project_name = "Population_project" 		# Req'd if usePopulation = "Y"
Solar_project_name 		= "Solar_project2"			# Req'd if analyzeSolar = "Y"
Wind_project_name 		= "Wind_project"			# Req'd if analyzeWind = "Y"
Outline_project_name 	= "Outline_project" 		# Not Required

# End of User Inputs

#=================================
# Run Program
#=================================
# Pack Inputs
analysisTypes = [analyzeSolar,analyzeWind,analyzeBiomass]
analysisOptions = [usePopulation,useProtect,populationFilter,populationRadius,skipExclusionZone]
databases = [preGdb,interGdb,resultsGdb]
namingConv = [LULC_project_name,DEM_project_name,Protect_project_name,population_project_name,Solar_project_name,Wind_project_name,Outline_project_name]

# Run Program
import os
os.chdir(scriptDir)
from RenewableResourceEval_V2 import *
Run_RenewableResourceEval_V2(analysisTypes, analysisOptions, databases, namingConv)
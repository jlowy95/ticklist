# Author Josh Lowy

# Define/Initialize basic parameters of the ticklist database such as the continent. 
# 'Area' object will be parent object for continent, 'Sub-Area' will be child class 
# for any/all actual areas with climbs.  Continents will be individual collections in the DB.

import pymongo


# initalizeContinents
# Creates an 'area' object for each of the continents except Antarctica

# addNewArea
# Will create a new subArea object in the currently selected area
# Properties (* denotes required at initialization):
# Name*, Parent (*Auto-filled by current selection), Description

# addNewClimb
# Will create a new climb object in the currently selected area
# Properties (* denotes required at initialization):
# Name*, Parent (*Auto-filled by current selection), Grade*, Danger (Default to None),
# Quality*, Description, Height, FA
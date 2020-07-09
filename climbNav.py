# Author Josh Lowy

# Connect to ticklist database
# Define functions for adding areas and climbs
# Use navigator to browse, edit, add, and delete

from pymongo import MongoClient

# Setup db client and database
client = MongoClient('mongodb://localhost:27017/')
db = client.MyTicksClimbs


# Initialize Navigator
# Define nav abilities:
# Locate area/climb, edit entry, add entry, delete entry



# defineNewArea
# Create a JSON object for an area
# Properties:
# name (area name), description, children (list of sub-areas/climbs, initialized as empty)
def defineNewArea(name, description, children):
    return {'name': name,
        'description': description,
        'children': []
        }

# Climb Types
# Used to distinguish type of entry
# Boulder: 0, Route: 1, Ice: 2
# Danger
# G: 0, PG-13: 1, R: 2, X: 3

# defineNewBoulder
# Create a JSON object for a boulder
# Properties:
# name, grade, danger, quality, description, height, fa
# Cannot have children
def defineNewBoulder(name, grade, danger, quality, description, height, fa):
    return {'name': name,
        'grade': grade,
        'danger': danger,
        'quality': quality,
        'description': description,
        'height': height,
        'fa': fa,
        'climbType': 0
        }

# defineNewRoute
# Create a JSON object for a route
# Properties:
# name, grade, danger, quality, routeType (list of sport/trad), description, pitches, height fa, committment
# Cannot have children
def defineNewRoute(name, grade, danger, quality, routeType, description, pitches, height, fa, commit):
    return {'name': name,
        'grade': grade,
        'danger': danger,
        'quality': quality,
        'routeType': routeType,
        'description': description,
        'pitches': pitches,
        'height': height,
        'fa': fa,
        'commit': commit,
        'climbType': 1
        }
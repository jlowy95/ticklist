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

# Basic welcome message
def welcome():
    print('Welcome!')

# Prompt user for next action, reloop if invalid option
def navOptions():
    valid = False
    while not valid:
        print('What would you like to do next?')
        ability = input("""Locate an area or climb [0] 
        Edit an existing entry [1]
        Add a new entry [2]
        Delete an existing entry [3]""")
        if type(ability) != int:
            ability = ability.lower()
            if 'loc' in ability:
                return 0
            elif 'ed' in ability:
                return 1
            elif 'ad' in ability:
                return 2
            elif 'del' in ability:
                return 3
            else:
                print("I'm sorry, I couldn't understand that. Let's try this again.")
            
# Direct to correct function           
def navOptionSelect(option_int):
    options = {0: 'locatefunction',
        1: 'editfunction',
        2: 'addfunction',
        3: 'delfunction'}
    options[option_int]


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
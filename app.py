# Author Josh Lowy 

# Flask app for MyTicks
# Connects to local MongoDB and allows for easy maintenance and logging of
# ticked climbs and tracking of ascents.

from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson import ObjectId
import json
import pprint

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/MyTicks"
mongo = PyMongo(app)

# Define collections for primary use
areas_col = mongo.db.areas
boulders_col = mongo.db.boulders
routes_col = mongo.db.routes

# Sample Entries
'''
Area
{
    _id: ObjectId(5f0d16cac6b1d534f316b56c),
    name: 'Wyoming',
    parentID: all-locations,
    path: all-locations$area/5f0d16cac6b1d534f316b56c,
    children: [],
    properties: {
        description: 'Wyoming is pretty.'
        images: [],
        'child_counts': {
            'areas': 0,
            'boulder': 0,
            'sport': 0,
            'trad': 0,
            'ice': 0
        },
        'elevation': '',
        'coords': {
            'lat': '',
            'lng': ''
        }
    }
}
Boulder
{
    _id: ObjectId(),
    name: 'Iron Man Traverse'
    parentID: '',
    path: all-locations$area/45398472$area/9287507$area/05275032$boulder/,
    properties: {
        grade: 4,
        quality: 4,
        danger: 0,
        height: 10,
        fa: 'Unknown',
        description: 'What a classic!',
        protection: 'Pads',
        images: [],
        'elevation': '',
        'coords': {
            'lat': '',
            'lng': ''
        }
    }
}
Route
{
    _id: ObjectId(),
    name: 'The Grand Wall'
    parentID: '',
    path: all-locations$area/45398472$area/9287507$area/05275032$route/,
    properties: {
        grade: 11.0,
        quality: 5,
        danger: 0,
        height: 1000,
        pitches: 8,
        committment: 3,
        fa: 'Unknown',
        description: 'What a classic!',
        protection: 'Double Rack',
        images: [],
        'elevation': '',
        'coords': {
            'lat': '',
            'lng': ''
        }
    }
}
'''

# Global Functions + Variables
api_routes = {
    'area': areas_col,
    'boulder': boulders_col,
    'route': routes_col
}

# getPathNames: For item in entry path, retrieve name
def getPathNames(entry_path):
    path_raw = entry_path.split('$')
    path_clean = []
    for link in path_raw:
        if link == 'all-locations':
            path_clean.append({'name': 'All Locations',
                'route': 'all-locations'})
        else:
            link_split = link.split('/')
            temp_entry = api_routes[link_split[0]].find_one({'_id': ObjectId(f'{link_split[1]}')})
            path_clean.append({'name': temp_entry['name'],
                'route': link
                })
    
    return path_clean


# getChildrenInfo: for item in children, retrieve info
def getChildrenInfo(children):
    if children:
        children_info = []
        for child in children:
            link_split = child.split('/')
            temp_entry = api_routes[link_split[0]].find_one({'_id': ObjectId(f'{link_split[1]}')})
            children_info.append({'name': temp_entry['name'],
                'route': child
                })
            
        return children_info
    else:
        return []


# simplifyArray: takes JSON form array and converts it to single python dictionary
def simplifyArray(json_request):
    return {field['name']: field['value'] for field in json_request}

# updateChildren: update the children property based on if there is or isnt already info there
def updateChildren(parent, new_entry):
    if parent['children'] == None: 
        areas_col.update_one({'_id': parent['_id']}, 
            {'$set': {
                'children': ['area/'+str(new_entry.inserted_id)]
                }})
    else:
        parent['children'].append(f'area/{str(new_entry.inserted_id)}')
        areas_col.update_one({'_id': parent['_id']}, 
            {'$set': {
                'children': parent['children']
                }})
        

# validateAddition: re-checks all fields are filled and valid,
# then checks database for new entry details of parent and name
# Returns a tuple corresponding to the following:
# (validated boolean, error code if error, additional info for error handling)
def validateAddition(loc_type, new_loc):
    print('Validating...')
    # Check for all fields filled
    for field in new_loc.keys():
        if new_loc[field] == '':
            # Invalid field - An Error occurred, please try again.
            return (False, 1, (loc_type, new_loc['parentID']))
    # Else continue

    # Check for valid grade, danger, committment based on loc_type

    # Check for duplicate entry
    validated =  api_routes[loc_type].find_one({'parentID': new_loc['parentID'], 'name': new_loc['name']})
    if validated:
        return (False, 2, (loc_type, validated['_id']))
    else:
        return (True,)


# validationErrorProtocol: handles any errors found by validateAddition
def validationErrorProtocol(error_code, data):
    print("Handling Error")
    if error_code == 1:
        # Unfilled/Invalid Field - likely due to unintended page manipulation
        # data = (loc_type, new_loc['parentID'])
        # Redirect to addEntry of loc_type of the parent area
        return {'redirect': f'/add-entry/{data[0]}/{str(data[1])}',
            'error': 1}
    elif error_code == 2:
        # Duplicate Entry
        # data = (loc_type, validated['_id']) (the _id of the existing entry)
        # Redirect to existing entry's page
        return {'redirect': f'/{data[0]}/{str(data[1])}',
            'error': 2}


# addArea: inserts new area entry and updates parent area
def addArea(new_area):
    # Validate if new entry
    validated = validateAddition('area', new_area)
    if validated[0]:
        # Find parent for path extension
        parent = areas_col.find_one({'_id': ObjectId(f'{new_area["parentID"]}')})
        # Initialize new entry
        new_entry = areas_col.insert_one({
            'name': new_area['name'],
            'parentID': new_area['parentID'],
            'path': '',
            'children': [],
            'properties': {
                'description': new_area['description'],
                'images': [],
                'child_counts': {
                    'areas': 0,
                    'boulder': 0,
                    'sport': 0,
                    'trad': 0,
                    'ice': 0
                },
                'elevation': '',
                'coords': {
                    'lat': '',
                    'lng': ''
                }
            }
        })
        # Update new entry path
        areas_col.update_one({'_id': new_entry.inserted_id}, 
            {'$set': {
                'path': parent['path']+'$area/'+str(new_entry.inserted_id)
                }})
        # Update parent children
        updateChildren(parent, new_entry)

        # Return and redirect
        print(f'Redirecting to area/{new_entry.inserted_id}')
        return {'redirect': f'/area/{str(new_entry.inserted_id)}',
            'success': 'New entry added successfully!'}
    else:
        # Else, error - handle the error and return
        print(f"Error Code: {validated[1]}")
        return validationErrorProtocol(validated[1], validated[2])


# addBoulder: inserts new boulder entry and updates parent area
def addBoulder(new_boulder):
    # Validate if new entry
    validated = validateAddition('boulder', new_boulder)
    if validated[0]:
        # Find parent for path extension
        parent = boulders_col.find_one({'_id': ObjectId(f'{new_boulder["parentID"]}')})
        # Initialize new entry
        new_entry = boulders_col.insert_one({
            'name': new_boulder['name'],
            'parentID': new_boulder['parentID'],
            'path': '',
            'children': [],
            'properties': {
                'grade': vermin2Int(new_boulder['grade']), # Write vermin2Int!!!
                'quality': -2,
                'danger': new_boulder['danger'],
                'height': new_boulder['height'],
                'fa': new_boulder['fa'],
                'description': new_boulder['description'],
                'protection': new_boulder['protection'],
                'images': [],
                'elevation': '',
                'coords': {
                    'lat': '',
                    'lng': ''
                }
            }
        })
        # Update new entry path
        boulders_col.update_one({'_id': new_entry.inserted_id}, 
            {'$set': {
                'path': parent['path']+'$boulder/'+str(new_entry.inserted_id)
                }})
        # Update parent children
        updateChildren(parent, new_entry)

        # Return and redirect
        print(f'Redirecting to boulder/{new_entry.inserted_id}')
        return {'redirect': f'/boulder/{str(new_entry.inserted_id)}',
            'success': 'New entry added successfully!'}
    else:
        # Else, error - handle the error and return
        print(f"Error Code: {validated[1]}")
        return validationErrorProtocol(validated[1], validated[2])


# addRoute: inserts new boulder entry and updates parent area
def addRoute(new_route):
    # Validate if new entry
    validated = validateAddition('route', new_route)
    if validated[0]:
        # Find parent for path extension
        parent = routes_col.find_one({'_id': ObjectId(f'{new_route["parentID"]}')})
        # Initialize new entry
        new_entry = routes_col.insert_one({
            'name': new_route['name'],
            'parentID': new_route['parentID'],
            'path': '',
            'children': [],
            'properties': {
                'grade': yos2Int(new_route['grade']), # Write yos2Int!!!
                'quality': -2,
                'danger': new_route['danger'],
                'height': new_route['height'],
                'pitches': new_route['pitches'],
                'committment': new_route['committment'],
                'fa': new_route['fa'],
                'description': new_route['description'],
                'protection': new_route['protection'],
                'images': [],
                'elevation': '',
                'coords': {
                    'lat': '',
                    'lng': ''
                }
            }
        })
        # Update new entry path
        routes_col.update_one({'_id': new_entry.inserted_id}, 
            {'$set': {
                'path': parent['path']+'$route/'+str(new_entry.inserted_id)
                }})
        # Update parent children
        updateChildren(parent, new_entry)

        # Return and redirect
        print(f'Redirecting to route/{new_entry.inserted_id}')
        return {'redirect': f'/route/{str(new_entry.inserted_id)}',
            'success': 'New entry added successfully!'}
    else:
        # Else, error - handle the error and return
        print(f"Error Code: {validated[1]}")
        return validationErrorProtocol(validated[1], validated[2])

'''--------------------------------------- ROUTES ---------------------------------------'''
# Home Route
# home page with secondary tools/info
@app.route('/')
def index():
    return render_template('index.html')


# All Locations
# Route-guide home/full directory
@app.route('/all-locations')
def allLocations():
    # Template to be filled when database is properly initialized
    return render_template('allLocations.html')


# API Routes
# Loads the corresponding page type to the entry requested
@app.route('/area/<entry_id>')
def area(entry_id):
    print(f'Entry: {entry_id}')
    try:
        # Retrieve Entry
        entry = areas_col.find_one({'_id': ObjectId(f'{entry_id}')})
        path = getPathNames(entry['path'])
        children = getChildrenInfo(entry['children'])
        print(f'Entry: {entry}')
        return render_template('area.html', area=entry, path=path, children=children)
    except Exception as e:
        print(e)
        return render_template('index.html')

@app.route('/boulder/<entry_id>')
def boulder(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = boulders_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        return render_template('boulder.html')
    except Exception as e:
        print(e)
        return render_template('index.html')

@app.route('/route/<entry_id>')
def routeClimb(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = routes_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        return render_template('route.html')
    except Exception as e:
        print(e)
        return render_template('index.html')


# Search query route
@app.route('/search/<search_terms>')
def search(search_terms):
    print(search_terms)


# Entry Management
# addEntry (adds an entry to the current area)
@app.route('/add-entry/<entry_type>/<parentID>')
def addEntry(entry_type, parentID):
    parent = areas_col.find_one({'_id': ObjectId(f'{parentID}')})
    if entry_type == 'area':
        return render_template('addArea.html', parent=parent)
    elif entry_type == 'boulder':
        return render_template('addBoulder.html')
    elif entry_type == 'route':
        return render_template('addRoute.html')
    else:
        print('Error: invalid entry_type')
        redirect(url_for('area', entry_id=parentID))

# submitChanges - POST route processes changes to db
# then redirects to new page if successful
@app.route('/submit-changes', methods=['POST'])
def submitChanges():
    inputted_data = simplifyArray(request.get_json())
    # print(inputted_data)
    # Switch for correct actions
    change_options = {
        'area': addArea(inputted_data), # add new area functions plus returns redirect to new area
        'boulder': '',
        'route': '',
        'edit': ''
    }
    return change_options[inputted_data['change-type']]

# editEntry (allows edits to the current entry)
@app.route('/edit-entry/<entry_type>/<entry_id>')
def editEntry(entry_type, entry_id):
    print('placeholder')



if __name__ == '__main__':
    app.run(debug=True)

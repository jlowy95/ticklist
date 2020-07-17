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

# Sample Entry
'''
{
    _id: ObjectID(5f0d16cac6b1d534f316b56c),
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
    children_info = []
    for child in children:
        link_split = child.split('/')
        temp_entry = api_routes[link_split[0]].find_one({'_id': ObjectId(f'{link_split[1]}')})
        children_info.append({'name': temp_entry['name'],
            'route': child
            })
        
    return children_info

# simplifyArray: takes JSON form array and converts it to single python dictionary
def simplifyArray(json_request):
    return {field['name']: field['value'] for field in json_request}

#updateChildren: update the children property based on if there is or isnt already info there
def updateChildren(parent, new_entry):
    if parent['children'] == None:
        return ['area/'+str(new_entry.inserted_id)]
    else:
        return parent['children'].append(f'area/{str(new_entry.inserted_id)}')

# addArea: inserts new area entry and updates parent area
def addArea(new_area):
    # print('Adding area!')
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
    areas_col.update_one({'_id': parent['_id']}, 
        {'$set': {
            'children': updateChildren(parent, new_entry)
            # Updates counts??
            }})
    print(f'Redirecting to area/{new_entry.inserted_id}')
    return ('area', new_entry.inserted_id)
    # redirect(url_for('area', entry_id=new_entry.inserted_id))



# Home Route
# home page with secondary tools/info
@app.route('/')
def index():
    return render_template('index.html')


# All Locations
# Route-guide home/full directory
@app.route('/all-locations')
def allLocations():
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
        'area': addArea(inputted_data), # add new area functions plus redirect
        'boulder': '',
        'route': '',
        'edit': ''
    }
    redir_tuple = change_options[inputted_data['change-type']]
    return redirect(url_for(redir_tuple[0], entry_id=redir_tuple[1]))
    

# editEntry (allows edits to the current entry)
@app.route('/edit-entry/<entry_type>/<entry_id>')
def editEntry(entry_type, entry_id):
    print('placeholder')



if __name__ == '__main__':
    app.run(debug=True)

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
    inputted_data = request.get_json()
    print(inputted_data)
    return inputted_data
    # Switch for correct actions
    # change_options = {
    #     'area': '', # add new area functions plus redirect
    #     'boulder': '',
    #     'route': '',
    #     'edit': ''
    # }
    # change_options[inputted_data]['change-type']
    

# editEntry (allows edits to the current entry)
@app.route('/edit-entry/<entry_type>/<entry_id>')
def editEntry(entry_type, entry_id):
    print('placeholder')



if __name__ == '__main__':
    app.run(debug=True)

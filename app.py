# Author Josh Lowy 

# Flask app for MyTicks
# Connects to local MongoDB and allows for easy maintenance and logging of
# ticked climbs and tracking of ascents.

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_pymongo import PyMongo
import mysql.connector
from bson import ObjectId
import datetime
import json
import pprint

app = Flask(__name__)

# Initialize SQLAlchemy connection
# MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:joshstemppassword@localhost/MyTicksClimbs"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Postrgesql
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://Josh:lowy@localhost/MyTicksClimbs"
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
 

# SQL Models
class AreaModel(db.Model):
    __tablename__ = 'areas'

    # area_type: {
    # 0: No children,
    # 1: Areas,
    # 2: Boulders/Routes}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    path = db.Column(db.String(150))
    description = db.Column(db.String(500))
    elevation = db.Column(db.Integer)
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    area_type = db.Column(db.Integer)
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, description, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.description = description
        self.elevation = elevation
        self.lat = lat
        self.lng = lng
        self.area_type = 0
        self.date_inserted = datetime.datetime.now()
    
    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'path': self.path
            },
            'properties': {
                'description': self.description,
                'elevation': self.elevation,
                'coords': {
                    'lat': self.lat,
                    'lng': self.lng
                }
            },
            'area_type': self.area_type,
            'date_inserted': self.date_inserted
        }

class BoulderModel(db.Model):
    __tablename__ = 'boulders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    path = db.Column(db.String(150))
    order = db.Column(db.Integer)
    grade = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    danger = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer)
    fa = db.Column(db.String(50))
    description = db.Column(db.String(500))
    pro = db.Column(db.String(100))
    elevation = db.Column(db.Integer)
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, order, grade, quality, danger, height, fa, description, pro, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.order = 0
        self.grade = grade
        self.quality = quality
        self.danger = danger
        self.height = height
        self.fa = fa
        self.description = description
        self.pro = pro
        self.elevation = elevation
        self.lat = lat
        self.lng = lng
        self.date_inserted = datetime.datetime.now()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'path': self.path,
                'order': self.order
            },
            'properties': {
                'grade': self.grade,
                'danger': self.danger,
                'height': self.height,
                'fa': self.fa,
                'description': self.description,
                'pro': self.pro,
                'elevation': self.elevation,
                'coords': {
                    'lat': self.lat,
                    'lng': self.lng
                }
            },                
            'date_inserted': self.date_inserted
        }

class RouteModel(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    path = db.Column(db.String(150))
    order = db.Column(db.Integer)
    grade = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    danger = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer)
    pitches = db.Column(db.Integer)
    committment = db.Column(db.String(3))
    fa = db.Column(db.String(50))
    description = db.Column(db.String(500))
    pro = db.Column(db.String(100))
    elevation = db.Column(db.Integer)
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, order, grade, quality, danger, height, pitches, committment, fa, description, pro, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.order = 0
        self.grade = grade
        self.quality = quality
        self.danger = danger
        self.height = height
        self.pitches = pitches
        self.committment
        self.fa = fa
        self.description = description
        self.pro = pro
        self.elevation = elevation
        self.lat = lat
        self.lng = lng
        self.date_inserted = datetime.datetime.now()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'path': self.path,
                'order': self.order
            },
            'properties': {
                'grade': self.grade,
                'danger': self.danger,
                'height': self.height,
                'pitches': self.pitches,
                'committment': self.committment,
                'fa': self.fa,
                'description': self.description,
                'pro': self.pro,
                'elevation': self.elevation,
                'coords': {
                    'lat': self.lat,
                    'lng': self.lng
                }
            },                
            'date_inserted': self.date_inserted
        }

# Use flask_pymongo to set up mongo connection
# app.config["MONGO_URI"] = "mongodb://localhost:27017/MyTicks"
# mongo = PyMongo(app)

# Define collections for primary use
# areas_col = mongo.db.areas
# boulders_col = mongo.db.boulders
# routes_col = mongo.db.routes

# Sample Entries
'''
Area
{
    id: 756,
    name: 'Wyoming',
    parent_id: 1,
    parent_name: 'All Locations',
    properties: {
        description: 'Wyoming is pretty.'
        images: [],
        'elevation': '',
        'coords': {
            'lat': '',
            'lng': ''
        }
    }
}
Boulder
{
    id: 4234,
    name: 'Iron Man Traverse'
    parent_id: 43,
    parent_name: 'Buttermilks',
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
    id: 98753,
    name: 'The Grand Wall'
    parent_id: 64,
    parent_name: 'The Chief',
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
# api_routes = {
#     'area': areas_col,
#     'boulder': boulders_col,
#     'route': routes_col
# }

common_html = {
    'nav': '''<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="#">MyTicks</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
      
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto">
            <li class="nav-item active">
              <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">Link</a>
            </li>
            <!-- <li class="nav-item">
              <a class="nav-link disabled" href="#">Disabled</a>
            </li> -->
          </ul>
          <form class="form-inline my-2 my-lg-0">
            <input class="form-control mr-sm-2" type="text" placeholder="Search MyTicks" aria-label="Search">
            <button class="btn btn-outline-light my-2 my-sm-0" type="submit">Search</button>
          </form>
        </div>
        </nav>''',
    'title_start': '<title>MyTicks',
    'title_end': '</title>',
    'error': '''<div class="alert alert-warning alert-dismissible fade show" role="alert" id="error-element">
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            <strong>Warning!</strong>&nbsp;&nbsp;<p id="error-text" style="display: inline"></p>
        </div>''',
    'scripts': '''<!-- Ajax/Jquery -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
        <!-- Bootstrap -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
        <!-- D3 -->
        <script src="https://d3js.org/d3.v5.min.js"></script>
        '''
}

# getPathNames: For item in entry path, retrieve name
def getPathNames(path):
    path_raw = [step.split('/') for step in path.split('$')]
    path_clean = []
    for step in path_raw:
        path_clean.append({'name': step[1], 'route':f"area/{step[0]}/{step[1]}"})
    return path_clean
    # flag = False
    # while not flag:
    #     if parent['id'] == 1 and parent['name'] == 'All Locations':
    #         path.append({'name': parent['name'],
    #         'route': f"area/{parent['id']}/{parent['name']}"})
    #         flag = True
    #         # print('getPathNames flagged')
    #     else:
    #         path.append({'name': parent['name'],
    #         'route': f"area/{parent['id']}/{parent['name']}"})
    #         parent = db.session.query(AreaModel)\
    #             .filter(AreaModel.parent_id==parent['id'])\
    #             .filter(AreaModel.parent_name==parent['name'])\
    #             .toJSON()['parent']
    # # print(f'getPathNames pre-return: {path.reverse()}')
    # path.reverse()
    # return path


# getChildrenInfo: for item in children, retrieve info
def getChildrenInfo(entry):
    if entry['area_type'] == 0:
        return []
    elif entry['area_type'] == 1:
        children_info = []
        children = db.session.query(AreaModel)\
            .filter(AreaModel.parent_id==entry['id'])\
            .filter(AreaModel.parent_name==entry['name'])\
            .all()
        if type(children)==list:
            for child in children:
                children_info.append({'name': child.name,
                    'route': f"area/{child.id}/{child.name}"})
        else:
            children_info.append({'name': children.name,
                    'route': f"area/{children.id}/{children.name}"})
        return {'sorted': children_info}
    elif entry['area_type'] == 2:
        #
        # ADD BOULDER/ROUTE API ROUTE PREFIX
        #
        sorted_info = []
        unsorted_info = []
        # Check boulders
        boulders = db.session.query(BoulderModel.id, BoulderModel.name, BoulderModel.order)\
            .filter(BoulderModel.parent_id==entry['id'])\
            .filter(BoulderModel.parent_name==entry['name'])\
            .all()
        # Check routes
        routes = db.session.query(RouteModel.id, RouteModel.name, RouteModel.order)\
            .filter(RouteModel.parent_id==entry['id'])\
            .filter(RouteModel.parent_name==entry['name'])\
            .all()
        # Union boulders + routes and sort
        children = boulders.union(routes).order_by(BoulderModel.order)
        # Append info to corresponding lists
        for child in children:
            if child.order == 0:
                unsorted_info.append({'name': child['name'],
                'route': f"{child['id']}/{child['name']}"})
            else:
                children_info.append({'name': child['name'],
                    'route': f"{child['id']}/{child['name']}"})

        if unsorted_info == []:
            return {'sorted': sorted_info}
        else:
            return {'sorted': sorted_info, 'unsorted': unsorted_info}
        


# simplifyArray: takes JSON form array and converts it to single python dictionary
def simplifyArray(json_request):
    return {field['name']: field['value'] for field in json_request}

# # updateChildren: update the children property based on if there is or isnt already info there
# def updateChildren(parent, new_entry):
#     if parent['children'] == None: 
#         areas_col.update_one({'_id': parent['_id']}, 
#             {'$set': {
#                 'children': ['area/'+str(new_entry.inserted_id)]
#                 }})
#     else:
#         parent['children'].append(f'area/{str(new_entry.inserted_id)}')
#         areas_col.update_one({'_id': parent['_id']}, 
#             {'$set': {
#                 'children': parent['children']
#                 }})
        

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
            return (False, 1, (loc_type, new_loc))
    # Else continue

    # Check for valid grade, danger, committment based on loc_type

    # Check for duplicate entry
    type2model = {'area': AreaModel,'boulders': BoulderModel, 'route': RouteModel}
    model = type2model[loc_type]
    validated =  db.session.query(model)\
        .filter(model.parent_id == new_loc['parent_id'])\
        .filter(model.parent_name==new_loc['parent_name'])\
        .filter(model.name==new_loc['name'])\
        .first()
    if validated:
        return (False, 2, (loc_type, validated))
    else:
        return (True,)


# validationErrorProtocol: handles any errors found by validateAddition
def validationErrorProtocol(error_code, data):
    print("Handling Error")
    if error_code == 1:
        # Unfilled/Invalid Field - likely due to unintended page manipulation
        # data = (loc_type, new_loc['parentID'])
        # Redirect to addEntry of loc_type of the parent area
        return {'redirect': f"/add-entry/{data[0]}/{str(data[1]['parent_id'])}/{str(data[1]['parent_name'])}",
            'error': 1}
    elif error_code == 2:
        # Duplicate Entry
        # data = (loc_type, validated['_id']) (the _id of the existing entry)
        # Redirect to existing entry's page
        return {'redirect': f"/{data[0]}/{str(data[1]['id'])}/{str(data[1]['name'])}",
            'error': 2}


# addArea: inserts new area entry and updates parent area
def addArea(new_area):
    # Validate if new entry
    validated = validateAddition('area', new_area)
    if validated[0]:
        # Initialize new entry
        new_entry = AreaModel(
            name=new_area['name'],
            parent_id=new_area['parent_id'],
            parent_name=new_area['parent_name'],
            path=new_area['parent_path']+f"${new_area['parent_id']}/{new_area['parent_name']}",
            description=new_area['description'],
            elevation=None,
            lat=None,
            lng=None
        )

        # Commit
        db.session.add(new_entry)
        db.session.commit()

        # Return and redirect
        print(f"Redirecting to area/{new_entry.id}/{new_entry.name}")
        return {'redirect': f"/area/{str(new_entry.id)}/{str(new_entry.name)}",
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
    return render_template('index.html', common=common_html)


# All Locations
# Route-guide home/full directory
@app.route('/1/All-Locations')
def allLocations():
    # Template to be filled when database is properly initialized
    return render_template('allLocations.html', common=common_html)


# API Routes
# Loads the corresponding page type to the entry requested
@app.route('/area/<entry_id>/<entry_name>')
def area(entry_id, entry_name):
    print(f'Entry: {entry_id}/{entry_name}')
    try:
        # Retrieve Entry
        entry = db.session.query(AreaModel)\
            .filter(AreaModel.id==entry_id)\
            .filter(AreaModel.name==entry_name)\
            .first().toJSON()
        path = getPathNames(entry['parent']['path'])
        children = getChildrenInfo(entry)
        return render_template('area.html', area=entry, path=path, children=children, common=common_html)
    except Exception as e:
        print(e)
        return render_template('404.html', common=common_html)

@app.route('/boulder/<entry_id>')
def boulder(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = boulders_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        return render_template('boulder.html', common=common_html)
    except Exception as e:
        print(e)
        return render_template('404.html', common=common_html)

@app.route('/route/<entry_id>')
def routeClimb(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = routes_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        return render_template('route.html', common=common_html)
    except Exception as e:
        print(e)
        return render_template('404.html', common=common_html)


# Search query route
@app.route('/search/<search_terms>')
def search(search_terms):
    print(search_terms)


# Entry Management
# addEntry (adds an entry to the current area)
@app.route('/add-entry/<entry_type>/<parent_id>/<parent_name>')
def addEntry(entry_type, parent_id, parent_name):
    parent = db.session.query(AreaModel)\
            .filter(AreaModel.id==parent_id)\
            .filter(AreaModel.name==parent_name)\
            .first().toJSON()
    print(parent)
    if entry_type == 'area':
        return render_template('addArea.html', parent=parent, common=common_html)
    elif entry_type == 'boulder':
        return render_template('addBoulder.html', common=common_html)
    elif entry_type == 'route':
        return render_template('addRoute.html', common=common_html)
    else:
        print('Error: invalid entry_type')
        redirect(url_for('area', entry_id=parent_id, entry_name=parent_name))

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

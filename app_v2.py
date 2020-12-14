'''
MyTicks: A Climbing Journal Webapp
Made by Josh Lowy
Copyright 2020 Josh Lowy

Flask based application connects to local SQL database.
Designed for easy maintenance and logging of ticked climbs
and for the tracking of ascents.
'''


# Imported Modules
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import func
from flask_migrate import Migrate
import mysql.connector
from bson import ObjectId
import datetime
import json
import pprint

# Initialize Flask app
app = Flask(__name__)

# Initialize SQLAlchemy connection
# MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:joshstemppassword@localhost/MyTicksTest"

# Connect SQL database to Flask app
db = SQLAlchemy(app)
migrate = Migrate(app, db)
 

# SQL Models
# These are translations of the tables in the db
# Area and Climb have toJSON fn for simplified data retrieval in templates

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
    directions = db.Column(db.String(500))
    elevation = db.Column(db.Integer)
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    area_type = db.Column(db.Integer)
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, description, directions, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.description = description
        self.directions = directions
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
                'directions': self.directions,
                'elevation': self.elevation,
                'coords': {
                    'lat': self.lat,
                    'lng': self.lng
                }
            },
            'area_type': self.area_type,
            'date_inserted': self.date_inserted
        }


class ClimbModel(db.Model):
    __tablename__ = 'climbs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    climb_type = db.Column(db.String(10), nullable=False)
    position = db.Column(db.Integer)
    quality = db.Column(db.Integer, nullable=False)
    danger = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer)
    fa = db.Column(db.String(50))
    description = db.Column(db.String(500))
    pro = db.Column(db.String(100))
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, climb_type, position, quality, danger, height, fa, description, pro):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.climb_type = climb_type
        self.position = 0
        self.quality = quality
        self.danger = danger
        self.height = height
        self.fa = fa
        self.description = description
        self.pro = pro
        self.date_inserted = datetime.datetime.now()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'position': self.position
            },
            'properties': {
                'quality': self.quality,
                'danger': dangerInt2Movie[self.danger],
                'height': self.height,
                'fa': self.fa,
                'description': self.description,
                'pro': self.pro
            },        
            'climb_type': self.climb_type,        
            'date_inserted': self.date_inserted
        }


class BoulderModel(db.Model):
    __tablename__ = 'boulders'

    id = db.Column(db.Integer, db.ForeignKey('climbs.id'),primary_key=True, nullable=False)
    grade = db.Column(db.Float, nullable=False)

    def __init__(self, id, grade):
        self.id = id
        self.grade = grade


class RouteModel(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.Float, nullable=False)
    pitches = db.Column(db.Integer, nullable=False)
    committment = db.Column(db.String(3))
    route_type = db.Column(db.Integer, nullable=False)

    def __init__(self, grade, pitches, committment, route_type):
        self.grade = grade
        self.pitches = pitches
        self.committment
        self.route_type = route_type


class TagsModel(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)

    def __init__(self, title):
        self.title = title


class TagsClimbsModel(db.Model):
    __tablename__ = 'tagClimb'

    climb_id = db.Column(db.Integer, db.ForeignKey(ClimbModel.id), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey(TagsModel.id), primary_key=True)

    def __init__(self, climb_id, tag_id):
        self.climb_id = climb_id
        self.tag_id = tag_id


# Global Functions + Variables

# errors: dictionary containing different error messages to be displayed when page issues occur
errors = {
    '403': {
        'title':'403 - Forbidden',
        'description':"That action is prohibited, please contact an administrator if you have questions about this page.",
        'secondary':"Attempting to add an area or boulder/route to an area designated for the other can result in this redirect."
    },
    '404': {
        'title':'404 - Woops, bad topo!',
        'description':"We couldn't find that spot in our guidebooks, try double checking your spelling or check out the search.",
        'secondary':"If what you're looking for still isn't there, consider adding it!"
    }
}

# dangerInt2Movie: dictionary to translate the stored Danger integer from db to common text value
dangerInt2Movie = {
    0:'',
    1:'PG-13',
    2:'R',
    3:'X'
}

# route_types: dictionary to translate route_type value from db to common text value.  
# The two stored values for each are used interchangeably in different template locations.
route_types = {
    None: {'short':'','long':''},
    0: {'short':'S','long':'Sport'},
    1: {'short':'T','long':'Trad'},
    2: {'short':'DWS','long':'Deep Water Solo'}
}

# likeCommonTags: dictionary of common tags for climbs 
# with their values being a list of common mispellings/abbreviations/variants
likeCommonTags = {
    "dirty": ["dirt"],
    "reachy": ["reach"],
    "technical": ["tech", "tricky"],
    "highball": ["tall", "high", "high ball"],
    "chossy": ["choss", "flakey", "loose"],
    "bad landing": ["danger", "landing"],
    "warmup": ["warm-up"],
    "pinchy": ["pinch", "pinches", "pinchey", "pinchs"],
    "crimpy": ["crimp", "crimps", "crimpey", "crimpes"],
    "compstyle": ["compy", "competition", "competition style"],
    "sandbagged": ["bagged", "sandbag"],
    "huecos": ["heucos", "heuco", "hueco", "hueco-y"],
    "pockety": ["pocket", "pockets", "pocketey"],
    "dyno": ["dyanmic", "dynos", "dyno-y"],
    "eliminate": ["elim"],
    "manufactured": ["chipped", "manufacture"]
}

# boulderInt2Grade: translates concensus boulder difficulty values to common V/Font grades
def boulderInt2Grade(floatDifficulty):
    if floatDifficulty < -0.66:
        return {'usa':'VB', 'euro':'3'}
    elif floatDifficulty < -0.34:
        return {'usa':'V0-', 'euro':'3+'}
    elif floatDifficulty < 0.34:
        return {'usa':'V0', 'euro':'4'}
    elif floatDifficulty < 0.66:
        return {'usa':'V0+', 'euro':'4+'}
    elif floatDifficulty < 1.34:
        return {'usa':'V1', 'euro':'5'}
    elif floatDifficulty < 1.66:
        return {'usa':'V1-2', 'euro':'5+'}
    elif floatDifficulty < 2.34:
        return {'usa':'V2', 'euro':'5+'}
    elif floatDifficulty < 2.66:
        return {'usa':'V2-3', 'euro':'6A'}
    elif floatDifficulty < 3.34:
        return {'usa':'V3', 'euro':'6A'}
    elif floatDifficulty < 3.66:
        return {'usa':'V3-4', 'euro':'6A+'}
    elif floatDifficulty < 4.34:
        return {'usa':'V4', 'euro':'6B'}
    elif floatDifficulty < 4.66:
        return {'usa':'V4-5', 'euro':'6B+'}
    elif floatDifficulty < 5.34:
        return {'usa':'V5', 'euro':'6C'}
    elif floatDifficulty < 5.66:
        return {'usa':'V5-6', 'euro':'6C+'}
    elif floatDifficulty < 6.34:
        return {'usa':'V6', 'euro':'7A'}
    elif floatDifficulty < 6.66:
        return {'usa':'V6-7', 'euro':'7A+'}
    elif floatDifficulty < 7.34:
        return {'usa':'V7', 'euro':'7A+'}
    elif floatDifficulty < 7.66:
        return {'usa':'V7-8', 'euro':'7B'}
    elif floatDifficulty < 8.34:
        return {'usa':'V8', 'euro':'7B'}
    elif floatDifficulty < 8.66:
        return {'usa':'V8-9', 'euro':'7B+'}
    elif floatDifficulty < 9.34:
        return {'usa':'V9', 'euro':'7C'}
    elif floatDifficulty < 9.66:
        return {'usa':'V9-10', 'euro':'7C'}
    elif floatDifficulty < 10.34:
        return {'usa':'V10', 'euro':'7C+'}
    elif floatDifficulty < 10.66:
        return {'usa':'V10-11', 'euro':'7C+'}
    elif floatDifficulty < 11.34:
        return {'usa':'V11', 'euro':'8A'}
    elif floatDifficulty < 11.66:
        return {'usa':'V11-12', 'euro':'8A'}
    elif floatDifficulty < 12.34:
        return {'usa':'V12', 'euro':'8A+'}
    elif floatDifficulty < 12.66:
        return {'usa':'V12-13', 'euro':'8A+'}
    elif floatDifficulty < 13.34:
        return {'usa':'V13', 'euro':'8B'}
    elif floatDifficulty < 13.66:
        return {'usa':'V13-14', 'euro':'8B'}
    elif floatDifficulty < 14.34:
        return {'usa':'V14', 'euro':'8B+'}
    else:
        return {'usa':'V14+', 'euro':'8B+'}
# routeInt2Grade: translates concensus route difficulty values to common YDS/French grades
def routeInt2Grade(floatDifficulty):
    if floatDifficulty < -0.66:
        return {'usa':'Easy 5th', 'euro':'1'}
    elif floatDifficulty < -0.34:
        return {'usa':'5.4', 'euro':'1'}
    elif floatDifficulty < 0.34:
        return {'usa':'5.4', 'euro':'2'}
    elif floatDifficulty < 0.66:
        return {'usa':'5.5', 'euro':'3'}
    elif floatDifficulty < 1.34:
        return {'usa':'5.5', 'euro':'3'}
    elif floatDifficulty < 1.66:
        return {'usa':'5.6', 'euro':'4'}
    elif floatDifficulty < 2.34:
        return {'usa':'5.6', 'euro':'4'}
    elif floatDifficulty < 2.66:
        return {'usa':'5.7', 'euro':'4+'}
    elif floatDifficulty < 3.34:
        return {'usa':'5.7', 'euro':'4+'}
    elif floatDifficulty < 3.66:
        return {'usa':'5.8', 'euro':'5a'}
    elif floatDifficulty < 4.34:
        return {'usa':'5.8', 'euro':'5a'}
    elif floatDifficulty < 4.66:
        return {'usa':'5.9', 'euro':'5b'}
    elif floatDifficulty < 5.34:
        return {'usa':'5.9', 'euro':'5b'}
    elif floatDifficulty < 5.66:
        return {'usa':'5.9+', 'euro':'5b/+'}
    elif floatDifficulty < 6.34:
        return {'usa':'5.10a', 'euro':'6a'}
    elif floatDifficulty < 6.66:
        return {'usa':'5.10b', 'euro':'6a/+'}
    elif floatDifficulty < 7.34:
        return {'usa':'5.10b', 'euro':'6a+'}
    elif floatDifficulty < 7.66:
        return {'usa':'5.10c', 'euro':'6a+/b'}
    elif floatDifficulty < 8.34:
        return {'usa':'5.10c', 'euro':'6b'}
    elif floatDifficulty < 8.66:
        return {'usa':'5.10d', 'euro':'6b/+'}
    elif floatDifficulty < 9.34:
        return {'usa':'5.10d', 'euro':'6b+'}
    elif floatDifficulty < 9.66:
        return {'usa':'5.11a', 'euro':'6b+/c'}
    elif floatDifficulty < 10.34:
        return {'usa':'5.11a', 'euro':'6c'}
    elif floatDifficulty < 10.66:
        return {'usa':'5.11b', 'euro':'6c/+'}
    elif floatDifficulty < 11.34:
        return {'usa':'5.11b', 'euro':'6c+'}
    elif floatDifficulty < 11.66:
        return {'usa':'5.11c', 'euro':'6c+'}
    elif floatDifficulty < 12.34:
        return {'usa':'5.11c', 'euro':'6c+/7a'}
    elif floatDifficulty < 12.66:
        return {'usa':'5.11d', 'euro':'7a'}
    elif floatDifficulty < 13.34:
        return {'usa':'5.11d', 'euro':'7a'}
    elif floatDifficulty < 13.66:
        return {'usa':'5.12a', 'euro':'7a/+'}
    elif floatDifficulty < 14.34:
        return {'usa':'5.12a', 'euro':'7a+'}
    elif floatDifficulty < 14.66:
        return {'usa':'5.12b', 'euro':'7a+/b'}
    elif floatDifficulty < 15.34:
        return {'usa':'5.12b', 'euro':'7b'}
    elif floatDifficulty < 15.66:
        return {'usa':'5.12c', 'euro':'7b/+'}
    elif floatDifficulty < 16.34:
        return {'usa':'5.12c', 'euro':'7b+'}
    elif floatDifficulty < 16.66:
        return {'usa':'5.12d', 'euro':'7b+/c'}
    elif floatDifficulty < 17.34:
        return {'usa':'5.12d', 'euro':'7c'}
    elif floatDifficulty < 17.66:
        return {'usa':'5.13a', 'euro':'7c/+'}
    elif floatDifficulty < 18.34:
        return {'usa':'5.13a', 'euro':'7c+'}
    elif floatDifficulty < 18.66:
        return {'usa':'5.13b', 'euro':'7c+/8a'}
    elif floatDifficulty < 19.34:
        return {'usa':'5.13b', 'euro':'8a'}
    elif floatDifficulty < 19.66:
        return {'usa':'5.13c', 'euro':'8a/+'}
    elif floatDifficulty < 20.34:
        return {'usa':'5.13c', 'euro':'8a+'}
    elif floatDifficulty < 20.66:
        return {'usa':'5.13d', 'euro':'8a+/b'}
    elif floatDifficulty < 21.34:
        return {'usa':'5.13d', 'euro':'8b'}
    elif floatDifficulty < 21.66:
        return {'usa':'5.14a', 'euro':'8b/+'}
    elif floatDifficulty < 22.34:
        return {'usa':'5.14a', 'euro':'8b+'}    
    else:
        return {'usa':'5.14+', 'euro':'8+'}
    

# getPathNames: Retrieves name and path/route for eachitem in the selected entry's parent path
def getPathNames(path):
    path_raw = [step.split('/') for step in path.split('$')]
    path_clean = []
    for step in path_raw:
        path_clean.append({'name': step[1], 'route':f"area/{step[0]}/{step[1]}"})
    return path_clean

# countClimbs: recursive function for querying and counting number of children climbs by type
def countClimbs(area_model):
    boulders, sport, trad, dws, total = 0,0,0,0,0
    # Check area_type to determine search
    if area_model.area_type == 0:
        # Empty area, return all 0s
        return {'boulders':0,'sport':0,'trad':0,'dws':0,'total':0}
    elif area_model.area_type == 1:
        # Sub areas, recursively call on children
        children = db.session.query(AreaModel)\
            .filter(AreaModel.parent_id==area_model.id)\
            .filter(AreaModel.parent_name==area_model.name)\
            .all()
        for child in children:
            counts = countClimbs(child)
            boulders += counts['boulders']
            sport += counts['sport']
            trad += counts['trad']
            dws += counts['dws']
            total += counts['total']
        return {'boulders':boulders,'sport':sport,'trad':trad,'dws':dws,'total':total}
    elif area_model.area_type == 2:
        # Climbs, get counts of climb types
        tallies = db.session.query(ClimbModel.climb_type, func.count(ClimbModel.id))\
            .filter(ClimbModel.parent_id==area_model.id)\
            .filter(ClimbModel.parent_name==area_model.name)\
            .group_by(ClimbModel.climb_type)\
            .all()
        for typ in tallies:
            if typ[0] == 'boulder':
                boulders = typ[1]
            elif typ[0] == 'sport':
                sport = typ[1]
            elif typ[0] == 'trad':
                trad = typ[1]
            elif typ[0] == 'dws':
                dws = typ[1]
        total = boulders+sport+trad+dws
        return {'boulders':boulders,'sport':sport,'trad':trad,'dws':dws,'total':total}
 

# getChildrenInfo: For populating info on area children, retrieves entry's childrens' data
def getChildrenInfo(entry):
    # print("getChildrenInfo")
    # if area_type 0, no children
    if entry['area_type'] == 0:
        return []
    # if area_type 1, sub areas, query AreaModel
    elif entry['area_type'] == 1:
        children_info = []
        children = db.session.query(AreaModel)\
            .filter(AreaModel.parent_id==entry['id'])\
            .filter(AreaModel.parent_name==entry['name'])\
            .all()
        if type(children)==list:
            for child in children:
                counts = countClimbs(child)
                children_info.append({'name': child.name,
                    'route': f"/area/{child.id}/{child.name}",
                    'counts': counts})
        else:
            counts = countClimbs(child)
            children_info.append({'name': child.name,
                'route': f"/area/{child.id}/{child.name}",
                'counts': counts})
        return children_info
    # if area_type 2, climbs, query ClimbModel
    elif entry['area_type'] == 2:
        sorted_info = []
        unsorted_info = []

        climbs = db.session.query(ClimbModel.position.label('position'),\
            ClimbModel.climb_type.label('climb_type'),\
            ClimbModel.id.label('id'),\
            ClimbModel.name.label('name'),\
            func.coalesce(BoulderModel.grade, RouteModel.grade).label('grade'),\
            ClimbModel.quality.label('quality'),\
            ClimbModel.danger.label('danger'),\
            ClimbModel.height.label('height'),\
            RouteModel.pitches.label('pitches'),\
            RouteModel.committment.label('committment'),\
            ClimbModel.fa.label('fa'),\
            ClimbModel.description.label('description'),\
            ClimbModel.pro.label('pro'),\
            RouteModel.route_type.label('route_type'))\
            .outerjoin(RouteModel, RouteModel.id == ClimbModel.id)\
            .outerjoin(BoulderModel, BoulderModel.id == ClimbModel.id)\
            .filter(ClimbModel.parent_id==entry['id']).filter(ClimbModel.parent_name==entry['name'])\
            .order_by('position')

        gradeByClimb_type = {'boulder': boulderInt2Grade,
             'sport': routeInt2Grade,
             'trad': routeInt2Grade,
             'dws': routeInt2Grade}
        # Append info to corresponding lists
        for child in climbs:
            # (position, climb_type, id, name, grade, quality, danger, height, pitches, committment, fa, desc, pro, route_type)
            child_entry = {
                'id': child[2],
                'name': child[3],
                'properties': {
                    'grade': gradeByClimb_type[child[1]](child[4]),
                    'route_type': route_types[child[13]],
                    'quality': child[5],
                    'danger': dangerInt2Movie[child[6]],
                    'height': child[7],
                    'pitches': child[8],
                    'committment': child[9],
                    'fa': child[10],
                    'description': child[11],
                    'pro': child[12],
                },
                'climb_type': child[1],
                'route': f"{child[1]}/{child[2]}/{child[3]}",
                'tags': [str(tag)[2:-3] for tag in db.session.query(TagsModel.title)\
                    .join(TagsClimbsModel, TagsClimbsModel.tag_id == TagsModel.id)\
                    .join(ClimbModel, ClimbModel.id == TagsClimbsModel.climb_id)\
                    .filter(ClimbModel.id == child[2])]
            }
            if child[0] == 0:
                unsorted_info.append(child_entry)
            else:
                sorted_info.append(child_entry)
        
        return {'sorted': sorted_info, 'unsorted': unsorted_info}
        
# simplifyArray: takes JSON form array and converts it to single python dictionary
def simplifyArray(json_request):
    return {field['name']: field['value'] for field in json_request}

# convertFormDatatypes: Some HTML form values are submitted as strings, not ints, this converts them
def convertFormDatatypes(new_loc):
    for i in ['grade', 'quality', 'danger', 'height', 'pitches']:
        if i in new_loc.keys():
            new_loc[i] = int(new_loc[i])
    return new_loc

        
# validateAddition: re-checks all fields are filled and valid,
# then checks database for new entry details of parent and name
# Returns a tuple corresponding to the following:
# ("validated" boolean (True=accepted), error code if error, additional info for error handling)
def validateAddition(loc_type, new_loc):
    print('Validating...')
    # Check for all fields filled
    for field in new_loc.keys():
        if new_loc[field] == '':
            # Invalid field - An Error occurred, please try again.
            return (False, 1, (loc_type, new_loc))
    # Else continue

    # Check for valid grade, danger, committment based on loc_type
    if loc_type == 'boulder':
        new_loc = convertFormDatatypes(new_loc)
        if new_loc['grade'] > 14 or new_loc['grade'] < -1:
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['danger']) != new_loc['danger'] or new_loc['danger'] > 3 or new_loc['danger'] < 0:
            return (False, 1, (loc_type, new_loc))
    
    if loc_type == 'route':
        if new_loc['grade'] > 40 or new_loc['grade'] < -1:
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['danger']) != new_loc['danger'] or new_loc['danger'] > 3 or new_loc['danger'] < 0:
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['pitches']) != new_loc['pitches']:
            return (False, 1, (loc_type, new_loc))
        if new_loc['committment'] not in ['I','II','III','IV','V','VI']:
            return (False, 1, (loc_type, new_loc))

    # Check for duplicate entry
    if loc_type == 'area':
        model = AreaModel
    else:
        model = ClimbModel
    # Old db code
    # type2model = {'area': AreaModel,'boulder': BoulderModel, 'route': RouteModel}
    # model = type2model[loc_type]
    validated =  db.session.query(model)\
        .filter(model.parent_id == new_loc['parent_id'])\
        .filter(model.parent_name==new_loc['parent_name'])\
        .filter(model.name==new_loc['name'])\
        .first()
    # If validated (if an entry already exists) return duplicta entry error, otherwise proceed
    if validated:
        return (False, 2, (loc_type, validated))
    else:
        return (True, new_loc)


# validationErrorProtocol: handles any errors found by validateAddition
def validationErrorProtocol(error_code, data):
    print("Handling Error")
    if error_code == 1:
        # Unfilled/Invalid Field - likely due to unintended page manipulation
        # data = (loc_type, new_loc)
        # Redirect to addEntry of loc_type of the parent area
        return {'redirect': f"/add-entry/{data[0]}/{str(data[1]['parent_id'])}/{str(data[1]['parent_name'])}",
            'error': 1}
    elif error_code == 2:
        # Duplicate Entry
        # data = (loc_type, validated) (the Model of the existing entry)
        # Redirect to existing entry's page
        if data[0] == 'area':
            return {'redirect': f"/area/{str(data[1].id)}/{str(data[1].name)}",
                'error': 2}
        else:
            return {'redirect': f"/area/{str(data[1].parent_id)}/{str(data[1].parent_name)}#v-pills-{data[0]}-{data[1].id}",
                'error': 2}


# addTags: inserts new tags to tags(TagsModel) and tagClimb(TagClimbsModel) tables
def addTags(form_fields, new_id):
    # Isolate tag fields
    tags = {field:form_fields[field] for field in form_fields.keys() if "tag" in field}
    
    # Process possible new tags
    # New tags in form field 'tags_other' as comma-separated list
    # Tags to be stored/converted to lowercasefor consistency
    if tags['tags_other']:
        other_tags = []
        new_tags = [tag.lower().strip() for tag in tags['tags_other'].split(',')]
        # Process tags, attempt to void false duplicates
        for tag in new_tags:
            exists =  db.session.query(TagsModel)\
                .filter(TagsModel.title == tag)\
                .first()
            # If exists, add relationship b/w climb and tag to TagClimbs
            if exists:
                other_tags.append(TagsClimbsModel(
                    climb_id=new_id,
                    tag_id=exists.id
                ))
            # Else, possible new tag, double check against likeCommonTags
            else:
                for key in likeCommonTags.keys():
                    if tag in likeCommonTags[key]:
                        # Existing tag, use existing value (query for id)
                        other_tags.append(TagsClimbsModel(
                            climb_id=new_id,
                            tag_id=db.session.query(TagsModel)\
                                .filter(TagsModel.title == key)\
                                .first().id
                        ))
                        continue
                # Not duplicate, NEW tag, add to TagsModel, flush for id, add relationship
                confirm_new_tag = TagsModel(
                    title=tag
                )
                db.session.add(confirm_new_tag)
                db.session.flush()
                other_tags.append(TagsClimbsModel(
                    climb_id=new_id,
                    tag_id=confirm_new_tag.id
                ))
        # All tags_other processed, bulk save
        db.session.bulk_save_objects(other_tags)

    # Process guidebook tags
    # Guidebook tags and ids as follows:
    guidebook_tags = {'tag_dirty':0,'tag_reachy':1,'tag_technical':2,'tag_highball':3,'tag_chossy':4,'tag_bad_landing':5}
    gtags_models = []
    for gkey in guidebook_tags.keys():
        if gkey in tags.keys():
            gtags_models.append(TagsClimbsModel(
                climb_id=new_id,
                tag_id=guidebook_tags[gkey]
            ))
    db.session.bulk_save_objects(gtags_models)
    # No commit, full commit will be made after boulder is flushed



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

        # Update parent area_type if necessary (1 for Areas)
        parent = db.session.query(AreaModel)\
            .filter(AreaModel.id==new_area['parent_id'])\
            .filter(AreaModel.name==new_area['parent_name'])\
            .first()
        if parent.area_type == 0:
            parent.area_type = 1
        elif parent.area_type == 2:
            return render_template('404.html', status_code=errors['403'])

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
        new_boulder = validated[1]
        # Initialize new entry
        new_entry = ClimbModel(
            name=new_boulder['name'],
            parent_id=new_boulder['parent_id'],
            parent_name=new_boulder['parent_name'],
            # path=new_boulder['parent_path']+f"${new_boulder['parent_id']}/{new_boulder['parent_name']}",
            climb_type='boulder',
            position=0,
            # grade=new_boulder['grade'],
            quality=new_boulder['quality'],
            danger=new_boulder['danger'],
            height=new_boulder['height'],
            fa=new_boulder['fa'],
            description=new_boulder['description'],
            pro=new_boulder['pro']
        )

        db.session.add(new_entry)
        # Flush ClimbModel addition to db for ID key
        db.session.flush()

        # Add grade to 'boulders' table
        new_entry_secondary = BoulderModel(
            id=new_entry.id,
            grade=new_boulder['grade']
        )

        db.session.add(new_entry_secondary)

        # Add tags to tag tables
        addTags(new_boulder,new_entry.id)

        # Update parent area_type if necessary (2 for Boulders/Routes)
        parent = db.session.query(AreaModel)\
            .filter(AreaModel.id==new_boulder['parent_id'])\
            .filter(AreaModel.name==new_boulder['parent_name'])\
            .first()
        if parent.area_type == 0:
            parent.area_type = 2
        elif parent.area_type == 1:
            return render_template('404.html', status_code=errors['403'])

        # Commit
        db.session.commit()

        # Return and redirect
        print(f'Redirecting to area/{str(new_entry.parent_id)}/{new_entry.parent_name}')
        return {'redirect': f'/area/{str(new_entry.parent_id)}/{new_entry.parent_name}#v-pills-boulder-{new_entry.id}',
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
@app.route('/1/All-Locations')
def allLocations():
    # Template to be filled when database is properly initialized
    return render_template('allLocations.html')


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
            .first()
        if entry:
            entry = entry.toJSON()
        else:
            return render_template('404.html', status_code=errors['404'])
        path = getPathNames(entry['parent']['path'])
        children = getChildrenInfo(entry)
        
        # Return correct template (areas / climbs)
        if entry['area_type'] == 2:
            return render_template('area_2.html', area=entry, path=path, children=children)
        else:
            return render_template('area.html', area=entry, path=path, children=children)

    except Exception as e:
        print(e)
        return render_template('404.html', status_code=errors['404'])


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
            .first()
    if parent:
        if parent.area_type == 0:
            parent = parent.toJSON()
        # Forbidden - areas may only have child areas OR boulders/routes
        elif (parent.area_type == 1 and entry_type != 'area') or (parent.area_type == 2 and entry_type == 'area'):
            return render_template('404.html', status_code=errors['403'])
        else:
            parent = parent.toJSON()
    else:
        return render_template('404.html', status_code=errors['404'])
    if entry_type == 'area':
        return render_template('addArea.html', parent=parent)
    elif entry_type == 'boulder':
        return render_template('addBoulder.html', parent=parent)
    elif entry_type == 'route':
        return render_template('addRoute.html', parent=parent)
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
        'area': addArea, # add new area functions plus returns redirect to new area
        'boulder': addBoulder,
        'route': '',
        'edit': ''
    }
    
    return change_options[inputted_data['change-type']](inputted_data)

# editEntry (allows edits to the current entry)
@app.route('/edit-entry/<entry_type>/<entry_id>')
def editEntry(entry_type, entry_id):
    print('placeholder')



if __name__ == '__main__':
    app.run(debug=True)

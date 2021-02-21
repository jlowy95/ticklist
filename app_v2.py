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
import re
import datetime
import json
import pprint
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Initialize SQLAlchemy connection
# MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:joshstemppassword@localhost/MyTicksTest"

# Connect SQL database to Flask app
db = SQLAlchemy(app)
migrate = Migrate(app, db)
 
# Define file upload guidelines
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    climb_type = db.Column(db.String(10), nullable=False) # for distinction between boulders and routes
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

    id = db.Column(db.Integer, db.ForeignKey('climbs.id'),primary_key=True, nullable=False)
    grade = db.Column(db.Float, nullable=False)
    aid_grade = db.Column(db.String(2))
    pitches = db.Column(db.Integer, nullable=False)
    committment = db.Column(db.String(3))
    route_type = db.Column(db.Integer, nullable=False)

    def __init__(self, id, grade, aid_grade, pitches, committment, route_type):
        self.id = id
        self.grade = grade
        self.aid_grade = aid_grade
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

    climb_id = db.Column(db.Integer, db.ForeignKey('climbs.id'), primary_key=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True, nullable=False)

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
    0: {'short':'','long':''},
    1: {'short':'S','long':'Sport'},
    2: {'short':'T','long':'Trad'},
    3: {'short':'DWS','long':'Deep Water Solo'},
    4: {'short': 'A', 'long': 'Aid'}
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

# allowed_file: Returns bool if file extension is in ALLOWED_EXTENSIONS
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        return {'usa':'V6-7', 'euro':'7A/+'}
    elif floatDifficulty < 7.34:
        return {'usa':'V7', 'euro':'7A+'}
    elif floatDifficulty < 7.66:
        return {'usa':'V7-8', 'euro':'7A+/B'}
    elif floatDifficulty < 8.34:
        return {'usa':'V8', 'euro':'7B'}
    elif floatDifficulty < 8.66:
        return {'usa':'V8-9', 'euro':'7B+/C'}
    elif floatDifficulty < 9.34:
        return {'usa':'V9', 'euro':'7C'}
    elif floatDifficulty < 9.66:
        return {'usa':'V9-10', 'euro':'7C/+'}
    elif floatDifficulty < 10.34:
        return {'usa':'V10', 'euro':'7C+'}
    elif floatDifficulty < 10.66:
        return {'usa':'V10-11', 'euro':'7C+/8A'}
    elif floatDifficulty < 11.34:
        return {'usa':'V11', 'euro':'8A'}
    elif floatDifficulty < 11.66:
        return {'usa':'V11-12', 'euro':'8A/+'}
    elif floatDifficulty < 12.34:
        return {'usa':'V12', 'euro':'8A+'}
    elif floatDifficulty < 12.66:
        return {'usa':'V12-13', 'euro':'8A+/B'}
    elif floatDifficulty < 13.34:
        return {'usa':'V13', 'euro':'8B'}
    elif floatDifficulty < 13.66:
        return {'usa':'V13-14', 'euro':'8B/+'}
    elif floatDifficulty < 14.34:
        return {'usa':'V14', 'euro':'8B+'}
    elif floatDifficulty < 14.66:
        return {'usa':'V14-15', 'euro':'8B+/C'}
    elif floatDifficulty < 15.34:
        return {'usa':'V15', 'euro':'8C'}
    else:
        return {'usa':'V15+', 'euro':'8C+'}
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
    elif floatDifficulty < 22.66:
        return {'usa':'5.14b', 'euro':'8b+/c'}
    elif floatDifficulty < 23.34:
        return {'usa':'5.14b', 'euro':'8c'}
    elif floatDifficulty < 23.66:
        return {'usa':'5.14c', 'euro':'8c/+'}
    elif floatDifficulty < 24.34:
        return {'usa':'5.14c', 'euro':'8c+'}
    elif floatDifficulty < 24.66:
        return {'usa':'5.14d', 'euro':'8c+/9a'}
    elif floatDifficulty < 25.34:
        return {'usa':'5.14d', 'euro':'9a'}
    elif floatDifficulty < 25.66:
        return {'usa':'5.15a', 'euro':'9a/+'}
    elif floatDifficulty < 26.34:
        return {'usa':'5.15a', 'euro':'9a+'}    
    else:
        return {'usa':'Aid', 'euro':'Aid'}


# getPathNames: Retrieves name and path/route for eachitem in the selected entry's parent path
def getPathNames(path):
    path_raw = [step.split('/') for step in path.split('$')]
    path_clean = [{'name': 'All Locations', 'route':f"1/All-Locations"}]
    for step in path_raw[1:]:
        path_clean.append({'name': step[1], 'route':f"area?entry_id={step[0]}&entry_name={step[1]}"})
    # print(path_clean)
    return path_clean


# countClimbs: recursive function for querying and counting number of children climbs by type
def countClimbs(area_model):
    boulders, sport, trad, dws, aid, total = 0,0,0,0,0,0
    # Check area_type to determine search
    if area_model.area_type == 0:
        # Empty area, return all 0s
        return {'boulders':0,'sport':0,'trad':0,'dws':0, 'aid':0, 'total':0}
    elif area_model.area_type == 1:
        # Sub areas, recursively call on children
        children = db.session.query(AreaModel)\
            .filter(AreaModel.parent_id==area_model.id)\
            .filter(AreaModel.parent_name==area_model.name)\
            .all()
        for child in children:
            # Recursion check
            if child == area_model:
                continue
            counts = countClimbs(child)
            boulders += counts['boulders']
            sport += counts['sport']
            trad += counts['trad']
            dws += counts['dws']
            aid += counts['aid']
            total += counts['total']
        return {'boulders':boulders,'sport':sport,'trad':trad,'dws':dws, 'aid':aid, 'total':total}
    elif area_model.area_type == 2:
        # Climbs, get counts of climb types
        tallies = db.session.query(func.ifnull(RouteModel.route_type, 0), func.count(func.ifnull(RouteModel.route_type, 0)))\
            .select_from(ClimbModel)\
            .outerjoin(RouteModel, ClimbModel.id == RouteModel.id)\
            .filter(ClimbModel.parent_id==area_model.id)\
            .filter(ClimbModel.parent_name==area_model.name)\
            .group_by(RouteModel.route_type)\
            .all()
        for typ in tallies:
            if typ[0] == 0:
                boulders = typ[1]
            elif typ[0] == 1:
                sport = typ[1]
            elif typ[0] == 2:
                trad = typ[1]
            elif typ[0] == 3:
                dws = typ[1]
            elif typ[0] == 4:
                aid = typ[1]
        total = boulders+sport+trad+dws+aid
        # print(f"'boulders':{boulders},'sport':{sport},'trad':{trad},'dws':{dws},'total':{total}")
        return {'boulders':boulders,'sport':sport,'trad':trad,'dws':dws, 'aid':aid, 'total':total}
 

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
                # Recursion Check
                if child.toJSON() == entry:
                    continue
                counts = countClimbs(child)
                children_info.append({
                    'id': child.id,
                    'name': child.name,
                    'counts': counts})
        else:
            counts = countClimbs(child)
            children_info.append({
                'id': child.id,
                'name': child.name,
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
            RouteModel.aid_grade.label('aid_grade'),\
            ClimbModel.quality.label('quality'),\
            ClimbModel.danger.label('danger'),\
            ClimbModel.height.label('height'),\
            RouteModel.pitches.label('pitches'),\
            RouteModel.committment.label('committment'),\
            ClimbModel.fa.label('fa'),\
            ClimbModel.description.label('description'),\
            ClimbModel.pro.label('pro'),\
            func.ifnull(RouteModel.route_type, 0).label('route_type'))\
            .outerjoin(RouteModel, RouteModel.id == ClimbModel.id)\
            .outerjoin(BoulderModel, BoulderModel.id == ClimbModel.id)\
            .filter(ClimbModel.parent_id==entry['id']).filter(ClimbModel.parent_name==entry['name'])\
            .order_by('position')

        gradeByClimb_type = {'boulder': boulderInt2Grade,
             'route': routeInt2Grade}
        # Append info to corresponding lists
        for child in climbs:
            # (position, climb_type, id, name, grade, aid_grade, quality, danger, height, pitches, committment, fa, desc, pro, route_type)
            child_entry = {
                'id': child[2],
                'name': child[3],
                'properties': {
                    'grade': gradeByClimb_type[child[1]](child[4]),
                    'aid_grade': child[5],
                    'route_type': route_types[child[14]],
                    'quality': child[6],
                    'danger': dangerInt2Movie[child[7]],
                    'height': child[8],
                    'pitches': child[9],
                    'committment': child[10],
                    'fa': child[11],
                    'description': child[12],
                    'pro': child[13],
                },
                'climb_type': child[1],
                # 'route': f"{child[1]}/{child[2]}/{child[3]}",
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
    # Ints
    for i in ['quality', 'danger', 'height', 'pitches', 'committment']:
        if i in new_loc.keys():
            if new_loc[i] != '':
                new_loc[i] = int(new_loc[i])
            else:
                new_loc[i] = None
    # Floats
    for i in ['grade']:
        if i in new_loc.keys():
            if new_loc[i] != '':
                new_loc[i] = float(new_loc[i])
            else:
                new_loc[i] = None
    return new_loc

# checkDupe: Checks ClimbModel and AreaModel for an already existing climb under said area.
def checkDupe(area, climb):
    query = db.session.query(ClimbModel)\
        .filter(ClimbModel.name == climb)\
        .filter(AreaModel.name == area)\
        .join(AreaModel, AreaModel.id == ClimbModel.parent_id)\
        .first()
    # If match, return true, else false
    if query:
        return True
    else:
        return False


# validateAddition: re-checks all fields are filled and valid,
# then checks database for new entry details of parent and name
# Returns a tuple corresponding to the following:
# ("validated" boolean (True=accepted), error code if error, additional info for error handling)
def validateAddition(loc_type, new_loc):
    # Convert int fields to int type
    new_loc = convertFormDatatypes(new_loc)

    # Check for valid grade, danger, committment based on loc_type
    if loc_type == 'boulder':
        # new_loc = convertFormDatatypes(new_loc)
        if new_loc['grade'] > 16 or new_loc['grade'] < -1:
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['danger']) != new_loc['danger'] or new_loc['danger'] > 3 or new_loc['danger'] < 0:
            return (False, 1, (loc_type, new_loc))
    
    if loc_type == 'route':
        # new_loc = convertFormDatatypes(new_loc)
        if new_loc['grade'] > 99 or new_loc['grade'] < -1:
            return (False, 1, (loc_type, new_loc))
        if (not(re.search('^[AC][0-5]$', new_loc['aid_grade'])) and new_loc['aid_grade'] != ''):
            print('Invalid aid_grade')
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['danger']) != new_loc['danger'] or new_loc['danger'] > 3 or new_loc['danger'] < 0:
            return (False, 1, (loc_type, new_loc))
        if int(new_loc['pitches']) != new_loc['pitches']:
            return (False, 1, (loc_type, new_loc))
        if new_loc['committment'] > 7 or new_loc['committment'] < 1:
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
        print(f"Duplicate found: {validated.name}")
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
                notCommon = True
                for key in likeCommonTags.keys():
                    if tag in likeCommonTags[key]:
                        # Existing tag, use existing value (query for id)
                        other_tags.append(TagsClimbsModel(
                            climb_id=new_id,
                            tag_id=db.session.query(TagsModel)\
                                .filter(TagsModel.title == key)\
                                .first().id
                        ))
                        notCommon = False
                        break
                # Not duplicate, NEW tag, add to TagsModel, flush for id, add relationship
                if notCommon:
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
    guidebook_tags = {'tag_dirty':1,'tag_reachy':2,'tag_technical':3,'tag_highball':4,'tag_chossy':5,'tag_bad_landing':6}
    gtags_models = []
    for gkey in guidebook_tags.keys():
        if gkey in tags.keys():
            gtags_models.append(TagsClimbsModel(
                climb_id=new_id,
                tag_id=guidebook_tags[gkey]
            ))
    db.session.bulk_save_objects(gtags_models)
    # No commit, full commit will be made after boulder is flushed


# findArea: Intended for mass import inserts, locates the parent area of the entry, adding new areas as needed
def findArea(areasList):
    try:
        # First area should 100% be in database
        connection = db.session.query(AreaModel)\
            .filter(AreaModel.name == areasList[0])\
            .first()
        # If not in database, we need user input
        if not connection:
            # print("No connection found, move this entry to IN-Invalid Area")
            return (False,)
        # Else continue
        else:
            parent_area = connection.toJSON()
            # Check areas for current area and reassign as parent if parent is in path. If area isn't found or areasList is empty, move on
            i = 1
            while i < len(areasList):
                query_areas = db.session.query(AreaModel)\
                    .filter(AreaModel.name == areasList[i])\
                    .all()
                # If current_area is found, check for parent in path then set as new parent
                if len(query_areas) == 0:
                    break
                else:
                    j = 0
                    while j < len(query_areas):
                        path = getPathNames(query_areas[j].path)
                        if parent_area['name'] in [a['name'] for a in path]:
                            parent_area = query_areas[j].toJSON()
                            i += 1
                            break
                        else:
                            j += 1
                    if j >= len(query_areas):
                        break
            # Add new areas as needed
            while i < len(areasList):
                # addArea, store the new area to add as parent
                new_area = {
                    'name': areasList[i],
                    'parent_id': parent_area['id'],
                    'parent_name': parent_area['name'],
                    'description': 'TBA',
                    'directions': 'TBA'
                }
                aa_res = addArea(new_area)
                # print(aa_res)
                if aa_res['success']:
                    # Shortcut to fully defining parent_area, as we only need id/name which are returned in the success message
                    parent_area = aa_res['success']
                    i += 1
                # If addArea fails, very confused, print error
                else:
                    print(f'addArea failure for {new_area}.')
            # Return area details for adding entry
            return (True, parent_area)
    except Exception as e:
        print(f"findArea Error: {e}")
        return (True, parent_area)


# addArea: inserts new area entry and updates parent area
def addArea(new_area):
    # Validate if new entry
    validated = validateAddition('area', new_area)
    if validated[0]:
        # Update parent area_type if necessary (1 for Areas)
        parent = db.session.query(AreaModel)\
            .filter(AreaModel.id==new_area['parent_id'])\
            .filter(AreaModel.name==new_area['parent_name'])\
            .first()
        if parent.area_type == 0:
            parent.area_type = 1
        elif parent.area_type == 2:
            return render_template('404.html', status_code=errors['403'])

        # Initialize new entry
        new_entry = AreaModel(
            name=new_area['name'],
            parent_id=new_area['parent_id'],
            parent_name=new_area['parent_name'],
            path=parent.path+f"${new_area['parent_id']}/{new_area['parent_name']}",
            description=new_area['description'],
            directions=new_area['directions'],
            elevation=None,
            lat=None,
            lng=None
        )


        # Commit
        db.session.add(new_entry)
        db.session.commit()

        # Return and redirect
        # print(f"Redirecting to area?entry_id={str(new_entry.id)}&entry_name={str(new_entry.name)}")
        return {
            'redirect': f"/area?entry_id={str(new_entry.id)}&entry_name={str(new_entry.name)}",
            'success': {
                'message': 'New entry added successfully!',
                'id': new_entry.id,
                'name': new_entry.name
                }
        }
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
            climb_type='boulder',
            position=0,
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
        # print(f'Redirecting to area/{str(new_entry.parent_id)}/{new_entry.parent_name}')
        return {
            'redirect': f'/area/{str(new_entry.parent_id)}/{new_entry.parent_name}#v-pills-boulder-{new_entry.id}',
            'success': {
                'message': 'New entry added successfully!',
                'id': new_entry.id,
                'name': new_entry.name
                }
            }
    else:
        # Else, error - handle the error and return
        print(f"Error Code: {validated[1]}")
        return validationErrorProtocol(validated[1], validated[2])


# addRoute: inserts new boulder entry and updates parent area
def addRoute(new_route):
    # Validate if new entry
    validated = validateAddition('route', new_route)
    if validated[0]:
        new_route = validated[1]
        # Initialize new entry
        new_entry = ClimbModel(
            name=new_route['name'],
            parent_id=new_route['parent_id'],
            parent_name=new_route['parent_name'],
            climb_type='route',
            position=0,
            quality=new_route['quality'],
            danger=new_route['danger'],
            height=new_route['height'],
            fa=new_route['fa'],
            description=new_route['description'],
            pro=new_route['pro']
        )

        db.session.add(new_entry)
        # Flush ClimbModel addition to db for ID key
        db.session.flush()

        # Add other info to 'routes' table
        new_entry_secondary = RouteModel(
            id=new_entry.id,
            grade=new_route['grade'],
            aid_grade=new_route['aid_grade'],
            pitches=new_route['pitches'],
            committment=new_route['committment'],
            route_type=new_route['route_type']
        )

        db.session.add(new_entry_secondary)

        # Add tags to tag tables
        addTags(new_route,new_entry.id)

        # Update parent area_type if necessary (2 for Boulders/Routes)
        parent = db.session.query(AreaModel)\
            .filter(AreaModel.id==new_route['parent_id'])\
            .filter(AreaModel.name==new_route['parent_name'])\
            .first()
        if parent.area_type == 0:
            parent.area_type = 2
        elif parent.area_type == 1:
            return render_template('404.html', status_code=errors['403'])

        # Commit
        db.session.commit()

        # Return and redirect
        # print(f'Redirecting to area/{str(new_entry.parent_id)}/{new_entry.parent_name}')
        return {
            'redirect': f'/area/{str(new_entry.parent_id)}/{new_entry.parent_name}#v-pills-route-{new_entry.id}',
            'success': {
                'message': 'New entry added successfully!',
                'id': new_entry.id,
                'name': new_entry.name
                }
            }
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
    al = db.session.query(AreaModel)\
        .filter(AreaModel.id==1)\
        .filter(AreaModel.name=='All Locations')\
        .first()
    al = al.toJSON()

    children = getChildrenInfo(al)
    grandchildren = []
    for child in children:
        grandchildren.append(getChildrenInfo(db.session.query(AreaModel)\
            .filter(AreaModel.id==child['id'])\
            .filter(AreaModel.name==child['name'])\
            .first().toJSON()))

    return render_template('allLocations.html', children=children, grandchildren=grandchildren)


# API Routes
# Loads the corresponding page type to the entry requested
@app.route('/area', methods=['GET'])
def area():
    args = request.args
    if args['entry_id'] and args['entry_name']:
        try:
            # Retrieve Entry
            entry = db.session.query(AreaModel)\
                .filter(AreaModel.id==args['entry_id'])\
                .filter(AreaModel.name==args['entry_name'])\
                .first()
            if entry:
                entry = entry.toJSON()
            else:
                return render_template('404.html', status_code=errors['404'])
            path = getPathNames(entry['parent']['path'])
            children = getChildrenInfo(entry)
            # print(children)
            
            # Return correct template (areas / climbs)
            if entry['area_type'] == 2:
                return render_template('area_2.html', area=entry, path=path, children=children)
            else:
                return render_template('area.html', area=entry, path=path, children=children)

        except Exception as e:
            print(e)
            return render_template('404.html', status_code=errors['404'])


# Search query route
@app.route('/search')
def search():
    search_terms = request.args.get('search_terms')

    # Format search terms for sqlalchemy
    likeFormat = "%{}%".format(search_terms)

    # Query Areas and Climbs for search_terms (in likeFormat)
    queryArea = db.session.query(AreaModel)\
        .filter(AreaModel.name.like(likeFormat)).all()
    queryClimb = db.session.query(ClimbModel)\
        .filter(ClimbModel.name.like(likeFormat)).all()
    # Use toJSON method to parse query results and store
    results = {
        'areas':[r.toJSON() for r in queryArea],
        'climbs': [r.toJSON() for r in queryClimb]
    }
    return render_template('search.html', search_terms=search_terms, results=results)


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
        return render_template('addBoulder2.html', parent=parent)
    elif entry_type == 'route':
        return render_template('addRoute2.html', parent=parent)
    else:
        print('Error: invalid entry_type')
        redirect(url_for('area', entry_id=parent_id, entry_name=parent_name))

# submitChanges - POST route processes changes to db
# then redirects to new page if successful
@app.route('/submit-changes', methods=['POST'])
def submitChanges():
    inputted_data = simplifyArray(request.get_json())
    print(inputted_data)
    # Switch for correct actions
    change_options = {
        'area': addArea, # add new area functions plus returns redirect to new area
        'boulder': addBoulder,
        'route': addRoute,
        'edit': ''
    }
    
    return change_options[inputted_data['change-type']](inputted_data)

# editEntry (allows edits to the current entry)
@app.route('/edit-entry/<entry_type>/<entry_id>/<entry_name>')
def editEntry(entry_type, entry_id, entry_name):
    # Attempt to locate entry
    if entry_type == 'area':
        entry = db.session.query(AreaModel)\
            .filter(AreaModel.id == entry_id)\
            .filter(AreaModel.name == entry_name)\
            .first()
    elif entry_type == 'climb':
        entry = db.session.query(ClimbModel)\
            .filter(ClimbModel.id == entry_id)\
            .filter(ClimbModel.name == entry_name)\
            .first()
    else:
        # Invalid entry type, 404
        print('Error: invalid entry_type')
        return render_template('404.html', status_code=errors['404'])

    # Verify that an entry was found or 404    
    if entry:
        entry = entry.toJSON()
    else:
        return render_template('404.html', status_code=errors['404'])

    # Use toJSON to create object to populate template then redirect
    if entry_type == 'area':
        path = getPathNames(entry['parent']['path'])
        return render_template('editArea.html', entry=entry, path=path)
    elif entry_type == 'climb':
        path = getPathNames(db.session.query(AreaModel.path)\
            .filter(AreaModel.id == entry['parent']['id'])\
            .filter(AreaModel.name == entry['parent']['name'])\
            .first()[0])
        # Danger is already converted, switch it to tuple (int, movie)
        reverseDanger = {'':(0,'G'),'PG-13':(1,'PG-13'),'R':(2,'R'),'X':(3,'X')}
        entry['properties']['danger'] = reverseDanger[entry['properties']['danger']]
        if entry['climb_type'] == 'boulder':
            secondary = db.session.query(BoulderModel)\
                .filter(BoulderModel.id == entry['id'])\
                .first()
            entry['properties']['grade'] = (secondary.grade, boulderInt2Grade(secondary.grade))
            return render_template('editClimb.html', entry=entry)
        elif entry['climb_type'] == 'route':
            secondary = db.session.query(RouteModel)\
                .filter(RouteModel.id == entry['id'])\
                .first()
            entry['properties']['route_type'] = (secondary.route_type, route_types[secondary.route_type])
            entry['properties']['grade'] = (secondary.grade, routeInt2Grade(secondary.grade))
            entry['properties']['pitches'] = secondary.pitches
            entry['properties']['committment'] = secondary.committment
            return render_template('editClimb.html', entry=entry, path=path)
        else:
            # Invalid climb_type, redirect to error
            print('Error: invalid climb_type')
            return render_template('404.html', status_code=errors['404'])
        

# Mass Import Tool
# massImport - returns the mass import tool page
@app.route('/mass-import')
def massImport():
    return render_template('massimport.html')

@app.route('/check-entry', methods=['GET', 'POST'])
def checkEntry():
    args = request.args
    if request.method == 'GET':
        if args['type'] == 'dupe':
            # !!!!!!! CHECK CASE SENSITIVITY FOR DUPE CHECK AND STORAGE PROTOCOL
            dupe = checkDupe(args['area'], args['climb'])
            if dupe:
                return {'dupeCheck': True}
            else:
                return {'dupeCheck': False}
    elif request.method == 'POST':
        try:
            inputted_data = request.get_json()
            # print(f'Adding: {inputted_data["name"]}')
            # Build out tree of parent areas
            parent_area = findArea(inputted_data['areas'])
            # print(f"findArea done: {parent_area}")
            # Returns tuple (completed boolean, parent_area)
            if parent_area[0]:
                new_climb = {
                    'name': inputted_data['name'],
                    'parent_id': parent_area[1]['id'],
                    'parent_name': parent_area[1]['name']
                }
                for key in inputted_data['details']:
                    new_climb[key] = inputted_data['details'][key]

                if inputted_data['details']['climb_type'] == 'boulder':
                    aeRes = addBoulder(new_climb)
                elif inputted_data['details']['climb_type'] == 'route':
                    aeRes = addRoute(new_climb)
                
                
                if aeRes['success']:
                    print(f"Climb added!: {inputted_data['name']}")
                    return {'inserted': True}
            else:
                # Area Error, move to IN
                print(f"Area error for {inputted_data['name']}")
                return {'inserted': False}
        except Exception as e:
            print(f"Error importing {inputted_data['name']}: {e}")
            print(inputted_data)
            return {'inserted': False}
    else:
        print("Method Error at /check-entry")


if __name__ == '__main__':
    app.run(debug=True)

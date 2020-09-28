from flask import Flask
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector
import datetime

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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    path = db.Column(db.String(150))
    position = db.Column(db.Integer)
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
    climb_type = db.Column(db.String())
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, position, grade, quality, danger, height, fa, description, pro, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.position = 0
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
        self.climb_type = 'boulder'
        self.date_inserted = datetime.datetime.now()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'path': self.path,
                'position': self.position
            },
            'properties': {
                'grade': boulderInt2Grade(self.grade),
                'quality': self.quality,
                'danger': dangerInt2Movie[self.danger],
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
            'climb_type': self.climb_type,        
            'date_inserted': self.date_inserted
        }

class RouteModel(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(35), nullable=False, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=False)
    parent_name = db.Column(db.String(35), nullable=False)
    path = db.Column(db.String(150))
    position = db.Column(db.Integer)
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
    climb_type = db.Column(db.String())
    date_inserted = db.Column(db.DateTime)

    def __init__(self, name, parent_id, parent_name, path, position, grade, quality, danger, height, pitches, committment, fa, description, pro, elevation, lat, lng):
        self.name = name
        self.parent_id = parent_id
        self.parent_name = parent_name
        self.path = path
        self.position = 0
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
        self.climb_type = 'route'
        self.date_inserted = datetime.datetime.now()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': {
                'id': self.parent_id,
                'name': self.parent_name,
                'path': self.path,
                'position': self.position
            },
            'properties': {
                'grade': self.grade,
                'quality': self.quality,
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
            'climb_type': self.climb_type,        
            'date_inserted': self.date_inserted
        }

dangerInt2Movie = {
    0:'',
    1:'PG-13',
    2:'R',
    3:'X'
}

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
   
entry = {'id': 3,
    'name': 'Wyoming'}

sorted_info = []
unsorted_info = []
# Check boulders
boulders = db.session.query(BoulderModel.position.label('position'),\
    BoulderModel.climb_type.label('climb_type'),\
    BoulderModel.id.label('id'),\
    BoulderModel.name.label('name'),\
    BoulderModel.grade.label('grade'),\
    BoulderModel.quality.label('quality'),\
    BoulderModel.danger.label('danger'),\
    sa.null().label('pitches'),\
    sa.null().label('committment'),\
    BoulderModel.fa.label('fa'),\
    BoulderModel.description.label('description'),\
    BoulderModel.pro.label('pro'),\
    BoulderModel.elevation.label('elevation'),\
    BoulderModel.lat.label('lat'),\
    BoulderModel.lng.label('lng'))\
    .filter(BoulderModel.parent_id==entry['id']).filter(BoulderModel.parent_name==entry['name'])
# Check routes
routes = db.session.query(RouteModel.position.label('position'),\
    RouteModel.climb_type.label('climb_type'),\
    RouteModel.id.label('id'),\
    RouteModel.name.label('name'),\
    RouteModel.grade.label('grade'),\
    RouteModel.quality.label('quality'),\
    RouteModel.danger.label('danger'),\
    RouteModel.pitches.label('pitches'),\
    RouteModel.committment.label('committment'),\
    RouteModel.fa.label('fa'),\
    RouteModel.description.label('description'),\
    RouteModel.pro.label('pro'),\
    RouteModel.elevation.label('elevation'),\
    RouteModel.lat.label('lat'),\
    RouteModel.lng.label('lng'))\
    .filter(RouteModel.parent_id==entry['id']).filter(RouteModel.parent_name==entry['name'])
# Union boulders + routes and sort
q = boulders.union(routes)
children = q.order_by('position')

gradeByClimb_type = {'boulder': boulderInt2Grade, 'route': routeInt2Grade}
# Append info to corresponding lists
for child in children:
    # (position, climb_type, id, name, grade, quality, danger, pitches, committment, fa, desc, pro, elev, lat, lng)
    child_entry = {
        'id': child[2],
        'name': child[3],
        'grade': gradeByClimb_type[child[1]](child[4]),
        'quality': child[5],
        'danger': dangerInt2Movie[child[6]],
        'pitches': child[7],
        'committment': child[8],
        'fa': child[9],
        'description': child[10],
        'pro': child[11],
        'elevation': child[12],
        'lat': child[13],
        'lng': child[14],
        'route': f"{child[1]}/{child[2]}/{child[3]}"
    }
    if child[0] == 0:
        unsorted_info.append(child_entry)
    else:
        sorted_info.append(child_entry)


print(sorted_info)

if __name__ == '__main__':
    app.run(debug=True)
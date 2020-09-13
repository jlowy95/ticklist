from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:cZechmat3@localhost/MyTicksClimbs"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# class CarsModel(db.Model):
#     __tablename__ = 'cars'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String())
#     model = db.Column(db.String())
#     doors = db.Column(db.Integer())

#     def __init__(self, name, model, doors):
#         self.name = name
#         self.model = model
#         self.doors = doors

#     def __repr__(self):
#         return f"<Car {self.name}>"

class AreaModel(db.Model):
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
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
            'parent_id': self.parent_id,
            'parent_name': self.parent_name,
            'path': self.path,
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


new_car = AreaModel(name='North America',
    parent_id=1, 
    parent_name='All Locations',
    path='1/All Locations',
    description='This is North America babyyyyyyy', 
    elevation=None, 
    lat=121.7860, 
    lng=86.7693)
db.session.add(new_car)
db.session.commit()
myQuery = db.session.query(AreaModel).filter(AreaModel.name=='North America').first()
print(myQuery.toJSON()['properties']['coords']['lat'])

# @app.route('/cars', methods=['POST', 'GET'])
# def handle_cars():
#     if request.method == 'POST':
#         if request.is_json:
#             data = request.get_json()
#             new_car = CarsModel(name=data['name'], model=data['model'], doors=data['doors'])
#             db.session.add(new_car)
#             db.session.commit()
#             return {"message": f"car {new_car.name} has been created successfully."}
#         else:
#             return {"error": "The request payload is not in JSON format"}

#     elif request.method == 'GET':
#         cars = CarsModel.query.all()
#         results = [
#             {
#                 "name": car.name,
#                 "model": car.model,
#                 "doors": car.doors
#             } for car in cars]

#         return {"count": len(results), "cars": results}

if __name__ == '__main__':
    app.run(debug=True)
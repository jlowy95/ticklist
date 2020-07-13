# Author Josh Lowy 

# Flask app for MyTicks
# Connects to local MongoDB and allows for easy maintenance and logging of
# ticked climbs and tracking of ascents.

from flask import Flask, render_template, redirect, request, jsonify
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
Types:  0 - Area, 1 - Boulder, 2 - Route
{
    _id: ObjectID(5f091fca617c42623517786f),
    name: 'North America',
    type: 0,
    parent: null,
    children: [],
    properties: {
        description: 'North America is pretty.'
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

# Home Route
@app.route('/')
def index():
    return render_template('index.html')


# API Routes
# Loads the corresponding page type to the entry requested
@app.route('area/<entry_id>')
def area(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = areas_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        return render_template('area.html')
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
# addArea (adds a sub-area to the current area)
@app.route('/new-area')
def addArea():
    return render_template('addArea.html')

@app.route('/new-boulder')
def addBoulder():
    return render_template('addBoulder.html')

@app.route('/new-route')
def addRoute():
    return render_template('addRoute.html')



if __name__ == '__main__':
    app.run(debug=True)

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
app.config["MONGO_URI"] = "mongodb://localhost:27017/MyTicksClimbs"
mongo = PyMongo(app)

# Define collection for primary use
climbs_col = mongo.db.climbs

# Sample Entry
'''
Types: 0 - Continent (highest), 1 - Area, 2 - Boulder, 3 - Route
{
    _id: ObjectID(5f091fca617c42623517786f),
    name: 'North America',
    type: 0,
    parent: null,
    children: [],
    properties: {
        description: 'North America is pretty.'
        images: []
    }
}
'''

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# API Route
# Loads the corresponding page type to the entry requested
@app.route('/climbs/<entry_id>')
def area(entry_id):
    print(f'Entry: {entry_id}')
    try:
        entry = climbs_col.find_one({'_id': ObjectId(f'{entry_id}')})
        print(f'Entry: {entry}')
        templates = {0: 'continent.html',
            1: 'area.html',
            2: 'boulder.html',
            3: 'route.html'}
        return render_template(templates[entry['type']])
    except Exception as e:
        print(e)
        return render_template('index.html')


# Search query route
@app.route('/search/<search_terms>')
def search(search_terms):
    print(search_terms)

if __name__ == '__main__':
    app.run(debug=True)

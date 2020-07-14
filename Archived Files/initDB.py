from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)

db = client.MyTicks

areas = db.areas
areas.drop()
areas = db.areas

state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

for state in state_names:
    entry = {
        'name': state,
        'parentID': 'all-locations',
        'path': '',
        'children': [],
        'properties': {
            'description': '',
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
    }
    _id = areas.insert_one(entry)
    # print(_id.inserted_id)
    areas.update_one({'_id': ObjectId(_id.inserted_id)}, {'$set': {'path': ('all-locations$area/' + str(_id.inserted_id))}})
    print(areas.find_one({'_id': ObjectId(_id.inserted_id)}))
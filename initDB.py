from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.MyTicks

areas = db.areas


state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

for state in state_names:
    entry = {
        'name': state,
        'parent': '',
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
    areas.insert_one(entry)
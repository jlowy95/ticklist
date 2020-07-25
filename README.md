# MyTicks
### Personal Ticklist App Project

## Todo
1. Decide on final database structure !!IN PROGRESS!!
  1. MongoDB
    - Paths between parents/children, retain redundant info or load multiple items (Load multiple items)
  2. MySQL
    - All parent info stored in child
    - All child info retrieved by simple query
    - Uneven layering/depth between items???
  - Clarify images property
2. Integrate Flask to html templates !!IN PROGRESS!!
  - Pass common html elements for simpler templates
  - Add images to areas template
3. Add validation
  - Both client and server side to changes/additions (DONE)
  - Add validation for difficulty/numeric values
4. Begin DB loading through 'add' forms

## Planned Framework/Dependencies
- Description: Flask web-app for tracking/recording climbs
- Primary Language: Python
- Database: MongoDB
  - Because of unknown/unpredictable hierarchy, NOSQL allows for more flexibility
  - Assign parent (Mongo \_id) to each climb/area for lookup based on parents/children without true nesting
- Functionailty
  - Setup API based on entry ids of climbs/areas
  - Different page templates will load for each 'datatype'
## Planned Functionality
- Userbase
  - Personal Ticks
  - Password Protected
  - Statistics
  - Wishlist
- Climbs/Areas
  - Different 'type' attribute for custom pages for areas, boulders, routes, etc.
  - Sample object:
  ```
  {
    _id: ObjectId(5f0d16cac6b1d534f316b56c),
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
  ```
- Characteristics
  - Climbs
    - Grade
    - Name
    - Danger
    - Quality
    - Description
    - \# of times climbed/repeats
    - Height/Pitches
    - Committment
    - FA
    - Notes for each send
  - Areas
    - Name
    - Description
    - Parent area/country

## Navigation
- Databases
  - MyTicksClimbs
    
    Hosts areas and climbs with their attributes
  - MyTicksUsers
    
    Holds users and their ticks tracked by climb \_id

# MyTicks
### Personal Ticklist App Project

## Todo
1. Decide on final database structure !!IN PROGRESS!!
  - Paths between parents/children, retain redundant info or load multiple items
  - Clarify images property
2. Integrate Flask to html templates !!IN PROGRESS!!
  - Add images to areas template
3. Add validation
  - Both client and server side to changes/additions
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
    \_id: ObjectID(5f091fca617c42623517786f),    
    name: 'North America',    
    type: 0,    
    parent: null,   
    children: [5f091fca617c42623517786f, 5f091fca617c42623517786f, 5f091fca617c42623517786f],   
    properties: {       
        description: 'North America is pretty.'       
        images: []     
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

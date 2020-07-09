# Personal Ticklist App Project

## Planned Functionality
- Userbase
  - Personal Ticks
  - Password Protected
  - Statistics
  - Wishlist
- Climbs
  - JSON object for type (i.e. Ropes, Boulders, Ice)
  - Undefined area hierarchy: 
    Not just Country, region, area, wall, climb.  Allows for sub-areas within sub-areas, etc.
  - Characteristics:
    - Grade
    - Name
    - Danger
    - Quality
    - Description
    - \# of times climbed/repeats
    - Height
    - FA
    - Notes for each send
    - Parent area
- Areas
  - JSON object for area
    - Continents will be collections, highest level of hierarchy
  - Characteristics
    - Name
    - Description
    - Parent area/country
## Planned Framework/Dependencies
- Primary Language: Python
- Database: MongoDB
  - Because of unknown/unpredictable hierarchy, NOSQL allows for more flexibility
  - Assign parent (and Mongo \_id) to each climb/area in "app" before loading to db
## Navigation
- Databases
  - MyTicksClimbs
    Hosts areas and climbs with their attributes
  - MyTicksUsers
    Holds users and their ticks tracked by climb \_id
- Files
  - climbNav.py
    Helps user navigate MyTicksClimbs database, add climbs/areas

# Personal Ticklist App Project

## Planned Functionality
- Userbase
  - Personal Ticks
  - Password Protected
  - Statistics
  - Wishlist
- Climbs
  - Python class/object for type (i.e. Ropes, Boulders, Ice)
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
  - Python class/object for area and country
    - Country will be highest level of hierarchy
  - Characteristics
    - Name
    - Description
    - Parent area/country
## Planned Framework/Dependencies
- Primary Language: Python
- Database: MongoDB
  - Because of unknown/unpredictable hierarchy, NOSQL allows for more flexibility
  - Assign parent and key to each climb/area (not country) in "app" before loading to db


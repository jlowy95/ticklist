# MyTicks
### Personal Ticklist App Project

## Todo
1. Decide on final database structure !!IN PROGRESS!!
  - Clarify images property
  - Research forum/comment nesting
  - Research userbase storage
2. Integrate Flask to html templates (DONE)
  - Flask templating used for area pages
3. Add functionality for rope climbs
  - Add entry routes/functions
  - Necessary validation
4. Add validation
  - Both client and server side to changes/additions (Areas+Boulders DONE)
  - Add validation for difficulty/numeric values (Areas+Boulders DONE)
4. Begin DB loading through 'add' forms
5. Add GPS UI
  - Front-end interactive map

## Framework/Dependencies
- Description: Flask web-app for tracking/recording climbs
- Primary Language: Python
- Database: MySQL

## Planned Functionality
- Userbase
  - Personal Ticks
  - Password Protected
  - Statistics
  - Wishlist
  - Beta mapping/noting
- Database
  - Area-focused navigation
    - All climbs of a wall/boulder viewable on the same page
    - Primary image planned as interactive 'map' of climbs
  - Unique templates based on climb type
    - Better distinction between climb types
    - No extraneous/irrelevant data
    - Cleaner/more direct layouts to priority information
- Characteristics
  - Climbs
    - Grade
    - Name
    - Danger
    - Characteristic Attributes (i.e. Reachy, Thought-provoking, Chossy)
    - Quality
    - Description
    - Directions/Getting there
    - Protection
    - \# of times climbed/repeats
    - Height/Pitches
    - Committment
    - FA
    - Notes for each send
  - Areas
    - Name
    - Description
    - Location Data/GPS
    - Directions/ Getting there
    - Parent area/country

## Navigation
- Databases
  - MyTicksClimbs
    
    Hosts areas and climbs with their attributes
  - MyTicksUsers

# MyTicks
### Personal Ticklist App Project

## Todo
1. Decide on final database structure !!IN PROGRESS!!
  - Clarify images property
  - Research forum/comment nesting
  - Research userbase storage
2. Add validation
  - Both client and server side to changes/additions (Areas+Boulders+Routes IN PROGRESS)
  - Add validation for difficulty/numeric values (Areas+Boulders+Routes DONE)
  - Finalize 'required' form fields and corresponding validation/implementation needed
3. Design/implement mass upload feature
  - Begin DB loading
4. Add GPS UI
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
    - areas
      - id
      - name
      - parent_id
      - parent_name
      - area_type
        - 0: No distinction
        - 1: Sub-areas
        - 2: Climbs
      - path
      - description
      - directions
      - elevation
      - lat
      - lng
      - date_inserted
    - climbs
      - id
      - name
      - parent_id
      - parent_name
      - position
      - quality (integer scale)
      - danger
        - 0: G
        - 1: PG-13
        - 2: R
        - 3: X
      - height
      - fa
      - description
      - pro
      - climb_type (for distinction between boulders and routes)
      - date_inserted
    - boulders
      - id (fk to climbs.id)
      - grade
    - routes
      - id (fk to climbs.id)
      - grade (integer scale)
      - pitches
      - committment
      - route_type
        - 1: 'sport'
        - 2: 'trad'
        - 3: 'dws'
    - danger
      - id
      - movie
    - tags
      - tagID
      - tagTitle
    - tagClimb
      - climbID
      - tagID
  - MyTicksUsers

import csv
import string
import pandas as pd

'''
Mass Input Reader
Reads and formats to-be-added climbs and areas from a templated .csv file
to MyTicks database-ready format

Example template can be found in repository

Template:
As many 'area#' columns  for area names as neccessary to reach an already established area.
'area1' being the highest in the directory, consecutively moving down to the immediate parent.
These are to be left blank for entries which do not require the same number of parent areas.

'Climb' to be used for the climb name.
If unnamed, use descriptors in addition to 'unnamed' (i.e. Unnamed Arete) or alternatively,
the guidebook reference number, or create a reference number (i.e. Unnamed (3)).

'Climb_Type' denotes the type of climb: 'boulder' or 'route'.  This can be easily copy-pasted as needed.

'Grade' will be read in accordance to 'climb_type' and a selected option on input for USA/Euro
 but can be in any standard format:
    Boulders
        USA/Vermin: plain integer (3), V format (V10), plus/minus/hyphen format (V3+ or V3-4)
        Euro/Font: standard format w/letters and pluses (7C+)
    Routes
        USA/YDS: integer-letter (10b), 5 scale (5.12b), plus/minus (5.9+)
        Euro/Fr: standard format w/letters and pluses and slashes (8b+/c)
MyTicks will standardize some of these inputs (i.e. 5.9+ will be rounded to 5.9 until concensus)

'Pitches','Committment','Route_Type' are only for routes and may be left blank for boulders (or will be ignored)
'Pitches' the integer number of pitches (can be between 1 and 50)
'Committment' can be read as an integer or roman numeral (can be between 1 and 6)
'Route_Type' can be 'sport', 'trad', 'deep water solo', or abbreviated 's', 't', 'dws'

'Height' is measured in feet and can be between 1 and 4500

'Quality' can be read as an integer (1-5) or as a series of characters (*** would be 3)

'Danger' can be read as an integer or movie grade as follows:
    0: 'G'
    1: 'PG-13'
    2: 'R'
    3: 'X'
If left blank, it will be assumed as 'G' / 0

'FA', 'Description', 'Pro' are optional but appreciated.
Similarly, area details for any/all new areas can be added after input.
'''

# Assign path to mass_input file (to be changed to uploaded file)
path = 'mass_input_template2.csv'

# Open and read the .csv file
with open(path, newline='', encoding='utf-8-sig') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    current_row = next(csvreader)
    #  Check for headers
    for col in current_row: 
        if 'Area' in col:
            print('Header detected.')
            break
        else:
            print('Header not found, resetting reader.')

    for row in csvreader:
        print(row)
        # Indices 0-5 are parent areas, 5 - Climb, 6 - Climb_Type, 7 - Grade,
        # 8 - Route_type, 9 - Height, 10 - Quality, 11 - Danger,
        # 12 - FA, 13 - Description, 14 - Protection

        # Check areas for existing entries/parents,
        #  creating new areas as needed within the newly provided parents
        connection = False
        for area in row[0:5]:
            if area == '':
                continue
            else:
                if not connection:
                    parent_check = findParents(area)
                    if parent_check[0] == 1:
                        # If no connection is yet established, mark the connection as this area
                        connection = parent_check[1]
                if connection:
                    parent_check = findParents(area)
                    if parent_check[0] == 1:
                        # A connection is already established, but a child lower in the tree still matches, 
                        # Replace the connection
                        connection = parent_check[1]
                    elif parent_check[0] == 0:
                        # New area found beneath connection, add as new area, area_type defaults 0


                        '''MAP TREE AS DICTIONARY FOR LATER REFERENCE'''



# findParents: Queries the AreaModel for names matching that provided.
# Returns a tuple - (Found Case (0-2), Match (As db.object))
# Found Case: 0-False, 1-True, 2-Multiple found user parsing needed
def findParents(area_name):
    # Query for matching (like) area name
    likeFormat = "%{}%".format(area_name)
    matches = db.session.query(AreaModel)\
        .filter(AreaModel.name.like(likeFormat)).all()

    if matches:
        # If multiple matches, present results to user.
        if len(matches) > 1:
            for match in matches:
                print(match)

        else: # Else, a single match has been found
            return (1, matches)
    else:
        return (0)

    

# raw_import = pd.read_csv(path)
# print(raw_import.head())
import csv
import string

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
# Author Josh Lowy

# Connect to ticklist database
# Define functions for adding areas and climbs

from pymongo import MongoClient

# Setup db client and database
client = MongoClient('mongodb://localhost:27017/')
db = client.ticklist


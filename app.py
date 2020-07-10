# Author Josh Lowy 

# Flask app for MyTicks
# Connects to local MongoDB and allows for easy maintenance and logging of
# ticked climbs and tracking of ascents.

from flask import Flask, render_template, redirect, request, jsonify
from flask_pymongo import PyMongo
import json
import pprint

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/ticklist"
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/navDB', methods=['POST'])
def predict_rent_price():
    collection = request.get_json()

if __name__ == '__main__':
    app.run(debug=True)

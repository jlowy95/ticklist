// Node MyTicks App

//Import Modules
const express = require('express');
const http = require('http');
const url = require('url');
const fs = require('fs');
const formidable = require('formidable');
const csv = require('csv-parser');
const path = require('path');
var mods = require('./nodemodules');

// Create app Instance
const app = express();
const port = 8080;

app.get('/', (req,res) => {
    // Temporary reroute to All Locations
    res.send('Hello World!');
});

app.get('/all-locations', (req,res) => {
    fs.readFile('../templates/allLocations.html', function(err, data) {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.write(data);
        return res.end();
    });
    // res.send('All Locations');
});



// Listen/Run App
app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`);
});
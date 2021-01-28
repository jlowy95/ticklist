// massimport.js: Handle file uploads for the mass importer tool and parse csv files for client-side 
// data validation, then push to server for submission.

// Define "submit" button
var continueButton = $('#continue');
continueButton.on('click', processFile);

// Client file upload
var mifile;

// Listener for file choice
$('#mifile').on('change', storeFile);

// storeFile: Listens for file upload then reads/stores data into global var 'mifile'.
// Continue button for further processing is then displayed.
function storeFile (evt) {
    // Get files from file change/upload event
    var files = evt.target.files;
    // Store file data out of function scope (client-side still)
    var file = files[0]; 
    var reader = new FileReader();
    reader.onload = function(event) {
        // console.log(event.target.result);
        mifile = event.target.result.split(/\r\n|\n/).slice(1); 
    };
    reader.readAsText(file);
    // Display continue button
    continueButton.css('display', 'block');
}

// processFile: Opens user correction/validation tools and runs csv parsing tools for server imports
function processFile () {
    // console.log(mifile);
    // Hide form and continue button, display instructions and processing
    $('#fileform').css('display','none');
    continueButton.css('display', 'none');
    $('#processing').css('display', 'block');
    // more processing functions
    start();
}

// User input controls for processing
$('#yesButton').on('click', buttonsHandler);
$('#noButton').on('click', buttonsHandler);
$('#skipButton').on('click', buttonsHandler);

// Switch handler for user processing inputs
function buttonsHandler() {
    var src = event.srcElement.id.slice(0,-6);
    // console.log(src);
    switch(src) {
        case ('yes'):
            console.log('Yes');
            break;
        case('no'): 
            console.log('No');
            break;
        case('skip'):
            console.log('Skip');
            iterateRow();
            break;
    }
}

//----------------------------------------------------------------
// Iterating functions for csv processing and user input
var currentIndex = 0;

function nextRow() { //Iterate row by row of imported csv file
    if (currentIndex < mifile.length) {
        // Separate details
        currentRow = mifile[currentIndex].split(',');
        var entry = separateDetails(currentRow);
        console.log(entry);

        // Check Database
        // var check = checkEntry(entry);
        // console.log(`check:${check}`);
        // getEntry(entry);
        dupeCheck(entry);

        // Clear contents of previous entry
        $('#areas').empty();
        $('#climb').empty();
        $('#details').empty();
        // Populate contents of current entry
        for (var i = 0; i<entry.areas.length; i++) {
            $('#areas').append($('<span></span>').text(entry.areas[i]));
            if (i<entry.areas.length-1 && entry.areas[i+1]!='') {
                $('#areas').append(' > ');
            }
        }
        $('#climb').append($('<span></span>').text(entry.name));
        for (var i = 0; i<entry.details.length; i++) {
            $('#details').append($('<span></span>').text(entry.details[i]));
            if (i<entry.details.length-1) {
                $('#details').append(', ');
            }
        }
    } else {
        alert('Temp Done!');
    }
}

function start() {
    currentIndex = 0;
    nextRow();
}

function iterateRow() {
    currentIndex++;
    nextRow();
}

function checkEntry(entry) {
    fetch('/check-entry', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(entry)
    })
    .then (response => response.json())
    .then (function(data) {
        console.log(data);
    })
    .catch(error => console.log(error));
}


async function getEntry(entry) {
    for (var i=0; i<entry.areas.length; i++) {
        await fetch(`/check-entry?area=${entry.areas[i]}`, {
            method: 'GET'
        })
        .then (response => response.json())
        .then (function(data) {
            console.log(data);
        })
        .catch(error => console.log(error));
    }
}

// dupeCheck: Sends a GET request to check if a duplicate climb under final listed area exists
function dupeCheck(entry) {
    fetch(`/check-entry?type=dupe&area=${entry.areas[-1]}&climb=${entry.name}`, {
        method: 'GET'
    })
    .then (response => response.json())
    .then (function(data) {
        console.log(data);
    })
    .catch(error => console.log(error));
}

// separateDetails: Takes the row/entry and creates an object for distinction of details/areas/name
function separateDetails(row) {
    var entry = {'details':{}};
    // Separate entry details
    var parents = row.slice(0,6);
    parents = parents.filter(item => item !== '');
    // Object Assignment
    entry.areas = parents;
    entry.name = row.slice(6,7);
    entry.details.climb_type = row.slice(7,8);
    entry.details.grade = row.slice(8,9);
    entry.details.pitches = row.slice(9,10);
    entry.details.committment = row.slice(10,11);
    entry.details.route_type = row.slice(11,12);
    entry.details.height = row.slice(12,13);
    entry.details.quality = row.slice(13,14);
    entry.details.danger = row.slice(14,15);
    entry.details.fa = row.slice(15,16);
    entry.details.description = row.slice(16,17);
    entry.details.pro = row.slice(17);
    return entry;
}
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
        currentRow = mifile[currentIndex].split(',');
        // Separate entry details
        var areas = currentRow.slice(0,6);
        areas = areas.filter(item => item !== '');
        console.log(areas);
        var name = currentRow.slice(6,7);
        var details = currentRow.slice(7);
        // Clear contents of previous entry
        $('#areas').empty();
        $('#climb').empty();
        $('#details').empty();
        // Populate contents of current entry
        for (var i = 0; i<areas.length; i++) {
            $('#areas').append($('<span></span>').text(areas[i]));
            if (i<areas.length-1 && areas[i+1]!='') {
                $('#areas').append(' > ');
            }
        }
        $('#climb').append($('<span></span>').text(name));
        for (var i = 0; i<details.length; i++) {
            $('#details').append($('<span></span>').text(details[i]));
            if (i<details.length-1) {
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

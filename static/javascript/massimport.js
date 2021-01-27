// massimport.js: Handle file uploads for the mass importer tool and parse csv files for client-side 
// data validation, then push to server for submission.

// Define "submit" button
var continueButton = d3.select('#continue');
continueButton.on('click', processFile);

// Client file upload
var mifile;

// Listener for file choice
document.getElementById('mifile').addEventListener('change', storeFile, false);

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
    continueButton.style('display', 'block');
}

// processFile: Opens user correction/validation tools and runs csv parsing tools for server imports
function processFile () {
    console.log(mifile);
    // Hide form and continue button, display instructions and processing
    d3.select('#fileform').style('display','none');
    continueButton.style('display', 'none');
    d3.select('#processing').style('display', 'block');
    // more processing functions
    start();
}

// User input controls for processing
d3.select('#yesButton').on('click', buttonsHandler);
d3.select('#noButton').on('click', buttonsHandler);
d3.select('#skipButton').on('click', buttonsHandler);

// Switch handler for user processing inputs
function buttonsHandler() {
    var src = d3.event['srcElement']['id'].slice(0,-6);
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

// Iterating functions for csv processing and user input
var currentIndex = 0;

function nextRow() {
    if (currentIndex < mifile.length) {
        currentRow = mifile[currentIndex];
        d3.select('#currentRow').text(currentRow);
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

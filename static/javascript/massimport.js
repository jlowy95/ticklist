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
        mifile = event.target.result; 
    };
    reader.readAsText(file);
    // Display continue button
    continueButton.style('display', 'block');
}

// processFile: Opens user correction/validation tools and runs csv parsing tools for server imports
function processFile () {
    console.log(mifile);
    
}
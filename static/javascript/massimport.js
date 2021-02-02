// massimport.js: Handle file uploads for the mass importer tool and parse csv files for client-side 
// data validation, then push to server for submission.

// -------------- PSUEDO -------------------
// 1. Input csv file
// 2. Read csv
// 3. Iterate by row
// 4. Validate data
//   a. Check for duplicate
//   b. Validate data
//     1. Check climb_type
//     2. Check grade
//     3. Check quality & danger (required)
//     4. Optionally validate other details
//     - If valid, addEntry
//     - If invalid, pause, attempt to fix, REvalidate
// 5. Locate entry insert or create new area
// 6. Update user (status)


// -------------- CODE ---------------------

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
        console.log(entry.name);

        // Check Database
        // var check = checkEntry(entry);
        // console.log(`check:${check}`);
        // getEntry(entry);

        // Clear contents of previous entry
        $('#areas').empty();
        $('#climb').empty();
        $('#details').empty();

        // Populate contents of current entry
        for (let i = 0; i<entry.areas.length; i++) {
            $('#areas').append($('<span></span>').text(entry.areas[i]));
            if (i<entry.areas.length-1 && entry.areas[i+1]!='') {
                $('#areas').append(' > ');
            }
        }
        $('#climb').text(entry.name);
        $('#grade').text(function() {
            if (entry.details.climb_type == 'boulder') {
                return 'V' + entry.details.grade;
            } else if (entry.details.climb_type == 'route') {
                return '5.' + entry.details.grade;
            } else {
                return 'N/A';
            }
        });
        $('#danger').text(function() {
            switch (entry.details.danger) {
                case '0':
                    return '';
                case '1':
                    return 'PG-13';
                case '2':
                    return 'R';
                case '3':
                    return 'X';
                default:
                    return 'N/A';
            }
        });
        $('#quality').html(function() {
            var quality = '';
            for (let i=0; i<entry.details.quality;i++) {
                quality += '&#9733';
            }
            return quality;
        });
        
        // for (let detail in entry.details.keys) {

        // }
        // for (let i in entry.details.keys) {
        //     $('#details').append($('<span></span>').text(entry.details[i]));
        //     if (i<entry.details.keys.length-1) {
        //         $('#details').append(', ');
        //     }
        // }

        // add current row to table
        addTRow(entry);
        // Check for duplicate, if dupe, continue
        dupeCheck(entry);

        gradeCheck(entry);

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

// --------------------------------------------------------------

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
    for (let i=0; i<entry.areas.length; i++) {
        await fetch(`/check-entry?area=${entry.areas[i]}`, {
            method: 'GET'
        })
        .then (response => response.json())
        .then (function(data) {
            // console.log(data);
        })
        .catch(error => console.log(error));
    }
}

// dupeCheck: Sends a GET request to check if a duplicate climb under final listed area exists
function dupeCheck(entry) {
    fetch(`/check-entry?type=dupe&area=${entry.areas[entry.areas.length-1]}&climb=${entry.name}`, {
        method: 'GET'
    })
    .then (response => response.json())
    .then (function(data) {
        // If duplicate was found, update status
        if (data.dupeCheck) {
            $(`#tr-${currentIndex+1} td:last span`).css('background', 'blue');
            // Continue
            iterateRow();
        }
        // console.log(data);
    })
    .catch(error => console.log(error));
}

// addTRow
function addTRow(entry) {
    // Isolate data we want for the table (in order)
    var table_data = [(currentIndex+1),entry.areas[0],entry.areas[entry.areas.length-1],entry.name,entry.details.climb_type,entry.details.grade];
    // Create tr object
    var tblRow = $(`<tr id="tr-${currentIndex+1}">`);
    // Append td's to tr
    $.each(table_data, function(i,v) {
        tblRow.append('<td>' + v + '</td>');
    });
    tblRow.append('<td class="text-center"><span class="square"></span></td>');
    // Append our completed tr to the tbody
    $('tbody').append(tblRow);
}

// separateDetails: Takes the row/entry and creates an object for distinction of details/areas/name
function separateDetails(row) {
    var entry = {'details':{}};
    // Separate entry details
    var parents = row.slice(0,6);
    parents = parents.filter(item => item !== '');
    // Object Assignment
    entry.areas = parents;
    entry.name = row[6];
    // If name was omitted, skip
    if (entry.name == '') {
        iterateRow();
    }
    entry.details.climb_type = row[7];
    entry.details.grade = row[8];
    entry.details.pitches = row[9];
    entry.details.committment = row[10];
    entry.details.route_type = row[11];
    entry.details.height = row[12];
    entry.details.quality = row[13];
    entry.details.danger = row[14];
    entry.details.fa = row[15];
    entry.details.description = row[16];
    entry.details.pro = row[17];
    return entry;
}

// gradeCheck:
function gradeCheck(entry) {
    // All inputs of type string as parsed by FileReader
    // TEMPORARY: grades will be submitted as whole US grades w/o V or 5.
    var climb_type = entry.details.climb_type.toLowerCase();
    var grade = entry.details.grade.toLowerCase();
    console.log('gradeCheck: ' + grade);

    // Check for valid symbols
    var valids = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','+','-','/'];
    for (let i=0;i<grade.length;i++) {
        // If character isn't valid...
        if (!(valids.includes(grade[i]))) {
            console.log('INVALID GRADE - Character: ' + grade[i]);
            // User Correction Needed
        }
    }

    // Boulder grades may have +/- at end
    // if (climb_type == 'boulder') {
    //     // Check for +/- in grade
        
    //     // Remove +/- if attached
    //     if (grade.endswith('+') || grade.endswith('-')) {
    //         grade = grade.slice(0,-1);
    //     // Check that base integer is btw 0-16
    //     if (parseInt(grade) >= 0 && parseInt(grade) <= 16) {
    //         console.log('Valid grade');
    //     } else {
    //         console.log('INVALID GRADE - boulderNot0-16');
    //     }

    // } else if (climb_type == 'route') {
        
    // } else {
    //     // Invalid climb_type
        
    // }
}
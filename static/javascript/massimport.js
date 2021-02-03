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
    // start();
    justRun();
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
var invalids = [];
var r2i = [];
var completed = 0;

async function nextRow() { //Iterate row by row of imported csv file
    if (currentIndex < mifile.length) {
        // Separate details
        currentRow = mifile[currentIndex].split(',');
        var entry = separateDetails(currentRow);
        // console.log(entry.name);

        updatePBar();

        // Clear contents of previous entry
        $('#areas').empty();
        // $('#climb').empty();
        // $('#details').empty();

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
        
        // add current row to table
        addTRow(entry);

        // Validate Data
        // Check for duplicate, if dupe, continue
        var duped = await dupeCheck(entry);
        if (!duped) {
            validateEntry(entry);
        }
        return true;

    } else {
        updatePBar();
        console.log('DONE!');
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

async function justRun() {
    currentIndex=0;
    while (currentIndex<mifile.length) {
        let nr = await nextRow();
        if (nr) {
            currentIndex++;
        }
    }
    stopPBar();
    alert('Validation Complete! Please attend to the "Input Needed" entries.');
}


// ----------------- Validation Functions -----------------------


// validateEntry: Collective fn for calling individual validation functions.  If invalid, adds entry to
// invalids with error code
function validateEntry(entry) {
    // * Dupe check run separately

    // Invalid Keys
    // {
    //  'valid': t/f
    //  'entry': entry,
    //  'error': ### (hundreds-fn/src, ones-code),
    //  'tblID': currentIndex+1
    // }

    // 1. Check climb_type/grade
    // 2. Check quality & danger (required)
    // 3. Optionally validate other details
    var vfns = [gradeCheck, qualCheck, dangCheck];
    var valid = true;
    for (let i=0;i<vfns.length;i++) {
        var res = vfns[i](entry);
        // If invalid response, add entry to invalids and iterateRow
        if (!res.valid) {
            $(`#tr-${currentIndex+1} td:last span`).css('background', 'yellow');
            invalids.push(res);
            valid = false;
            break;
        }
    }
    // If still valid, add to r2i array
    if (valid) {
        $(`#tr-${currentIndex+1} td:last span`).css('background', 'greenyellow');
        r2i.push({'entry': entry, 'tblID': currentIndex+1});
    }
}

// dupeCheck: Sends a GET request to check if a duplicate climb under final listed area exists
async function dupeCheck(entry) {
    await fetch(`/check-entry?type=dupe&area=${asciiURL(entry.areas[entry.areas.length-1])}&climb=${asciiURL(entry.name)}`, {
        method: 'GET'
    })
    .then (response => response.json())
    .then (function(data) {
        // If duplicate was found, update status
        if (data.dupeCheck) {
            $(`#tr-${currentIndex+1} td:last span`).css('background', 'blue');
            completed++;
            // Continue
            return true;
        } else {
            return false;
        }
        
    })
    .catch(error => console.log(error));
}

// gradeCheck: Performs basic validation on the climb_type and grade details of the current entry
function gradeCheck(entry) {
    // All inputs of type string as parsed by FileReader
    // TEMPORARY: grades will be submitted as whole US grades w/o V or 5.
    var climb_type = entry.details.climb_type.toLowerCase();
    var grade = entry.details.grade.toLowerCase();
    // console.log('gradeCheck: ' + grade);

    // Check for valid symbols
    var valids = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','+','-','/'];
    var letterCount = 0;
    for (let i=0;i<grade.length;i++) {
        // Count letters to check no more than 1
        if (['a','b','c','d'].includes(grade[i])) {
            letterCount++;
        }
        // If character isn't valid...
        if (!(valids.includes(grade[i]))) {
            console.log(entry.name + 'INVALID GRADE - Character: ' + grade[i]);
            return {'valid': false, 'entry': entry, 'error': 101, 'tblId': currentIndex+1};
        }
    }
    if (letterCount>1) {
        console.log(entry.name + 'INVALID GRADE - multipleLetters: ');
        return {'valid': false, 'entry': entry, 'error': 109, 'tblId': currentIndex+1};
    }


    // Check for +/- in grade and only at end
    if (grade.includes('+') || grade.includes('-')) {
        if (grade.endswith('+') || grade.endswith('-')) {
            // +\- OK, remove for further validation
            grade = grade.slice(0,-1);
        } else {
            // +\- in middle, INVALID
            console.log(entry.name + 'INVALID GRADE - Out of place +\-');
            return {'valid': false, 'entry': entry, 'error': 102, 'tblId': currentIndex+1};
        }
    }

    // Boulder grades may have +/- at end
    if (climb_type == 'boulder') {
        // Check for letters (ONLY USD), VB acceptable
        if (grade === 'b') {
            return {'valid': true};
        } else if (['a','b','c','d'].some(r => grade.includes(r))) {
            console.log(entry.name + 'INVALID GRADE - Letters in boulder');
            return {'valid': false, 'entry': entry, 'error': 103, 'tblId': currentIndex+1};
        }
        
        // Check that base integer is btw 0-16
        if (parseInt(grade) < 0 || parseInt(grade) > 16) {
            console.log(entry.name + 'INVALID GRADE - boulderNot0-16');
            return {'valid': false, 'entry': entry, 'error': 104, 'tblId': currentIndex+1};
        }

    } else if (climb_type == 'route') {
        // Check int, and check for letter based on int
        var intGrade = parseInt(grade);
        if (intGrade < 4 || intGrade > 15) {
            console.log(entry.name + 'INVALID GRADE - routeNot4-15');
            return {'valid': false, 'entry': entry, 'error': 105, 'tblId': currentIndex+1};
        } else if (intGrade < 10) {
            // Check for letter (letter for 5.9 and below is invalid)
            if (['a','b','c','d'].some(r => grade.includes(r))) {
                console.log(entry.name + 'INVALID GRADE - easyRouteLetter');
                return {'valid': false, 'entry': entry, 'error': 106, 'tblId': currentIndex+1};
            }
        } else { // Else 10 <= intGrade <= 15
            // Check for letter (letter is required now)
            if (['a','b','c','d'].some(r => grade.includes(r))) {
                // If letter, letter must be at end (+/- already removed)
                if (!(['a','b','c','d'].some(r => grade.endsWith(r)))) {
                    console.log(entry.name + 'INVALID GRADE - RouteMisplacedLetter');
                    return {'valid': false, 'entry': entry, 'error': 108, 'tblId': currentIndex+1};
                }
            } else {
                console.log(entry.name + 'INVALID GRADE - hardRouteNoLetter');
                return {'valid': false, 'entry': entry, 'error': 107, 'tblId': currentIndex+1};
            }
        }

    } else {
        // Invalid climb_type
        console.log(entry.name + 'INVALID CLIMB_TYPE');
        return {'valid': false, 'entry': entry, 'error': 201, 'tblId': currentIndex+1};
    }
    return {'valid': true};
}

// qualCheck: Returns a false JSON object if entry's quality is not 0-5
function qualCheck(entry) {
    if (parseInt(entry.details.quality) <= 0 || parseInt(entry.details.quality) >= 6) {
        console.log(entry.name + 'INVALID QUALITY');
        return {'valid': false, 'entry': entry, 'error': 301, 'tblId': currentIndex+1};
    } else {
        return {'valid': true};
    }
}

// dangCheck: Returns a false JSON object if the entry's danger is not 0-3 or standard movie
function dangCheck(entry) {
    // Check int or movie
    var dangInt = parseInt(entry.details.danger);
    if (!isNaN(dangInt)) {
        // Check if whole number
        if (dangInt % 1 === 0) {
            // Check if 0-3
            if (dangInt < 0 || dangInt > 3) {
                console.log(entry.name + 'INVALID dangerInt');
                return {'valid': false, 'entry': entry, 'error': 401, 'tblId': currentIndex+1};
            }
        } else {
            console.log(entry.name + 'INVALID Danger - not whole int');
            return {'valid': false, 'entry': entry, 'error': 402, 'tblId': currentIndex+1};
        }
    } else { // Else movie
        if (!(['G','PG','PG13','PG-13','R','X'].includes(entry.details.danger))) {
            console.log(entry.name + 'INVALID Danger - invalidMovie');
            return {'valid': false, 'entry': entry, 'error': 403, 'tblId': currentIndex+1};
        }
    }
    return {'valid': true};
}


// -------------------------- Other Functions ---------------------------


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
    // Trim excess spaces
    row = row.map(el => el.trim());

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

// asciiURL: Unidentified source is misconverting/reading get requests with "#" characters.  This function 
// properly converts spaces and '#' symbols to their ascii equivalents for url compatibility.
function asciiURL(mystring) {
    try {
        mystring = mystring.replace(" ", "%20");
        mystring = mystring.replace("#", "%23");
        return mystring;
    } catch (error) {
        console.log(`dupeCheck asciiURL error @ ${currentIndex}`);
        console.log(error);
    }
    
}

// updatePBar: updates/fills the progress bar based on the % of processed entries
function updatePBar() {
    var pbar_r2i = r2i.length/mifile.length*100;
    var pbar_in = invalids.length/mifile.length*100;
    var pbar_c = completed/mifile.length*100;
    $('#progressbar-c').css('width',`${pbar_c}%`);
    $('#progressbar-valid').css('width',`${pbar_r2i}%`);
    $('#progressbar-in').css('width',`${pbar_in}%`);
    // console.log(`C: ${pbar_c}, Valid: ${pbar_r2i}, IN: ${pbar_in}`);
}

function stopPBar() {
    $('#progressbar-valid').removeClass('progress-bar-striped');
    $('#progressbar-valid').removeClass('progress-bar-animated');
}
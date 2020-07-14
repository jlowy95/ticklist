// Grab current selection based on user navigation of db
    // Grab selected continent for db collection
    var collection = d3.select('#continents');
    collection.on('change', function(){
        var entry_id = collection.property('value')
        console.log(entry_id);
        window.location.href = `/climbs/${entry_id}`;
        console.log(`localhost:5000/climbs/${entry_id}`);
    });
    

// Fill new 'select' options based on user selections
// Default to 'This area is currently empty!'


// Grab inputted data
function get_inputs() {
    return $('#area-form').serializeArray();
}

// Add new entry
// function addEntry()
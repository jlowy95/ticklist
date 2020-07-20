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

// // Send request to flask and use response(prediction) in page
function call_API(data) {
    fetch('/submit-changes', {

            // Specify the method
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // A JSON payload
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(function(data) {
            console.log(data);
            window.location.href = data.redirect;
        });

}

function submit_data() {
    call_API(get_inputs());
}

var area_form_submit = d3.select('#area-form-submit');
area_form_submit.on('click', submit_data);
// Grab current selection based on user navigation of db
    // Grab selected continent for db collection
    var collection = d3.select('#continents');
    collection.on('change', function(){
        console.log(collection.property('value'));
    });
    

// Fill new 'select' options based on user selections
// Default to 'This area is currently empty!'


// Send request to flask and use response in page
function requestSelection(data) {
    fetch('/navDB', {

            // Specify the method
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // A JSON payload
            body: JSON.stringify(data)
        }).then(response => response.json())
        .then(function(data) {
            console.log(data);
        });

}
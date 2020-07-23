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

// Validate Form
// Disable form submissions if there are invalid fields
function validateForms() {
    // Get the forms we want to add validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
    if (form.checkValidity() === false) {
        console.log('Invalid form submission.');
    } else {
        // Else form is valid, submit to back-end
        console.log('Valid form submission.');
        submit_data();
    }
    form.classList.add('was-validated');
    }, false);   
}

// Collect inputted data
function get_inputs() {
    return $('#entry-form').serializeArray();
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
        })
        .catch(error => console.log(error));

}

function submit_data() {
    call_API(get_inputs());
}

var area_form_submit = d3.select('#area-form-submit');
area_form_submit.on('click', validateForms);
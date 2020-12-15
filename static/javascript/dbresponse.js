// On Load functions (mostly for error handling)
function handlePOSTError(errorCode) {
    console.log("Handling error.");
    var error_element = d3.select('#error-element');
    if (errorCode == 1) {
        // Unfilled/Invalid Field - likely due to unintended page manipulation
        console.log('Unfilled/Invalid Field - likely due to unintended page manipulation');
        error_element.style("display", "block");
        d3.select("#error-text").text("An error occurred, please try again.");
    } else if (errorCode == 2) {
        // Duplicate Entry
        console.log('Duplicate Entry');
        error_element.style("display", "block");
        d3.select("#error-text").text("Duplicate entry found, you have been redirected to the existing entry.");
        $(`#v-pills-tab a[href="${window.location.hash}"]`).tab('show');
    } else if (errorCode == 2) {
        // Prohibited Entry Type
        console.log('Prohibited Entry Type');
        error_element.style("display", "block");
        d3.select("#error-text").text("Prohibited Entry Type: Areas may only contain sub-areas OR boulders and routes.");
    }
}

window.onload = function() {
    console.log('Running OnLoad');
    // Check session storage
    var error = sessionStorage.getItem("error");
    if (error) {
        console.log('Error Detected');
        sessionStorage.removeItem("error");
        handlePOSTError(sessionStorage.getItem("errorCode"));
        sessionStorage.removeItem("errorCode");
    }
    // Check intra-page href and redirect
    var url = document.location.toString();
    if (url.match('#')) {
        $('a[href="#' + url.split('#')[1] + '"]').tab('show');
    }
};


// Validate Form
// Disable form submissions if there are invalid fields
function validateForms() {
    var valid = true;
    // Get the forms we want to add validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
    if (form.checkValidity() === false) {
        // Unfilled/invalid field found, flip boolean to prevent form submission
        valid = false;
        console.log('Invalid form submission.');
    }
    form.classList.add('was-validated');
    }, false);
    
    // After loop, if form is still valid, submit
    if (valid) submit_data(); 
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
            // Action Tree
            // 1. Valid submission - redirect to new page
            // 2. Invalid Fields submitted - refresh with error message
            // 3. Duplicate Entry submitted - redirect to existing entry
            if (data.redirect) {
                if (data.error) {
                    sessionStorage.setItem("error", "true");
                    sessionStorage.setItem("errorCode", data.error);
                }
                window.location.href = data.redirect;
            }
            
        })
        .catch(error => console.log(error));

}

function submit_data() {
    call_API(get_inputs());
}

var entry_form_submit = d3.select('#entry-form-submit');
entry_form_submit.on('click', validateForms);
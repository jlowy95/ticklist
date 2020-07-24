// On Load functions (mostly for error handling)
function handlePOSTError(errorCode) {
    var error_element = d3.select('#error-popup');
    if (errorCode == 0) {
        // Unfilled/Invalid Field - likely due to unintended page manipulation
        console.log('Unfilled/Invalid Field - likely due to unintended page manipulation');
        error_element.style("display: block;");
        error_element.text("An error occurred, please try again.");
    } else if (errorCode == 1) {
        // Duplicate Entry
        console.log('Duplicate Entry');
        error_element.style("display: block;");
        error_element.text("Duplicate entry found, you have been redirected to the existing entry.");
    }
}

window.onload = function() {
    var error = sessionStorage.getItem("error");
    if (error) {
        sessionStorage.removeItem("error");
        handlePOSTError(sessionStorage.getItem("errorCode"));
        sessionStorage.removeItem("errorCode");
    }
};


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

var area_form_submit = d3.select('#area-form-submit');
area_form_submit.on('click', validateForms);
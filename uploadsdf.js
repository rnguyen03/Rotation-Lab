/* javascript to accompany upload-sdf.html */
$(document).ready(function() {
    var submission = $('#message'); // get the molecule-list container
    var loading = $('<p>Loading...</p>')
    var success = $('<p>Submission Successful</p>')
    var repeating = $('<p>Molecule Already Exists...</p>')
    var invalid = $('<p>Submission Error</p>')
    $('#submit_sdf').on('click', function(e) {
        e.preventDefault();
        submission.empty()
        submission.append(loading);
        var molName = $('#mol-name').val().trim();
        var sdfFile = $('#sdf-file')[0].files[0];
        var regex = /^[a-zA-Z0-9_\-]+$/;
        if (!molName.match(regex)) {
            alert('Invalid molecule name');
            return;
        }
        var formData = new FormData();
        formData.append('mol-name', molName);
        formData.append('sdf-file', sdfFile);
        $.ajax({
            url: 'upload-sdf.html',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                submission.empty()
                submission.append(success)
                console.log("Element added");
            },
            error: function(xhr, status, error) {
                submission.empty()
                if (xhr.status === 400) {
                    submission.append(invalid)
                } else if (xhr.status === 406){
                    submission.append(repeating)
                } else {
                    submission.append(invalid)
                    alert("Error: " + error);
                }
            }
        });
    });
});
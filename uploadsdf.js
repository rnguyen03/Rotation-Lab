/* javascript to accompany upload-sdf.html */
$(document).ready(function() {
    $('#submit_sdf').on('click', function(e) {
        e.preventDefault();
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
                console.log("Element added");
            },
            error: function(xhr, status, error) {
                if (xhr.status === 400) {
                    alert("Submission Invalid.");
                } else {
                    alert("Error: " + error);
                }
                console.log(xhr.responseText);
            }
        });
    });
});
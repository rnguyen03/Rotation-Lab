$(document).ready(function () {
    getSDF(0);

    $("#rotate-x").click(function() {
        requestRotation("x");
        getSDF(1);
    });
    
    $("#rotate-y").click(function() {
        requestRotation("y");
        getSDF(1);
    });
    
    $("#rotate-z").click(function() {
        requestRotation("z");
        getSDF(1);
    });
});

function requestRotation(axis) {
    $.ajax({
        url: '/angle', // the URL to your Flask route that processes the molecule
        type: 'POST',
        data: {'axis': axis},
        success: function (response) {
            console.log("Rotation made");
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr.status);
            console.log(errorThrown);
        }
    });
}

function getSDF(count, atoms) {
    $.ajax({
        url: "/svg",
        type: "GET",
        dataType: "text",
        success: function(data, status, xhr) {
            var displayBox = $('#display-box');
            displayBox.empty();
            if (xhr.status === 204) {
                console.log("No Selection")
                var emptyBar = $('<div class="empty-bar"></div>').text("Click here to navigate to Molecules to select a molecule!");
                emptyBar.on('click', function() {
                    window.location.href = 'molecules.html';
                });
                displayBox.append(emptyBar);
            }
            else {                
                displayBox.append(data);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}
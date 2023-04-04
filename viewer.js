$(document).ready(function () {
    getSDF();

    $("#rotate-x").click(function() {
        requestRotation("x");
        getSDF();
    });
    
    $("#rotate-y").click(function() {
        requestRotation("y");
        getSDF();
    });
    
    $("#rotate-z").click(function() {
        requestRotation("z");
        getSDF();
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

function getSDF(){
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
                data = data.replace('width="1000"', 'width="500"');
                data = data.replace('height="1000"', 'height="400"');
                data = data.replace('<svg ', '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" ');
                displayBox.append(data);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}
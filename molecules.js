/* javascript to accompany molecules.html */
$(document).ready(function () {
    $.ajax({
        url: '/get-molecules', // the URL to your Flask route that returns the molecules
        type: 'GET',
        dataType: 'json', 
        success: function (data, status, xhr) {
            if (xhr.status === 204) {
                console.log("Database Empty")
                var moleculeList = $('#molecule-list');
                var emptyBar = $('<div class="empty-bar"></div>').text("No Molecules. Upload an SDF");
                moleculeList.append(emptyBar);
            }
            else {
                var molecules = data; // convert the response to a JavaScript object
                var moleculeList = $('#molecule-list'); // get the molecule-list container
                moleculeList.empty();
                console.log("SUCEEDED");
                // loop through the molecules and add them to the moleculeList container
                for (var i = 0; i < molecules.length; i++) {
                    var molecule = molecules[i];

                    // create a new molecule bar element
                    var moleculeBar = $('<div class="molecule-bar"></div>');

                    // set the molecule name as the bar's text
                    moleculeBar.append($('<span class="molecule-name"></span>').text(molecule.name));

                    // wrap the atom and bond counts in a separate container
                    var moleculeInfo = $('<div class="molecule-info"></div>');
                    moleculeInfo.append($('<span class="molecule-atoms"></span>').text('Atoms: ' + molecule.atom_count));
                    moleculeInfo.append($('<span class="molecule-bonds"></span>').text('Bonds: ' + molecule.bond_count));
                    moleculeBar.append(moleculeInfo);

                    // add a click event to the moleculeBar element that calls the processMolecule function with the molecule name
                    moleculeBar.on('click', function () {
                        var moleculeName = $(this).find('.molecule-name').text();
                        processMolecule(moleculeName);
                    });

                    // add the moleculeBar element to the page
                    moleculeList.append(moleculeBar);
                }
            }
        },
        error: function(xhr, textStatus, errorThrown){
            console.log(xhr.status);
            console.log(errorThrown);
        }
    });
    function processMolecule(moleculeName) {
        $.ajax({
          url: '/view-molecule', // the URL to your Flask route that processes the molecule
          type: 'POST',
          data: {'moleculeName': moleculeName},
          success: function (response) {
            console.log(response);
            window.location.href = '/viewer.html'; // redirect to viewer.html
          },
          error: function (xhr, textStatus, errorThrown) {
            console.log(xhr.status);
            console.log(errorThrown);
          }
        });
    }
});
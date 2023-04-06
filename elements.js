/* javascript to accompany elements.html */
$(document).ready(function () {
	var submission = $('#message'); // get the molecule-list container
	var submission2 = $('#message2');
    var loading = $('<p>Loading...</p>')
    var success = $('<p>Submission Successful</p>')
    var repeating = $('<p>Molecule Already Exists...</p>')
    var invalid = $('<p>Submission Error</p>')
	
	$("#add_element").click(function () {
		$("#hidden_button").val("add_element");
	});
	$("#remove_element").click(function () {
		$("#hidden_button").val("remove_element");
	});
	$("form").submit(function (event) {
		event.preventDefault();
		submission.empty();
		submission2.empty();
		var buttonClicked = $("#hidden_button").val();
		if (buttonClicked === "add_element") {
			submission.append(loading);
			// add element was clicked
			$.post("/elements.html", {
				/* pass a JavaScript dictionary */
				operation: "add",
				eNumber: $("#element_number").val(),
				eCode: $("#element_code").val(),
				eName: $("#element_name").val(),
				col1: $("#color1").val(),
				col2: $("#color2").val(),
				col3: $("#color3").val(),
				rad: $("#radius").val()
			}).done(function (data) {
				submission.empty();
                submission.append(success)
				console.log(data);
			}).fail(function (xhr, status, error) {
				console.log(status)
				submission.empty();
                submission.append(invalid)
			});
		} else if (buttonClicked === "remove_element") {
			submission2.append(loading);
			// remove element was clicked
			$.post("/elements.html", {
				/* pass a JavaScript dictionary */
				operation: "remove",
				reName: $("#remove_element_name").val(),
			}).done(function (data) {
				submission2.empty();
                submission2.append(success)
			}).fail(function (xhr, status, error) {
				submission2.empty();
                submission2.append(invalid)
			});
		}
	});

});

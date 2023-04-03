/* javascript to accompany elements.html */
$(document).ready(function () {
	$("#add_element").click(function () {
		$("#hidden_button").val("add_element");
	});
	$("#remove_element").click(function () {
		$("#hidden_button").val("remove_element");
	});
	$("form").submit(function (event) {
		event.preventDefault();
		var buttonClicked = $("#hidden_button").val();
		if (buttonClicked === "add_element") {
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
				console.log(data);
				alert("Submission succeeded!");
			}).fail(function (xhr, status, error) {
				console.log(xhr)
				alert("Submission failed!");
			});
		} else if (buttonClicked === "remove_element") {
			// remove element was clicked
			$.post("/elements.html", {
				/* pass a JavaScript dictionary */
				operation: "remove",
				reName: $("#remove_element_name").val(),
			}).done(function (data) {
				alert("Submission succeeded!");
			}).fail(function (xhr, status, error) {
				console.log(xhr)
				alert("Submission failed!");
			});
		}
	});

});

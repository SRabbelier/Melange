$(document).ready(function() {
	$("#applications_progress_bar").progressBar({showText: false});
});

function acceptOrgInit() {
	$("#acceptance_text").fadeOut("slow",
		function() {
			$("#applications_progress_bar").fadeIn("slow");
		}
	);
	$.getJSON("{{ bulk_accept_link|safe }}",
		function(data){
			setTimeout(function(){acceptOrg(data)}, 0);
		}
	);
}

function acceptOrg(accepted_applications) {
	var application_index = 0, max_applications=accepted_applications.applications.length;
	for (application_index; application_index<max_applications; application_index++) {
		// regular expression to find a valid scope path inside matching parenthesis
		var re = /\((\w*)\)/;
		var scope_path = accepted_applications.link.match(re)[1];
		// the URL is obtained by using the scope path found in the matching parenthesis
		var url_to_call = accepted_applications.link.replace(re,eval("accepted_applications.applications[application_index]."+scope_path));
		// now we can call the URL found
		$.ajax({
			async: false,
			url: url_to_call,
			timeout: 10000,
			complete: function(data) {
				if (data) {
					// update progress bar percentage and description
					var percentage = Math.floor(100 * (application_index+1) / (accepted_applications.nr_applications));
					$("#description_progressbar").html(" Processed application "+accepted_applications.applications[application_index].name+" ("+(application_index+1)+"/"+accepted_applications.nr_applications+")");
					$("#applications_progress_bar").progressBar(percentage);
				}
			}
		});
	}
	// tell the user we are done
	$("#description_done").html(" <strong>Done!</strong>");

}


var duplicateSlots = new function() {
  // this variable will contain all the org details, and filled
  // incrementally
  var orgs_details = {};
  // this variable will contain all student/proposal data details,
  // filled incrementally
  var assigned_proposals = new Array();

  // public function to begin iterating load of JSONs and then call printing
  // of duplicates

  this.showDuplicatesInit = function() {

    // Remember this object for Javascript scoping
    html_string = '';
    var this_object = this;
    var NUMBER_OF_ORGS = number_of_orgs;
    var OFFSET_LENGTH = offset_length;
    // Variables to handle progress bar updating
    var ITERATIONS = (number_of_orgs % offset_length)==0 ? Math.floor(number_of_orgs/offset_length) : Math.floor(number_of_orgs/offset_length)+1;
    var successful_calls = 0;

    $("#id_button_duplicate_slots").fadeOut("slow",
      function() {
        $("#duplicates_progress_bar").progressBar(0);
        $("#description_done").html("");
        // For every ajax success, bind this function to update user feedback
        $(this).bind("ajaxSuccess", function() {
          successful_calls++;
          var percentage = Math.floor(100 * (successful_calls) / (ITERATIONS));
          $("#duplicates_progress_bar").progressBar(percentage);
          $("#description_progressbar").html(" Processed orgs chunk " + (successful_calls) + "/" + ITERATIONS);
          // If this is the last call, feedback the user and print the duplicates data
          if (successful_calls==ITERATIONS) {
            $("#applications_progress_bar").fadeOut("slow",
              function() {
                $("#duplicates_progress_bar").progressBar(0);
                $("#id_button_duplicate_slots").fadeIn("slow");
              }
            );
            $("#description_progressbar").html("");
            $("#description_done").html("<strong> Done!</strong>");
            $("#duplicates_progress_bar").fadeOut("slow",
              function() {
                $("#id_button_duplicate_slots").val("Recalculate").fadeIn("slow",
                  function() {
                    // Call printing to HTML function with correct scope
                    printDuplicatesAndSendJSON.call(this_object);
                  }
                );
              }
            );
          }
        });
        // Call the showDuplicates function for the first time with correct scope
        $("#duplicates_progress_bar").fadeIn("slow", showDuplicates.apply(this_object,[url_to_query,OFFSET_LENGTH,NUMBER_OF_ORGS]));
      }
    );
  }

  function showDuplicates(url_to_query,OFFSET_LENGTH,NUMBER_OF_ORGS) {
    var current_offset = 0;
    orgs_details = {};
    assigned_proposals = new Array();

    // Here Ajax call is handled
    setTimeout(function() {
      $.ajax({
        cache:false,
        mode: "sync",
        type: "GET",
        timeout: 1000000,
        dataType: "json",
        url: "/program/assigned_proposals/"+url_to_query+"?limit="+OFFSET_LENGTH+"&offset="+current_offset,
        success: function (data, textStatus) {
          if (data) {
            // Load JSON data
            loadSingleJSONData(data);
          }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
          // if there is an error return the button and leave a try again message
          if (XMLHttpRequest!=undefined) {
            $("#id_button_duplicate_slots").fadeIn("slow", function() {
	      $("#description_done").html("<strong class='error'> Error encountered, try again</strong>");
            });
          }
       }
      });
      current_offset+=OFFSET_LENGTH;
      if (current_offset<NUMBER_OF_ORGS) {
        setTimeout(arguments.callee,1);
      }
    },1);
    // This prevent page reloading after each ajax call
    return false;
  }

  // private function to load a JSON and pushing the data to the
  // private global variables
  function loadSingleJSONData(data) {
    if (data) {
      // pushing org details
      for (var org_key in data.data.orgs) {
        orgs_details[org_key] = data.data.orgs[org_key];
      }
      // pushing proposals
      $(data.data.proposals).each(
        function(intIndex, proposal) {
          // if this student_key is not yet present
          if (assigned_proposals[proposal.student_key]==undefined) {
            // create the object and insert general info
            assigned_proposals[proposal.student_key] = {};
            assigned_proposals[proposal.student_key].name = proposal.student_name;
            assigned_proposals[proposal.student_key].contact = proposal.student_contact;
            assigned_proposals[proposal.student_key].proposals = new Array();
          }
          // anyway, push the accepted proposals
          assigned_proposals[proposal.student_key].proposals.push(
            {
              "org_key" : proposal.org_key,
              "proposal_key" : proposal.key_name,
              "proposal_title": proposal.proposal_title
            }
          );
        }
      );
    }
  }

  // private function to generate the JSON to send for caching and calling
  // the actual function that will print the data
  function printDuplicatesAndSendJSON() {
    // JSON skeleton that need to be sent to the server
    var to_json = {
      "data": {
        "orgs" : orgs_details,
        "students": {}
      }
    }
    // for every student...
    for (var student_key in assigned_proposals) {
      var accepted_proposals = assigned_proposals[student_key].proposals.length;
      // if accepted proposal are less than 2, then ignore and continue the iteration
      if (accepted_proposals<2) continue;
      var student = assigned_proposals[student_key];
      // push this student to the caching JSON
      to_json.data.students[student_key] = student;
      var proposals = student.proposals;
      // call the function that prints the output html
      this.showDuplicatesHtml(orgs_details,student,student_key,proposals);
    }
    if (html_string=="") {
      $("#div_duplicate_slots").html("<strong>No duplicate slots found</strong>");
    }
    // at the end, send the JSON for caching purposes
    $.ajax({
      url: location.href,
      type: 'POST',
      processData: true,
      data: {result: JSON.stringify(to_json)},
      contentType: 'application/json',
      dataType: 'json',
    });
  }

  // public function to output actual HTML out of the data (cached or not)
  this.showDuplicatesHtml = function(orgs_details,student,student_key,proposals) {
    if (html_string == '') {
      $("#div_duplicate_slots").html('');
      html_string='<ul>';
    }
    html_string+= '<li>Student: <strong><a href="/student/show/'+student_key+'">'+student.name+'</a></strong> (<a href="mailto:'+student.contact+'">'+student.contact+'</a>)';
    html_string+='<ul>';
    $(proposals).each(
      function (intIndex, proposal) {
        html_string+='<li>Organization: <a href="/org/show/'+proposal.org_key+'">'+orgs_details[proposal.org_key].name+'</a>, admin: '+orgs_details[proposal.org_key].admin_name+' (<a href="mailto:'+orgs_details[proposal.org_key].admin_email+'">'+orgs_details[proposal.org_key].admin_email+'</a>)</li>';
        html_string+='<ul><li>Proposal: <a href="/student_proposal/show/'+proposal.proposal_key+'">'+proposal.proposal_title+'</a></li></ul>';
      }
    );
    html_string+='</ul></li>';
    html_string+='</ul>';
    $("#div_duplicate_slots").html(html_string);
  }
}

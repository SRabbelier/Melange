(function () {
  var duplicateSlots = window.duplicateSlots = function () {
  };
  // this variable will contain all the org details, and filled
  // incrementally
  var orgs_details = {};
  // this variable will contain all student/proposal data details,
  // filled incrementally
  var assigned_proposals = [];

  // public function to output actual HTML out of the data (cached or not)
  duplicateSlots.showDuplicatesHtml =
    function (orgs_details, student, student_key, proposals) {
      /*jslint undef:false */
      if (html_string === '') {
        jQuery("#div_duplicate_slots").html('');
        html_string = '<ul>';
      }
      html_string += [
        '<li>',
        '  Student: ',
        '    <strong>',
        '      <a href="/student/show/', student_key, '">', student.name,
        '</a>',
        '    </strong> ',
        '(<a href="mailto:', student.contact, '">', student.contact, '</a>)'
      ].join("");
      html_string += '<ul>';
      jQuery(proposals).each(
        function (intIndex, proposal) {
          html_string += [
            '<li>',
            '  Organization: ',
            '    <a href="/org/show/', proposal.org_key, '">',
            orgs_details[proposal.org_key].name,
            '</a>, admin: ', orgs_details[proposal.org_key].admin_name,
            ' (<a href="mailto:',
            orgs_details[proposal.org_key].admin_email,
            '">',
            orgs_details[proposal.org_key].admin_email, '</a>)</li>'
          ].join("");
          html_string += [
            '<ul>',
            '  <li>',
            'Proposal: ',
            '<a href="/student_proposal/show/', proposal.proposal_key, '">',
            proposal.proposal_title, '</a>',
            '  </li>',
            '</ul>'
          ].join("");
        }
      );
      html_string += '</ul></li>';
      html_string += '</ul>';
      jQuery("#div_duplicate_slots").html(html_string);
      /*jslint undef:true */
    };

  // private function to generate the JSON to send for caching and calling
  // the actual function that will print the data
  function printDuplicatesAndSendJSON() {
    // JSON skeleton that need to be sent to the server
    var to_json = {
      "data": {
        "orgs" : orgs_details,
        "students": {}
      }
    };
    // for every student...
    jQuery.each(assigned_proposals, function (student_key, student) {
      var accepted_proposals = student.proposals.length;
      // if accepted proposal are less than 2, then ignore and
      // continue the iteration
      if (accepted_proposals < 2) {
        return true;
      }
      // push this student to the caching JSON
      to_json.data.students[student_key] = student;
      var proposals = student.proposals;
      // call the function that prints the output html
      duplicateSlots.showDuplicatesHtml(
        orgs_details, student, student_key, proposals
      );
    });
    /*jslint undef:false */
    if (html_string === "") {
    /*jslint undef:true */
      jQuery("#div_duplicate_slots")
        .html("<strong>No duplicate slots found</strong>");
    }
    // at the end, send the JSON for caching purposes
    jQuery.ajax({
      url: location.href,
      type: 'POST',
      processData: true,
      data: {result: JSON.stringify(to_json)},
      contentType: 'application/json',
      dataType: 'json'
    });
  }

  // private function to load a JSON and pushing the data to the
  // private global variables
  function loadSingleJSONData(data) {
    if (data) {
      // pushing org details
      jQuery.each(data.data.orgs, function (org_key, organization) {
        orgs_details[org_key] = organization;
      });
      // pushing proposals
      jQuery(data.data.proposals).each(
        function (intIndex, proposal) {
          // if this student_key is not yet present
          if (assigned_proposals[proposal.student_key] === undefined) {
            // create the object and insert general info
            assigned_proposals[proposal.student_key] = {};
            assigned_proposals[proposal.student_key].name =
              proposal.student_name;
            assigned_proposals[proposal.student_key].contact =
              proposal.student_contact;
            assigned_proposals[proposal.student_key].proposals = [];
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

  function showDuplicates(url_to_query, OFFSET_LENGTH, NUMBER_OF_ORGS) {
    var current_offset = 0;
    orgs_details = {};
    assigned_proposals = [];

    // Here Ajax call is handled
    setTimeout(
      function () {
        jQuery.ajax({
          cache: false,
          mode: "sync",
          type: "GET",
          timeout: 1000000,
          dataType: "json",
          url: [
            "/program/assigned_proposals/", url_to_query,
            "?limit=", OFFSET_LENGTH,
            "&offset=", current_offset
          ].join(""),
          success: function (data, textStatus) {
            if (data) {
              // Load JSON data
              loadSingleJSONData(data);
            }
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            // if there is an error return the button and
            // leave a try again message
            if (XMLHttpRequest !== undefined) {
              jQuery("#id_button_duplicate_slots").fadeIn("slow",
                function () {
                  jQuery("#description_done").html([
                    "<strong class='error'> ",
                    "Error encountered, try again",
                    "</strong>"
                  ].join(""));
                }
              );
            }
          }
        });
        current_offset += OFFSET_LENGTH;
        if (current_offset < NUMBER_OF_ORGS) {
          setTimeout(arguments.callee, 1);
        }
      },
      1
    );
    // This prevent page reloading after each ajax call
    return false;
  }

  // public function to begin iterating load of JSONs and then call printing
  // of duplicates

  duplicateSlots.showDuplicatesInit = function () {
    /*jslint undef:false */
    html_string = '';
    // Remember this object for Javascript scoping
    var this_object = this;
    var NUMBER_OF_ORGS = number_of_orgs;
    var OFFSET_LENGTH = offset_length;
    // Variables to handle progress bar updating
    var ITERATIONS = (number_of_orgs % offset_length) === 0 ?
      Math.floor(number_of_orgs / offset_length) :
      Math.floor(number_of_orgs / offset_length) + 1;
    /*jslint undef:true */

    if (ITERATIONS === 0) {
      jQuery("#div_duplicate_slots")
        .html("<strong>No org slots to process</strong>");
      return;
    }

    var successful_calls = 0;

    jQuery("#id_button_duplicate_slots").fadeOut("slow",
      function () {
        jQuery("#duplicates_progress_bar").progressBar(0);
        jQuery("#description_done").html("");
        // For every ajax success, bind this function to update user feedback
        jQuery(this).bind("ajaxSuccess", function () {
          successful_calls++;
          var percentage = Math.floor(100 * (successful_calls) / (ITERATIONS));
          jQuery("#duplicates_progress_bar").progressBar(percentage);
          jQuery("#description_progressbar").html([
            " Processed orgs chunk ", successful_calls, "/", ITERATIONS
          ].join(""));
          // If this is the last call, feedback the user and
          // print the duplicates data
          if (successful_calls === ITERATIONS) {
            jQuery("#applications_progress_bar").fadeOut("slow",
              function () {
                jQuery("#duplicates_progress_bar").progressBar(0);
                jQuery("#id_button_duplicate_slots").fadeIn("slow");
              }
            );
            jQuery("#description_progressbar").html("");
            jQuery("#description_done").html("<strong> Done!</strong>");
            jQuery("#duplicates_progress_bar").fadeOut("slow",
              function () {
                jQuery("#id_button_duplicate_slots").val("Recalculate").fadeIn(
                  "slow",
                  function () {
                    // Call printing to HTML function with correct scope
                    printDuplicatesAndSendJSON.call(this_object);
                  }
                );
              }
            );
          }
        });
        // Call the showDuplicates function for the first time
        // with correct scope
        jQuery("#duplicates_progress_bar").fadeIn(
          "slow",
          showDuplicates.apply(
            this_object,
            /*jslint undef:false */
            [url_to_query, OFFSET_LENGTH, NUMBER_OF_ORGS]
            /*jslint undef:true */
          )
        );
      }
    );
  };
}());
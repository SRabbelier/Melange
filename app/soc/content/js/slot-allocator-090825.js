var current_allocated_slots = 0;
var current_slots = {};
var tooltip = [
  "<div class='tooltip'>",
  "<div class='tooltip-body'>",
  "<img src='/soc/content/images/purrInfo.png' alt='' />",
  "<h3>Slots</h3>",
  "<p id='p_assigned_slots'></p>",
  "<p id='p_remaining_slots'></p>",
  "<p id='p_total_slots'></p></div>",
  "<div class='tooltip-bottom'></div>",
  "</div>"
].join('');

jQuery.postJSON = function (post_url, to_json, callback) {
  jQuery.ajax({
    url: post_url,
    type: 'POST',
    processData: true,
    data: {result: JSON.stringify(to_json)},
    contentType: 'application/json',
    dataType: 'json',
    success: callback
  });
};

function updateCurrentSlots() {
  current_allocated_slots = 0;
  jQuery.each(current_slots, function (org_id, org_details) {
    current_allocated_slots =
      current_allocated_slots + Number(org_details.slots);
  });
}

function updateOverlay() {
  updateCurrentSlots();
  var remaining_slots = window.MAX_AVAILABLE_SLOTS - current_allocated_slots;
  jQuery("#p_assigned_slots")
    .html("<strong>Assigned slots:</strong> " + current_allocated_slots);
  jQuery("#p_remaining_slots")
    .html("<strong>Remaining slots:</strong> " + remaining_slots);
}

function updateFromJSON(data) {
  if (data) {
    jQuery(data.data).each(
      function (intIndex, item) {
        jQuery("#id_spin_slot_count_" + item.link_id).val(item.slots);
        current_slots[item.link_id] = {
          slots: item.slots,
          locked: item.locked,
          adjustment: item.adjustment
        };
        jQuery("#id_locked_slot_" + item.link_id)
          .attr("checked", item.locked);
        jQuery("#id_spin_adjustment_count_" + item.link_id)
          .val(item.adjustment);
      }
    );
    updateOverlay();
  }
}

function retrieveJSON() {
  jQuery.getJSON(
    window.RETURN_URL + "?_=" + (new Date().getTime()),
    function (data) {
      if (data) {
        updateFromJSON(data);
      }
    }
  );
}

function reCalculate() {
  var url = window.RETURN_URL + "?_=" + (new Date().getTime());
  jQuery.postJSON(url, current_slots, updateFromJSON);
}

function submit() {
  var url = window.RETURN_URL + "?submit=1&_=" + (new Date().getTime());
  jQuery.postJSON(url, current_slots, updateFromJSON);
}

function load() {
  var url = window.RETURN_URL + "?load=1&_=" + (new Date().getTime());
  jQuery.postJSON(url, current_slots, updateFromJSON);
}

function lockSlots(checkbox) {
  var locked = jQuery(checkbox).attr("checked");
  var re = /^id_locked_slot_(\w*)/;
  var org_link_id = checkbox.id.match(re)[1];
  current_slots[org_link_id].locked = locked;
}

function assignSlots(counter) {
  var re = /^id_spin_slot_count_(\w*)/;
  var org_link_id = counter.id.match(re)[1];
  current_slots[org_link_id].slots = jQuery(counter).val();
  updateCurrentSlots();
  updateOverlay();
}

function assignAdjustment(counter) {
  var re = /^id_spin_adjustment_count_(\w*)/;
  var org_link_id = counter.id.match(re)[1];
  current_slots[org_link_id].adjustment = jQuery(counter).val();
}


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
  "</div>",
  ].join('');

$.postJSON = function (post_url, to_json, callback) {
    $.ajax({
        url: post_url,
        type: 'POST',
        processData: true,
        data: {result: JSON.stringify(to_json)},
        contentType: 'application/json',
        dataType: 'json',
        success: callback,
    });
};

function updateFromJSON(data) {
  if (data) {
    $(data.data).each(
      function (intIndex,item) {
        $("#id_spin_slot_count_"+item.link_id).val(item.slots);
        current_slots[item.link_id] = {slots: item.slots, locked: item.locked, adjustment: item.adjustment};
        $("#id_locked_slot_"+item.link_id).attr("checked",item.locked);
        $("#id_spin_adjustment_count_"+item.link_id).val(item.adjustment);
      }
    );
    updateOverlay();
  }
}

function retrieveJSON() {
  $.getJSON("http://localhost:8080/program/slots/google/gsoc2009?_="+(new Date().getTime()),
    updateFromJSON
  );
}

function reCalculate() {
  url = "http://localhost:8080/program/slots/google/gsoc2009?_="+(new Date().getTime())
   $.postJSON(url, current_slots, updateFromJSON);
}

function updateOverlay() {
  updateCurrentSlots();
  var remaining_slots = MAX_AVAILABLE_SLOTS - current_allocated_slots;
  $("#p_assigned_slots").html("<strong>Assigned slots:</strong> "+current_allocated_slots);
  $("#p_remaining_slots").html("<strong>Remaining slots:</strong> "+remaining_slots);
}

function updateCurrentSlots() {
  current_allocated_slots = 0;
  for (var org_id in current_slots) {
    current_allocated_slots = current_allocated_slots+new Number(current_slots[org_id].slots);
  }
}

function lockSlots (checkbox) {
  var locked = $(checkbox).attr("checked");
  var re = /^id_locked_slot_(\w*)/;
  var org_link_id = checkbox.id.match(re)[1];
  current_slots[org_link_id].locked = locked;
}

function assignSlots (counter) {
  var re = /^id_spin_slot_count_(\w*)/;
  var org_link_id = counter.id.match(re)[1];
  current_slots[org_link_id].slots = $(counter).val();
  updateCurrentSlots();
  updateOverlay();
}

function assignAdjustment (counter) {
  var re = /^id_spin_adjustment_count_(\w*)/;
  var org_link_id = counter.id.match(re)[1];
  current_slots[org_link_id].adjustment = $(counter).val();
}


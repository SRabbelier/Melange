/* Copyright 2010 the Melange authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * @author <a href="mailto:fadinlight@gmail.com">Mario Ferraro</a>
 */

(function () {
  var melange = window.melange;
  this.prototype = new melange.templates._baseTemplate();
  this.prototype.constructor = melange.templates._baseTemplate;
  melange.templates._baseTemplate.apply(this, arguments);

  var _self = this;

  var MAX_AVAILABLE_SLOTS = _self.context.total_slots;
  var RETURN_URL = _self.context.return_url;

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

  var list;

  jQuery(function() {
    jQuery(document).bind("melange_list_loaded", function (event) {
      list = event.list_object;
      var locked_colModel = "locked";
      var slots_colModel = "slots_ass";
      var linkid_colModel = "link_id";

      var rows = list.jqgrid.object.jqGrid('getRowData');
      jQuery.each(rows, function (row_id,row_data) {
        var org_link_id = row_data[linkid_colModel];

        list.jqgrid.object.jqGrid(
          'setCell',
          (row_id + 1),
          slots_colModel,
          '<div class="slots" id="id_slot_count_container_'+org_link_id+'"><input type="text" id="id_spin_slot_count_'+org_link_id+'" size="3" value="0"/></div>',
          null,
          null
        );

        jQuery("#id_spin_slot_count_"+org_link_id).bind("change", assignSlots);

        list.jqgrid.object.jqGrid(
          'setCell',
          (row_id + 1),
          locked_colModel,
          '<div class="locked" id="id_locked_slot_container_'+org_link_id+'"><input type="checkbox" id="id_locked_slot_'+org_link_id+'"/></div>',
          null,
          null
        );

        jQuery("#id_locked_slot_"+org_link_id).bind("change", lockSlots);
      });
      jQuery('[id^=id_spin_slot_count_]').spin({min:0, max:MAX_AVAILABLE_SLOTS});

      jQuery(tooltip).purr({usingTransparentPNG: true, isSticky: true});
      jQuery("#p_total_slots").html("<strong>Max slots:</strong> "+MAX_AVAILABLE_SLOTS);

      jQuery("#button_slot_allocation_recalculate").bind("click", reCalculate);
      jQuery("#button_slot_allocation_submit").bind("click", submitSlots);
      jQuery("#button_slot_allocation_load").bind("click", loadSlots);

      retrieveJSON();
    });
  });


  jQuery.postJSON = function (post_url, to_json, callback) {
    jQuery.ajax({
      url: post_url,
      type: 'POST',
      processData: true,
      data: {
        xsrf_token: window.xsrf_token,
        result: JSON.stringify(to_json)
      },
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
    var remaining_slots = MAX_AVAILABLE_SLOTS - current_allocated_slots;
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
          var list_row = jLinq.from(list.data.data).equals("link_id",item.link_id).select()[0];
          list_row.slots_ass = item.slots;
          list_row.locked = item.locked;
          current_slots[item.link_id] = {
            slots: item.slots,
            locked: item.locked
          };
          jQuery("#id_locked_slot_" + item.link_id)
            .attr("checked", item.locked);
        }
      );
      updateOverlay();
    }
    jQuery("[id^=button_slot_]").removeAttr('disabled');
  }

  function retrieveJSON() {
    jQuery.getJSON(
      RETURN_URL + "?_=" + (new Date().getTime()),
      function (data) {
        if (data) {
          updateFromJSON(data);
        }
      }
    );
  }

  function reCalculate() {
    jQuery("#button_slot_allocation_recalculate").attr('disabled', 'disabled');
    var url = RETURN_URL + "?_=" + (new Date().getTime());
    jQuery.postJSON(url, current_slots, updateFromJSON);
  }

  function submitSlots() {
    jQuery("#button_slot_allocation_submit").attr('disabled', 'disabled');
    var url = RETURN_URL + "?submit=1&_=" + (new Date().getTime());
    jQuery.postJSON(url, current_slots, updateFromJSON);
  }

  function loadSlots() {
    jQuery("#button_slot_allocation_load").attr('disabled', 'disabled');
    var url = RETURN_URL + "?load=1&_=" + (new Date().getTime());
    jQuery.postJSON(url, current_slots, updateFromJSON);
  }

  function lockSlots() {
    var checkbox = this;
    var locked = jQuery(checkbox).attr("checked");
    var re = /^id_locked_slot_(\w*)/;
    var org_link_id = checkbox.id.match(re)[1];
    current_slots[org_link_id].locked = locked;
    var list_row = jLinq.from(list.data.data).equals("link_id",org_link_id).select()[0];
    list_row.locked = locked;
  }

  function assignSlots() {
    var counter = this;
    var re = /^id_spin_slot_count_(\w*)/;
    var org_link_id = counter.id.match(re)[1];
    current_slots[org_link_id].slots = jQuery(counter).val();
    var list_row = jLinq.from(list.data.data).equals("link_id",org_link_id).select()[0];
    list_row.slots_ass = jQuery(counter).val();
    updateCurrentSlots();
    updateOverlay();
  }
}());

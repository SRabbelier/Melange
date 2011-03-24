/* Copyright 2009 the Melange authors.
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
  /** @lends melange.list */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  if (window.jLinq === undefined) {
    throw new Error("jLinq not loaded");
  }

  var jLinq = window.jLinq;

  /** Package that handles all lists related functions
    * @name melange.list
    * @namespace melange.list
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.list = window.melange.list = function () {
    return new melange.list();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.list);

  melange.error.createErrors([
    "listIndexNotValid",
    "divNotExistent",
    "indexAlreadyExistent"
  ]);

  var isEmptyObject = function (obj) {
    //from jQuery 1.4 source, we can switch to it when we will upgrade to 1.4
    for ( var name in obj ) {
      return false;
    }
    return true;
  }

  var retrieveData = function (postdata) {
    var my_index = postdata.my_index;
    var original_data = list_objects.get(my_index).data.data;
    var temp_data = original_data;
    var group_operation = "";
    var searches = {
      "eq": { // equals
        method: "equals",
        not: false
      },
      "ne": { // not equals
        method: "equals",
        not: true
      },
      "lt": { // less
        method: "less",
        not: false
      },
      "le": { // less or equal
        method: "lessEquals",
        not: false
      },
      "gt": { // greater
        method: "greater",
        not: false
      },
      "ge": { // greater or equal
        method: "greaterEquals",
        not: false
      },
      "bw": { // begins with
        method: "startsWith",
        not: false
      },
      "bn": { // does not begins with
        method: "startsWith",
        not: true
      },
      "ew": { // ends with
        method: "endsWith",
        not: false
      },
      "en": { // does not end with
        method: "endsWith",
        not: true
      },
      "cn": { // contains
        method: "contains",
        not: false
      },
      "nc": { // does not contain
        method: "contains",
        not: true
      },
      "in": {
        method: "match",
        not: false
      },
      "ni": {
        method: "match",
        not: true
      }
    };

    // Process search filter
    if (postdata._search && postdata.filters) {
      var filters = JSON.parse(postdata.filters);
      if (filters.rules[0].data !== "") {
        group_operation = filters.groupOp;
        if (group_operation === "OR") {
          temp_data = {};
        }
        jQuery.each(filters.rules, function (arr_index, filter) {
          if (filter.op === "in" || filter.op === "ni") {
            filter.data = filter.data.split(",").join("|");
          }
          if (searches[filter.op].not) {
            if (group_operation === "OR") {
              temp_data = jLinq.from(temp_data).union(jLinq.from(original_data).not()[searches[filter.op].method](filter.field, filter.data).select()).select();
            }
            else {
              temp_data = jLinq.from(temp_data).not()[searches[filter.op].method](filter.field, filter.data).select();
            }
          }
          else {
            if (group_operation === "OR") {
              temp_data = jLinq.from(temp_data).union(jLinq.from(original_data)[searches[filter.op].method](filter.field, filter.data).select()).select();
            }
            else {
              temp_data = jLinq.from(temp_data)[searches[filter.op].method](filter.field, filter.data).select();
            }
          }
        });
      }
    }
    // otherwise process simple filter
    else if (original_data[0] !== undefined) {
      jQuery.each(original_data[0], function (element_key, element_value) {
        if (postdata[element_key] !== undefined) {
          var search_by_reg_exp = jQuery("#regexp_" + list_objects.get(my_index).jqgrid.id).is(":checked");
          var select_filter = false;
          jQuery.each(list_objects.get(my_index).configuration.colModel, function (item_index, column) {
            if (column.editoptions !== undefined && element_key === column.name) {
              select_filter = true;
            }
          });
          // Search by regular expression if switch is on or if there is a select box to filter
          if (search_by_reg_exp || select_filter) {
            temp_data = jLinq.from(temp_data).match(element_key, postdata[element_key]).select();
          }
          // else search by simple text
          else {
            temp_data = jLinq.from(temp_data).contains(element_key, postdata[element_key]).select();
          }
        }
      });
    }
    // Process index/sorting filters
    var sort_column = postdata.sidx;
    var order_type = postdata.sord;

    // Do internal conversion if sort type is number
    jQuery.each(list_objects.get(my_index).configuration.colModel, function (column_index, column) {
      if (column.name === sort_column && (column.sorttype === "integer" || column.sorttype === "int")) {
        jQuery.each(temp_data, function (datum_index, datum) {
          var parsed_int = parseInt(datum[sort_column], 10);
          if (!isNaN(parsed_int)) {
            datum[sort_column] = parsed_int;
          }
        });
      }
    });

    if (order_type === "asc") {
      order_type = "";
    }
    else {
      order_type = "-";
    }

    if (temp_data.length > 0) {
      temp_data = jLinq.from(temp_data).ignoreCase().orderBy(order_type + sort_column).select();
    }
    list_objects.get(my_index).data.filtered_data = temp_data;

    // If pagination is disabled, change number or rows to length of filtered data
    if (postdata.rows === -1) {
      postdata.rows = list_objects.get(my_index).data.filtered_data.length;
    }

    var offset_start = (postdata.page - 1) * postdata.rows;
    var offset_end = (postdata.page * postdata.rows) - 1;

    var json_to_return = {
      "page": postdata.page,
      "total": temp_data.length === 0 ? 0 : Math.ceil(temp_data.length / postdata.rows),
      "records": temp_data.length,
      "rows": []
    };
    for (var i = offset_start; i <= offset_end; i++) {
      if (temp_data[i] === undefined) {
        continue;
      }
      var my_cell = [];
      if (original_data[0] !== undefined) {
          jQuery.each(list_objects.get(my_index).configuration.colModel, function (element_key, element_value) {
              var current_row;
              var search_into = list_objects.get(my_index).data.all_data;
              for (var row_index = 0; row_index < search_into.length; row_index++) {
                if (search_into[row_index].columns.key === temp_data[i]["key"]) {
                  current_row = search_into[row_index];
                  break;
                }
              }
            var column_content = temp_data[i][element_value.name];
            if (current_row.operations !== undefined && current_row.operations.row !== undefined && current_row.operations.row.link !== undefined) {
              // If there are no links in the text then insert a listsnoul link
              if (column_content !== null && column_content !== undefined && column_content.toString().match(/<a\b[^>]*>.*<\/a>/) === null) {
                column_content = '<a style="display:block;" href="' + current_row.operations.row.link + '" class="listsnoul">' + column_content + '</a>';
              }
            }
            my_cell.push(column_content);
          });
      }

      json_to_return.rows.push({
        "key": temp_data[i].key,
        "cell": my_cell
      });
    }

    var thegrid = jQuery("#" + list_objects.get(my_index).jqgrid.id)[0];
    thegrid.addJSONData(json_to_return);
  };

  var list_objects = (function () {
    var self = this;
    var lists = [];

    return {
      add: function (list_object) {
        lists[list_object.getIdx()] = list_object;
      },
      get: function (idx) {
        if (lists[idx] !== undefined) {
          return lists[idx];
        }
        else return null;
      },
      getAll: function () {
        return jQuery.extend({}, lists);
      },
      isExistent: function (idx) {
        if (lists[idx] !== undefined) {
          return true;
        }
        else return false;
      }
    };
  }());

  function List (div, idx, configuration, operations) {
    var _self = this;
    // Default options

    var default_jqgrid_options = {
      datatype: retrieveData,
      viewrecords: true
    };

    var default_pager_options = {
      edit: false,
      add: false,
      del: false,
      afterRefresh:
        function() {
          _self.refreshData();
          _self.jqgrid.object.trigger("reloadGrid");
        }
    };

    // Init data
    var div = div;
    var idx = idx;

    // Configuration (sent by protocol either by server or at init)
    this.configuration = configuration;
    this.operations = operations;

    // JQGrid related data
    this.jqgrid = {
      id: null,
      object: null,
      options: null,
      last_selected_row: null,
      editable_columns: [],
      dirty_fields: {},
      pager: {
        id: null,
        options: null
      }
    };

    // Data fetched from server
    this.data = {
      data: [],
      all_data: [],
      filtered_data: null
    };

    // Functions for jqGrid
    var jqgrid_functions = {
      //TODO (Mario): change the name of the functions to reflect the new editing feature
      enableDisableButtons: (function (list_object) {
        return function (row_id) {
          var option_name = list_object.jqgrid.object.jqGrid('getGridParam','multiselect') ? 'selarrrow' : 'selrow'
          var selected_ids = list_object.jqgrid.object.jqGrid('getGridParam',option_name);
          if (!selected_ids instanceof Array) {
            selected_ids = [selected_ids];
          }

          function updateDirtyField (row_id) {
            var row = jQuery("#" + list_object.jqgrid.id).jqGrid('getRowData', row_id);
            var original_data = jLinq.from(list_object.data.all_data).equals("columns.key",row.key).select()[0];
            if (list_object.jqgrid.dirty_fields[row.key] === undefined) {
              list_object.jqgrid.dirty_fields[row.key] = [];
            }
            var changed_columns = [];
            var not_changed_columns = [];
            jQuery.each(row, function (column_name, column_content) {
              /* Need to have a loose comparison here, as e.g. previously integer values
                 could be changed into strings by jqGrid
              */
              if (column_content != original_data.columns[column_name]) {
                changed_columns.push(column_name);
              } else {
                not_changed_columns.push(column_name);
              }
            });

            // Update dirty row with dirty columns
            jQuery.each(changed_columns, function (column_index, column_name) {
              if (jQuery.inArray(column_name, list_object.jqgrid.dirty_fields[row.key]) === -1) {
                list_object.jqgrid.dirty_fields[row.key].push(column_name);
              }
            });

            // Check if a previously dirty column has now the original value again
            jQuery.each(not_changed_columns, function (column_index, column_name) {
              var index_in_row_array = jQuery.inArray(column_name, list_object.jqgrid.dirty_fields[row.key]);
              if (index_in_row_array !== -1) {
                list_object.jqgrid.dirty_fields[row.key].splice(index_in_row_array, 1);
              }
            });

            // if deleting the not-anymore-dirty column has left the row array empty, then delete it
            if (list_object.jqgrid.dirty_fields[row.key].length === 0) {
              delete list_object.jqgrid.dirty_fields[row.key];
            }

            jQuery.each(list_object.operations.buttons, function (setting_index, operation) {
              if (operation.type === "post_edit") {
                var button_object = jQuery("#" + list_object.jqgrid.id + "_buttonOp_" + operation.id);
                // if this button is a post_edit button then disable or enable the button if dirty_fields apply
                if (isEmptyObject(list_object.jqgrid.dirty_fields)) {
                  button_object.attr("disabled","disabled");
                }
                else {
                  button_object.removeAttr("disabled");
                }
              }
            });

          }

          // Enable editing if set by backend
          // editable params for *_field_props available at http://www.trirand.com/jqgridwiki/doku.php?id=wiki:inline_editing
          if (selected_ids.length === 1) {
            if(row_id && row_id !== list_object.jqgrid.last_selected_row) {
              jQuery("#" + list_object.jqgrid.id).restoreRow(list_object.jqgrid.last_selected_row);
              jQuery("#" + list_object.jqgrid.id).jqGrid("editRow", row_id, true, null, null, 'clientArray', null, updateDirtyField);
              list_object.jqgrid.last_selected_row = row_id;
            }
          }

          jQuery.each(list_object.operations.buttons, function (setting_index, operation) {
            var button_object = jQuery("#" + list_object.jqgrid.id + "_buttonOp_" + operation.id);
            // if this button is not a post_edit button (which is already autoupdated during updates of dirty fields)
            if (operation.type !== "post_edit") {
              if (selected_ids.length >= operation.real_bounds[0] && selected_ids.length <= operation.real_bounds[1]) {
                button_object.removeAttr("disabled");
                // If this is a per-entity operation, substitute click event for button (if present)
                if (operation.real_bounds[0] === 1 && operation.real_bounds[1] === 1 && button_object.data('melange') !== undefined) {
                  // get current selection
                  var row = list_object.jqgrid.object.jqGrid('getRowData',selected_ids[0]);
                  var object = jLinq.from(list_object.data.all_data).equals("columns.key",row.key).select()[0];
                  var partial_click_method = button_object.data('melange').click;
                  button_object.click(partial_click_method(object.operations.buttons[operation.id].link));
                  button_object.attr("value",object.operations.buttons[operation.id].caption);
                }
              }
              else {
                button_object.attr("disabled","disabled");
              }
            }
          });
        }
      }(_self)),
      // function defines for global buttons
      global_button_functions : {
        redirect_simple : function (parameters) {
          if (parameters.new_window) {
            return function () {
              window.open(parameters.link);
            }
          }
          else {
            return function () {
              window.location.href = parameters.link;
            }
          }
        },
        redirect_custom: function (parameters) {
          return function (link) {
            if (parameters.new_window) {
              return function () {
                window.open(link);
              }
            }
            else {
              return function () {
                window.location.href = link;
              }
            }
          };
        },
        post: function (parameters) {
          return function () {
            var option_name = list_objects.get(parameters.idx).jqgrid.object.jqGrid('getGridParam','multiselect') ? 'selarrrow' : 'selrow'
            var selected_ids = list_objects.get(parameters.idx).jqgrid.object.jqGrid('getGridParam',option_name);
            if (!(selected_ids instanceof Array)) {
              if (selected_ids === null) {
                selected_ids = [];
              }
              else {
                selected_ids = [selected_ids];
              }
            }
            var objects_to_send = [];
            if (selected_ids.length < parameters.real_bounds[0] || selected_ids.length > parameters.real_bounds[1]) {
              return;
            }
            jQuery.each(selected_ids, function (id_index, id) {
              var row = jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).jqGrid('getRowData',id);
              var object = jLinq.from(list_objects.get(parameters.idx).all_data).equals("columns.key",row.key).select()[0];
              var single_object = {};
              jQuery.each(parameters.keys, function (key_index, column_name) {
                // If there was a surrounding link (with class listsnoul, so just link for rows)
                var field_text = row[column_name];
                if (jQuery(field_text).hasClass("listsnoul")) {
                  // strip the surrounding link from the text
                  var extracted_text = /^<a\b[^>]*>(.*?)<\/a>$/.exec(field_text);
                  field_text = extracted_text[1];
                }
                single_object[column_name] = field_text;
              });
              objects_to_send.push(single_object);
            });
            if (parameters.url === "") {
              parameters.url = window.location.href;
            }
            jQuery.post(
              parameters.url,
              {
                xsrf_token: window.xsrf_token,
                idx: parameters.idx,
                button_id: parameters.button_id,
                data: JSON.stringify(objects_to_send)
              },
              function (data) {
                if (parameters.redirect == "true") {
                  try {
                    var data_from_server = JSON.parse(data);
                    if (data_from_server.data.url !== undefined) {
                      window.location.href = data_from_server.data.url;
                    }
                  }
                  catch (e) {
                    //TODO (Mario): display an error message
                  }
                }
                var refresh_int = parseInt(parameters.refresh, 10);
                if (!isNaN(refresh_int)) {
                  list_objects.get(refresh_int).refreshData();
                  jQuery("#" + list_objects.get(refresh_int).jqgrid.id).trigger("reloadGrid");
                }
                if (parameters.refresh == "current") {
                  list_objects.get(parameters.idx).refreshData();
                  jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).trigger("reloadGrid");
                }
                else if (parameters.refresh == "all") {
                  var lists = list_objects.getAll();
                  jQuery.each(lists, function (list_index, list_object) {
                    list_object.refreshData();
                    jQuery("#" + list_objects.get(list_index).jqgrid.id).trigger("reloadGrid");
                  });
                }
              }
            )
          }
        },
        post_edit: function (parameters) {
          return function () {
            var current_grid = list_objects.get(parameters.idx).jqgrid;
            var rows_to_send = {};
            if (current_grid.editable_columns.length === 0 && isEmptyObject(current_grid.dirty_fields)) {
              return;
            }
            // This is done to make sure we detect rows by key column and not by row id
            var number_of_records = current_grid.object.jqGrid('getGridParam','records');
            for (var record_number = 1; record_number <= number_of_records; record_number++) {
              var row = jQuery("#" + current_grid.id).jqGrid('getRowData',record_number);
              if (current_grid.dirty_fields[row.key] !== undefined) {
                // This row should be updated, create object
                rows_to_send[row.key] = {};
                jQuery.each(current_grid.dirty_fields[row.key], function (column_index, column_name) {
                  rows_to_send[row.key][column_name] = row[column_name];
                });
              }
            }
            if (parameters.url === "") {
              parameters.url = window.location.href;
            }
            jQuery.post(
              parameters.url,
              {
                xsrf_token: window.xsrf_token,
                idx: parameters.idx,
                button_id: parameters.button_id,
                data: JSON.stringify(rows_to_send)
              },
              function (data) {
                if (parameters.redirect == "true") {
                  try {
                    var data_from_server = JSON.parse(data);
                    if (data_from_server.data.url !== undefined) {
                      window.location.href = data_from_server.data.url;
                    }
                  }
                  catch (e) {
                    //TODO (Mario): display an error message
                  }
                }
                var refresh_int = parseInt(parameters.refresh, 10);
                if (!isNaN(refresh_int)) {
                  list_objects.get(refresh_int).refreshData();
                  jQuery("#" + list_objects.get(refresh_int).jqgrid.id).trigger("reloadGrid");
                }
                if (parameters.refresh == "current") {
                  list_objects.get(parameters.idx).refreshData();
                  jQuery("#" + list_objects.get(parameters.idx).jqgrid.id).trigger("reloadGrid");
                }
                else if (parameters.refresh == "all") {
                  var lists = list_objects.getAll();
                  jQuery.each(lists, function (list_index, list_object) {
                    list_object.refreshData();
                    jQuery("#" + list_objects.get(list_index).jqgrid.id).trigger("reloadGrid");
                  });
                }
              }
            )
          }
        }
      },
      row_functions : {
        redirect_custom: function (parameters) {
          return function (link, event) {
            /* Even if default is not to open in a new window/tab, will open
               if middle button click or if ctrl+left button click.
            */
            if ((parameters.new_window) || (event.which === 2) || ((event.which === 1) && (event.ctrlKey))) {
              return function () {
                window.open(link);
              }
            }
            else {
              return function () {
                window.location.href = link;
              }
            }
          };
         }
       }
    };

    var createListHTML = function () {
        jQuery("#" + div).replaceWith([
          '<p id="temporary_list_placeholder_',idx,'">',
          '</p>',
          '<table id="' + _self.jqgrid.id + '"',
          ' cellpadding="0" cellspacing="0"',
          '></table>',
          '<div id="' + _self.jqgrid.pager.id + '"',
          ' style="text-align:center"',
          '></div>'
        ].join(""));
    };

    var fetchDataFromServer = function() {
      var start = "";
      var current_loop = 0;

      var server_loop = function () {
        // Preserve current query string
        var ampersand_question = "?";
        if (window.location.href.indexOf("?") !== -1) {
          ampersand_question = "&";
        }
        jQuery.ajax({
          async: true,
          cache: false,
          url: [
            window.location.href,
            ampersand_question,
            "fmt=json&limit=150",
            (start === "" ? "" : "&start=" + start),
            "&idx=", idx
          ].join(""),
          timeout: 60000,
          tryCount: 1,
          retryLimit: 5,
          error: function (xhr, textStatus, errorThrown) {
            // retry on 500 errors from server
            if (xhr.status == 500) {
              this.tryCount++;
              if (this.tryCount <= this.retryLimit) {
                jQuery.ajax(this);
                return;
              }
              // retryLimit is reached, show a message
              jQuery("#temporary_list_placeholder_" + idx).html([
                '<span style="color:red">',
                'Error retrieving data: please refresh the list or the whole page to try again',
                '</span>'].join("")
              );
              jQuery("#load_" + _self.jqgrid.id).hide();
            } else {
              // another error from server, show a message
              jQuery("#temporary_list_placeholder_" + idx).html([
                '<span style="color:red">',
                'Error retrieving data: please refresh the list or the whole page to try again',
                '</span>'].join("")
              );
              jQuery("#load_" + _self.jqgrid.id).hide();
            }
          },
          success: function (data_from_server) {
            var source = data_from_server;
            var first_batch_received = (current_loop > 0);
            var data_received = source.data[start] !== undefined;
            var last_batch = !source.data[start].length;

            if (data_received && (!first_batch_received || !last_batch)) {
              // temporary fix until Issue 766
              if (_self.configuration === null) {
                _self.configuration = source.configuration;
              }
              if (_self.operations === null) {
                _self.operations = source.operations;
              }
              var my_data = source.data[start];

              jQuery.each(my_data, function () {
                _self.data.data.push(this.columns);
                _self.data.all_data.push(this);
              });

              //if jQGrid object is not already instantiated, create it
              if (_self.jqgrid.object === null) {
                initJQGrid();
              }
              else {
                //else trigger new data in jqgrid object
                _self.jqgrid.object.trigger("reloadGrid");
              }

              //call next iteration
              if (my_data[(my_data.length- 1)] !== undefined) {
                start = source.next;
                setTimeout(server_loop, 100);
                current_loop++;
              }
              else {
                jQuery("#temporary_list_placeholder_" + idx).remove();
                jQuery("#load_" + _self.jqgrid.id).hide();
              }
            }
            else {
              //loading data finished, hiding loading message
              jQuery("#temporary_list_placeholder_" + idx).remove();
              jQuery("#load_" + _self.jqgrid.id).hide();

              //Trigger toolbar set default filters if a default one is requested (searchoptions)
              jQuery("#" + _self.jqgrid.id)[0].triggerToolbar();

              //check if there are editable columns
              jQuery.each(_self.configuration.colModel, function (column_index, column) {
                if (column.editable !== undefined && column.editable === true) {
                  _self.jqgrid.editable_columns.push(column.name);
                }
              });

              // Delete previous buttons, if any
              jQuery("#t_" + _self.jqgrid.id).children().remove();

              // Add global action buttons on the toolbar
              if (_self.operations !== undefined && _self.operations.buttons !== undefined) {
                jQuery.each(_self.operations.buttons, function (setting_index, operation) {
                  var bounds = operation.bounds;
                  // create button for global operation
                  var new_button_id = _self.jqgrid.id + "_buttonOp_" + operation.id;
                  jQuery("#t_" + _self.jqgrid.id).append("<input type='button' value='" + operation.caption + "' style='float:left' id='" + new_button_id + "'/>");

                  operation.parameters.idx = idx;

                  /* If this button is a post_edit button then button bounds should
                     behave differently: the button should be disabled if no dirty
                     fields are detected, then enabled the first time a cell content
                     is changed
                  */
                  if (operation.type !== "post_edit") {
                    // Substitute "all" string (if any) to actual number of records
                    operation.real_bounds = operation.bounds;
                    var handle_all = operation.real_bounds.indexOf("all");
                    if (handle_all !== -1) {
                      operation.real_bounds[handle_all] = _self.jqgrid.object.jqGrid('getGridParam','records');
                    }
                    /* Add button bounds on parameters to let POST
                       requests working also with [0,"all"] bounds */
                    operation.parameters.real_bounds = operation.real_bounds;
                  }
                  // the button should be disabled by default if lower bound is >0 or operation is a post_edit one
                  if (operation.type === "post_edit" || operation.real_bounds[0] > 0) {
                    jQuery("#" + new_button_id).attr("disabled","disabled");
                  }
                  /* Add id of the button operation to parameters so the appropriate backend action
                     can be identified if multiple buttons redirect to the same page. */
                  operation.parameters.button_id = operation.id;
                  // associate action
                  jQuery("#" + new_button_id).click(jqgrid_functions.global_button_functions[operation.type](operation.parameters));
                  // If this is a partial function, than store it in a safe place
                  if (operation.type == "redirect_custom") {
                    jQuery("#" + new_button_id).data(
                      'melange',
                      {
                        click: jqgrid_functions.global_button_functions[operation.type](operation.parameters)
                      }
                    );
                  }
                });
              }

              //Add row action if present
              /*var multiselect = _self.jqgrid.object.jqGrid('getGridParam','multiselect');
              if (_self.operations !== undefined && _self.operations.row !== undefined && !isEmptyObject(_self.operations.row)) {

                // if row action is present, than change cursor
                // FIXME: this is done by polling continuosly the body element
                // this is not so elegant nor efficient, need to find another solution
                jQuery("body").live("mouseover", function() {
                  if (multiselect) {
                    jQuery("#" + _self.jqgrid.id + " tbody tr td:gt(0)").css("cursor","pointer")
                  }
                  else {
                    jQuery("#" + _self.jqgrid.id + " tbody tr td").css("cursor","pointer")
                  }
                });

                var operation = _self.operations.row;
                operation.parameters.idx = idx;

                // If this is a partial function, than store it in a safe place
                if (operation.type == "redirect_custom") {
                  _self.jqgrid.object.data(
                    'melange',
                    {
                      rowsel: jqgrid_functions.row_functions[operation.type](operation.parameters)
                    }
                  );
                }
                // associate action to row
                _self.jqgrid.object.jqGrid('setGridParam',{
                  onCellSelect: function (row_number, cell_index, cell_content, event) {*/
                    /* If this is a multiselect table, do not trigger row action
                       if user clicks on a checkbox in the first column
                    */
                    /*if (multiselect && cell_index == 0) {
                      return;
                    }
                    // get current selection
                    var row = jQuery("#" + _self.jqgrid.id).jqGrid('getRowData',row_number);
                    var object = jLinq.from(_self.data.all_data).equals("columns.key",row.key).select()[0];
                    var partial_row_method = _self.jqgrid.object.data('melange').rowsel;
                    partial_row_method(object.operations.row.link, event)();
                  }
                });
              }*/

              //Add CSV Export button and RegEx switch only once all data is loaded

              //Add some padding at the bottom of the toolbar to display buttons correctly
              jQuery("#t_" + _self.jqgrid.id).css("padding-bottom","3px");

              //Add CSV export button
              jQuery("#t_" + _self.jqgrid.id).append("<input type='button' value='CSV Export' style='float:right' id='csvexport_" + _self.jqgrid.id + "'/>");
              //Add Click event to CSV export button
              jQuery("#csvexport_" + _self.jqgrid.id).click(function () {
                var csv_export = [];
                csv_export[0] = [];
                //get Columns names
                if (_self.data.data[0] !== undefined || _self.data.filtered_data[0] !== undefined) {
                  var iterate_through = _self.data.filtered_data || _self.data.data;
                  jQuery.each(_self.configuration.colNames, function (column_index, column_name) {
                    // check index for column name
                    var field_text = column_name;
                    // Check for &quot;, which is translated to " when output to textarea
                    field_text = field_text.replace(/\"|&quot;|&#34;/g,"\"\"");

                    if (field_text.indexOf(",") !== -1 || field_text.indexOf("\"") !== -1 || field_text.indexOf("\r\n") !== -1) {
                      field_text = "\"" + field_text + "\"";
                    }
                    csv_export[0].push(field_text);
                  });
                  csv_export[0] = csv_export[0].join(",");

                  //Check the actual order of the column, so the data dictionary can be in any order
                  var column_ids = [];
                  jQuery.each(_self.configuration.colModel, function (column, details) {
                    column_ids.push(details.name);
                  });
                  //now run through the columns
                  jQuery.each(iterate_through, function (row_index, row) {
                    csv_export[csv_export.length] = [];
                    jQuery.each(column_ids, function (column_index, column_id) {
                      var cell_value = row[column_id];
                      if (cell_value === null) {
                        cell_value = "";
                      }
                      if (cell_value === undefined) {
                        cell_value = "";
                      }
                      var field_text = cell_value.toString();

                      // extract link href (if any) from the text
                      var extracted_text = /^<a\b[^>]*href="(.*?)" \b[^>]*>(.*?)<\/a>$/.exec(field_text);
                      if (extracted_text !== null) {
                        field_text = extracted_text[1];
                      }

                      // Check for &quot;, which is translated to " when output to textarea
                      field_text = field_text.replace(/\"|&quot;|&#34;/g,"\"\"");

                      if (field_text.indexOf(",") !== -1 || field_text.indexOf("\"") !== -1 || field_text.indexOf("\r\n") !== -1) {
                        field_text = "\"" + field_text + "\"";
                      }
                      csv_export[csv_export.length - 1].push(field_text);
                    });
                    csv_export[csv_export.length - 1] = csv_export[csv_export.length - 1].join(",");
                  });
                  csv_export = csv_export.join("\r\n");

                }
              });

              //Add RegExp switch
              jQuery("#t_" + _self.jqgrid.id).append("<div style='float:right;margin-right:4px;'><input type='checkbox' id='regexp_" + _self.jqgrid.id + "'/>RegExp Search</div>");

              //Make the switch trigger a new search when clicked
              jQuery("#regexp_" + _self.jqgrid.id).click(function () {
                jQuery("#" + _self.jqgrid.id).jqGrid().trigger("reloadGrid");
              });


              //Trigger event when loading of the list is finished
              var loaded_event = jQuery.Event("melange_list_loaded");
              loaded_event.list_object = _self;
              _self.jqgrid.object.trigger(loaded_event);
              //console.debug("void, skipping");
            }
          }
        });
      };
      setTimeout(server_loop, 100);
    };

    this.refreshData = function () {
      _self.data = {
        data: [],
        all_data: [],
        filtered_data: null
      };
      fetchDataFromServer();
    }

    var initJQGrid = function () {
      var final_jqgrid_configuration = jQuery.extend(
        _self.configuration,
        {
          //giving index of the table in post data
          postData: {my_index: idx},
          // Disable or enable button depending on how many rows are selected
          onSelectAll: jqgrid_functions.enableDisableButtons,
          onSelectRow: jqgrid_functions.enableDisableButtons
        }
      );

      var button_showhide_options = {
        caption: "",
        buttonicon: "ui-icon-calculator",
        onClickButton: function () {
          jQuery("#" + _self.jqgrid.id).setColumns({
            colnameview: false,
            jqModal: true,
            ShrinkToFit: true
          });
          return false;
        },
        position: "last",
        title: "Show/Hide Columns",
        cursor: "pointer"
      };

      jQuery("#" + _self.jqgrid.id)
       .jqGrid(
         jQuery.extend(_self.jqgrid.options, final_jqgrid_configuration)
       )
       .jqGrid(
         // show pager
         "navGrid",
         "#" + _self.jqgrid.pager.id,
         _self.jqgrid.pager.options,
         {}, // settings for edit
         {}, // settings for add
         {}, // settings for delete
         {
           closeAfterSearch: true,
           multipleSearch: true
         },
         {} // view parameters
        ).jqGrid(
          // show button to hide/show columns
          "navButtonAdd",
          "#" + _self.jqgrid.pager.id,
          button_showhide_options
        );
      jQuery("#" + _self.jqgrid.id).jqGrid('filterToolbar', {});

      // Show Loading message, after substituting it with an animated image
      jQuery("#load_" + _self.jqgrid.id).closest("div").css("line-height","100%");
      jQuery("#load_" + _self.jqgrid.id).html("<img src='/soc/content/images/jqgrid_loading.gif'></img>");
      jQuery("#load_" + _self.jqgrid.id).show();

      _self.jqgrid.object = jQuery("#" + _self.jqgrid.id);
    };

    this.getDiv = function () {return div;};
    this.getIdx = function () {return idx;};

    var init = function () {
      jQuery(
        function () {
          if (jQuery("#" + div).length === 0) {
            throw new melange.error.divNotExistent("Div " + div + " is not existent");
          }

          _self.jqgrid.id = "jqgrid_" + div;
          _self.jqgrid.pager.id = "jqgrid_pager_" + div;
          _self.jqgrid.options = jQuery.extend(default_jqgrid_options, {pager: "#" + _self.jqgrid.pager.id});
          _self.jqgrid.pager.options = default_pager_options;

          list_objects.add(_self);

          createListHTML();
          initJQGrid();
          fetchDataFromServer();
        }
      );

    }();
  };

  $m.loadList = function (div, init, idx) {
    var idx = parseInt(idx, 10);
    var init = JSON.parse(init);
    if (isNaN(idx) || idx < 0) {
      throw new melange.error.listIndexNotValid("List index " + idx + " is not valid");
    }
    if (list_objects.isExistent(idx)) {
      throw new melange.error.indexAlreadyExistent("Index " + idx + " is already existent");
    }

    var list = new List(div, idx, init.configuration, init.operations);
  };
}());

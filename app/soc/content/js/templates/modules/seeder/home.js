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
 * @author <a href="mailto:sttwister@gmail.com">Felix Kerekes</a>
 */

(function () {
  var melange = window.melange;
  this.prototype = new melange.templates._baseTemplate();
  this.prototype.constructor = melange.templates._baseTemplate;
  melange.templates._baseTemplate.apply(this, arguments);

  var _self = this;

  var MODEL_SELECTOR_DIRECTIVE = {
    ".model_select_option": {
      "model<-models": {
        ".": "model.name",
        ".@value": "model.name"
      }
    }
  };

  var BASE_MODEL_CONTAINER_DIRECTIVE = {
    ".@id": "model.name",
    ".model_name": "model.name",

    ".property_set_container": {
      "property_set<-properties_data": {
        ".@property_set_name": "property_set.name",
        ".property_set_name": "property_set.name",

        ".property_container": {
          "property<-property_set.properties": {
            ".@property_name": "property.name",

            ".@reference_class": "property.reference_class",

            ".property_name": function(a) {
              context = a.context;
              property = a.item;

              var prefix = "";
              if (property.required) {
                prefix = "(*) ";
              }
              var suffix = "";
              if (property.reference_class) {
		suffix = " -> " + property.reference_class;
              }

              return prefix + property.verbose_name + " - " + property.type + suffix;
            },

            ".provider_select@property_name": "property.name",
            ".provider_select@required": "property.required",

            ".provider_select_option": {
              "provider<-property.providers": {
                ".": "provider.name",
                ".@value": "provider.name"
              }
            }

          }
        }
      }
    }
  };

  var MODEL_CONTAINER_DIRECTIVE = BASE_MODEL_CONTAINER_DIRECTIVE;

  var NESTED_MODEL_CONTAINER_DIRECTIVE = BASE_MODEL_CONTAINER_DIRECTIVE;

  jQuery.extend(NESTED_MODEL_CONTAINER_DIRECTIVE, {
    ".@class": function() {
      return "model_container";
    }
  });

  var PROVIDER_CONTAINER_DIRECTIVE = {
	".@provider_name": "provider.name",
	".provider_description": "provider.description",

    ".provider_parameter_container": {
      "parameter<-provider.parameters": {
        ".@parameter_name": "parameter.name",
        ".parameter_name": "parameter.verbose_name",
        ".parameter_description": "parameter.description",
        ".parameter_required": function(a) {
          parameter = a.item;
          if (parameter.required) {
            return "(required)";
          }
          return "";
        },
        ".provider_parameter_input@parameter_name": "parameter.name"
      }
    }
  };

  var REFERENCE_MODEL_SELECTOR_DIRECTIVE = {
    ".model_select_option": {
      "model<-models": {
        ".": function(a) {
          model = a.item;
          prefix = "";

          for (i = 0; i < model.level-1; ++i) {
            prefix = prefix + "| ";
          }

          if (model.level > 0) {
            prefix = prefix + "+-";
          }

          return prefix + model.name;
        },

        ".@value": "model.name"
      }
    }
  };

  /**
   * Fired when a model selector for a reference property has been changed.
   *
   * @param event
   *          The event that triggered the action.
   * @param renderer
   *          The renderer to use for rendering the new model configuration.
   *
   */
  var selectedModelChanged = function(event, renderer) {
    var select = event.target;
    var property_div = jQuery(jQuery(select).parents(".property_container")[0]);

    var reference_model_parameters_div =
      jQuery(".reference_model_parameters", property_div);

    var reference_class = select.value;
    melange.seeder.log(5, "Adding new model reference provider to " +
        reference_class);

    var model = melange.seeder.getModel(reference_class);
    var properties_data = melange.seeder.getProperties(reference_class);
    var model_data = {
        model: model,
        properties_data: properties_data
    };
    var model_html = renderer(model_data);
    jQuery(reference_model_parameters_div).html(model_html);
    jQuery(".model_remove_link").click(onRemoveModelClicked);
    jQuery(".provider_select").change(onProviderChanged);
    initializeToggle(reference_model_parameters_div);
    addDefaultProviders(reference_model_parameters_div);
  }

  /**
   * Wrapper for selectedModelChanged for direct references.
   */
  var selectedNewModelChanged = function(event) {
    selectedModelChanged(event, _self.nestedModelContainerRenderer);
  };

  /**
   * Wrapper for selectedModelChanged for back references.
   */
  var selectedRelatedModelChanged = function(event) {
    selectedModelChanged(event, _self.modelContainerRenderer);
  };

  /**
   * Adds a model selector to the DOM.
   *
   * @param property_div
   *          The DOM div element holding the model property.
   * @param provider_parameters_div
   *          The DOM div element holding the provider parameters.
   * @param callback
   *          The callback to be called when the selected model is changed.
   */
  var addModelSelector = function(property_div,
                                  provider_parameters_div,
                                  callback) {

    var reference_class = property_div.attr("reference_class");
    var models = melange.seeder.getModelChildren(reference_class);
    var data = {
        models: models
    };
    var models_selector_html = _self.referenceModelSelectorRenderer(data);
    provider_parameters_div.html(models_selector_html);
    jQuery(".model_select", provider_parameters_div).change(callback);
    jQuery(".model_select", provider_parameters_div).change();
  }

  /**
   * Fired when the test button for a provider is clicked.
   *
   * @param event
   *          The event that triggered the action.
   */
  var onTestProviderClicked = function(event) {
	var test_button = event.target;
	var provider_div = jQuery(test_button).parents(".provider_container")[0];
	var provider_name = jQuery(provider_div).attr("provider_name");

	var provider_response_div = jQuery(".test_provider_response", provider_div);

	var parameters = {};

	jQuery(".provider_parameter_input", provider_div).each(
	  function(index, parameter_input) {
		var name = jQuery(parameter_input).attr("parameter_name");
		var value = parameter_input.value;
		if (value !== "") {
		  parameters[name] = value;
		}
	  }
	);

	var data = {
	  "provider_name": provider_name,
	  "parameters": parameters
	};
    json = JSON.stringify(data);

    jQuery.post(
      "/seeder/test_provider",
      {
        xsrf_token: window.xsrf_token,
        data: json
      },
      function(response) {
        // TODO: Report any errors to the user
        data = JSON.parse(response);

	jQuery(provider_response_div).text(data.value);
      }
    );
  }

  /**
   * Update the list of words for model properties that have choices.
   *
   * @param property_div
   *          The property DOM element corresponding to the property to check
   *          for choices.
   */
  var addChoicesToProvider = function(property_div) {
    var provider_parameters_div = jQuery(".provider_parameters", property_div);

    var property_name = property_div.attr("property_name");
    var property_set_div = property_div.parents(
        ".property_set_container")[0];
    var model_name = jQuery(property_set_div).attr(
        "property_set_name");

    var model = melange.seeder.getModel(model_name);

    var property = null;
    jQuery.each(model.properties, function(index, prop)
      {
        if (prop.name === property_name) {
          property = prop;
        }
      }
    );

    if (property && property.choices) {
      var input = jQuery("input[parameter_name=choices]",
          provider_parameters_div)[0];
      var choices = property.choices.join(",");
      input.value = property.choices.join(",");
    }
  }

  /**
   * Update the class of referenced model for reference model properties.
   *
   * @param property_div
   *          The property DOM element corresponding to the property to check
   *          for choices.
   */
  var addReferenceClassToProvider = function(property_div) {
    var provider_parameters_div = jQuery(".provider_parameters", property_div);

    var property_name = property_div.attr("property_name");
    var property_set_div = property_div.parents(
        ".property_set_container")[0];
    var model_name = jQuery(property_set_div).attr(
        "property_set_name");

    var model = melange.seeder.getModel(model_name);

    var property = null;
    jQuery.each(model.properties, function(index, prop)
      {
        if (prop.name === property_name) {
          property = prop;
        }
      }
    );

    if (property && property.reference_class) {
      var input = jQuery("input[parameter_name=model_name]",
          provider_parameters_div)[0];
      input.value = property.reference_class;
    }
  }

  /**
   * Update the parameters input boxes for a provider.
   *
   * @param provider_select
   *          The DOM element for the provider select element.
   */
  var updateProviderParameters = function(provider_select) {
    var property_div = jQuery(jQuery(provider_select).parents(".property_container")[0]);
    var provider_name = provider_select.value;

    var provider_parameters_div = jQuery(".provider_parameters", property_div);
    provider_parameters_div.empty();

    if (provider_name !== "none") {

      if (provider_name === "NewModel") {
        addModelSelector(property_div, provider_parameters_div,
            selectedNewModelChanged);
        return;
      }

      if (provider_name === "RelatedModels") {
        addModelSelector(property_div, provider_parameters_div,
            selectedRelatedModelChanged);
        return;
      }

      melange.seeder.log(5, "Adding parameters for " + provider_name + "...");
      var providers = melange.seeder.getProvidersList();
      var provider = melange.seeder.getProvider(provider_name);
      data = {
          provider: provider
      };
      html = _self.providerContainerRenderer(data);
      melange.seeder.log(5, "Parameters added!");
      provider_parameters_div.html(html);

      jQuery(".test_provider").click(onTestProviderClicked);

      if (provider_name === "RandomWordProvider") {
        addChoicesToProvider(property_div);
      }

      if (provider_name === "RandomReferenceProvider") {
        addReferenceClassToProvider(property_div);
      }
    }
  }

  /**
   * Called when the data provider for a model property is changed by the user.
   * Updates the parameters for the new data provider.
   *
   * @param event
   *          The event that triggered the action.
   */
  var onProviderChanged = function(event) {
    var provider_select = event.target;
    melange.seeder.log(5, "Provider changed!");

    updateProviderParameters(provider_select);
  }

  /**
   * Called when the user clicks on the remove model link. Removes the model
   * from the DOM and from the list of models to seed.
   */
  var onRemoveModelClicked = function(event) {
    var link = event.target;
    var model_div = jQuery(link).parent().parent();
    jQuery(model_div).remove();
  }


  /**
   * Adds a new model to the DOM.
   *
   * @param model_name
   *          The name of the model to add.
   * @return The div holding the model that was added to the DOM.
   */
  var addModel = function(model_name) {
    var model = melange.seeder.getModel(model_name);
    var properties_data = melange.seeder.getProperties(model_name);
    data = {
        model: model,
        properties_data: properties_data
    };
    var model_div = jQuery(_self.modelContainerRenderer(data));
    jQuery(".provider_select", model_div).change(onProviderChanged);
    jQuery(".model_remove_link", model_div).click(onRemoveModelClicked);
    melange.seeder.log(5, "Model " + model_name + " added!");
    initializeToggle(model_div);
    addDefaultProviders(model_div);
    return model_div;
  }

  /**
   * Adds a new model to the DOM and add it to the models list.
   *
   * @param model_name
   *          The name of the model to add.
   * @return The div holding the model that was added to the DOM.
   */
  var addModelToRoot = function(model_name) {
    var model_div = addModel(model_name);
    jQuery("#selected_models").append(model_div);
    return model_div;
  }

  /**
   * Adds default data providers for required properties.
   *
   * @param model_div
   *          The DOM element containing the model.
   */
  var addDefaultProviders = function(model_div) {
    melange.seeder.log(5, "Adding default providers!!!");

    // Iterate over all properties
    jQuery(".provider_select", model_div).each(
      function(_, provider_select) {

        if (provider_select.value === "none" &&
            jQuery(provider_select).attr("required") === "true") {
          // Iterate over all data providers
          for (i = 0; i < provider_select.options.length; ++i) {
            var option = provider_select.options[i];

            // Pick the first provider that starts with Random
            if (option.value.match("^Random") == "Random") {
              provider_select.value = option.value;
              jQuery(provider_select).change();
              break;
            }
          }
        }
      }
    );
  }

  /**
   * Called when the user clicks the add model button in order to add a new
   * model to seed. Updates the list of models to be seeded along with all the
   * properties of the new model.
   *
   */
  var onAddModelClicked = function() {
    var model_name = jQuery(".model_select")[0].value;
    melange.seeder.log(5, "Adding model " + model_name + "...");
    addModelToRoot(model_name);
  }

  /**
   * Return a configuration sheet for the seeding operation extracted from the
   * DOM starting from a specific element.
   */
  var getConfigurationSheetFromElement = function(model_div, nested) {

    var model = {
      name: model_div.id
    };

    // Check if the model has a number input
    // Nested models don"t have number input
    var number_input = jQuery("input#number", model_div)[0];
    if (number_input) {
      model.number = number_input.value;
    }

    var properties = {};
    // Iterate over all the model"s properties
    jQuery(".property_container", model_div).each(
      function (index, property_div) {
        var property_name = jQuery(property_div).attr("property_name");

        var provider_select = jQuery(".provider_select", property_div)[0];
        var provider_name = provider_select.value;

        // Check that this property actually belong to the current model
        // and not to a nested referenced model
        var parent_class = jQuery(model_div).attr("class");
        var parent = jQuery(property_div).parents("." + parent_class)[0];
        if (parent !== model_div) {
          return;
        }

        if (provider_name !== "none") {
          var provider = {};
          provider.provider_name = provider_name;
          var parameters = {};

          if (provider_name === "NewModel") {
            // Recurse if there"s a nested model
            var model_child = jQuery(".model_container", property_div)[0];
            parameters = getConfigurationSheetFromElement(model_child, true);
          } else if (provider_name === "RelatedModels") {
            // Recurse if there"s a nested model
            var model_child = jQuery(".model_container", property_div)[0];
            parameters = getConfigurationSheetFromElement(model_child, true);
          } else {
            // Iterate over all the data provider parameters
            jQuery(".provider_parameter_container", property_div).each(
              function(index, parameter_div) {
                var parameter_name = jQuery(parameter_div).attr("parameter_name");
                var input = jQuery("input", parameter_div)[0].value;
                if (input) {
                  parameters[parameter_name] = input;
                }
              }
            );
          }

          provider.parameters = parameters;
          properties[property_name] = provider;
        }
      }
    );
    model["properties"] = properties;
    return model;
  }

  /**
   * Returns a configuration sheet for the seeding operation extracted from the
   * DOM.
   */
  var getConfigurationSheet = function () {
    melange.seeder.log(5, "Building configuration sheet...");
    var sheet = [];
    jQuery(".model_container").each(
      function(index, element) {
        var parent = jQuery(element).parent()[0];
        var parent_id = jQuery(parent).attr("id");
        if (parent_id === "selected_models") {
          sheet.push(getConfigurationSheetFromElement(element));
        }
      }
    );
    melange.seeder.log(5, "Configuration sheet built:");
    melange.seeder.log(5, sheet);
    return sheet;
  }

  /**
   * Called when the users clicks the validate configuration sheet button.
   * Sends the configuration sheet to the server for validation.
   */
  var onValidateConfigurationSheetClicked = function () {
    melange.seeder.log(5, "Validating configuration sheet");

    var sheet = getConfigurationSheet();
    var json = JSON.stringify(sheet);

    // Redirect to the echo service so we are prompted with a download
    jQuery.post(
      "/seeder/validate_configuration_sheet",
      {
        xsrf_token: window.xsrf_token,
        data: json
      },
      function(response) {
        // TODO: Report any errors to the user
        data = JSON.parse(response);
      }
    );
  }

  /**
   * Called when the users clicks the get configuration sheet button. Allows the
   * user to save the configuration sheet.
   */
  var onDownloadConfigurationSheetClicked = function () {
    var sheet = getConfigurationSheet();
    var json = JSON.stringify(sheet);

    jQuery("#download_configuration_sheet_data").attr("value", json);
  }

  /**
   * Callback called after a seeding job has been started.
   */
  var seedingJobStarted = function (response) {
    melange.seeder.log(5, "Response:");
    melange.seeder.log(5, response);

    data = JSON.parse(response);

    if (data.response === "success") {
      var id = data["id"];

      window.location = "/mapreduce/detail?mapreduce_id="+id;
    } else {
      // TODO: Report this to the user
      melange.seeder.log(5, "ERROR!!!");
    }
  }

  /**
   * Called when the users clicks the send configuration sheet button. Sends the
   * configuration sheet to the server to begin seeding.
   */
  var onSendConfigurationSheetClicked = function () {
    var sheet = getConfigurationSheet();
    melange.seeder.sendConfigurationSheet(sheet, seedingJobStarted);
  }

  /**
   * Set up the properties of a model and display them.
   *
   * @param model_data
   *          The model data from the configuration sheet containing the
   *          properties.
   * @param model_div
   *          The DOM div element corresponding to the model.
   */
  var loadModelProperties = function(model_data, model_div) {
    jQuery.each(model_data.properties,
      function(property_name, property) {
        var query = ".property_container[property_name="+property_name+"]";

        // Get the property_div whose parent is model_div
        var property_div = jQuery(query, model_div).filter(
          function(index) {
            return jQuery(this).parents(".model_container")[0] === model_div[0];
          }
        )[0];

        // Set the provider select to the right value
        var provider_select = jQuery(".provider_select", property_div)[0];
        provider_select.value = property.provider_name;

        // Update the parameter input buxes for the provider
        updateProviderParameters(provider_select);

        var parameters = property.parameters;

        if (property.provider_name === "NewModel") {
          var model_select = jQuery(".model_select", property_div);
          model_select.attr("value", parameters.name);
          model_select.change();

          var nested_model_div = jQuery(".model_container", property_div);

          loadModelProperties(parameters, nested_model_div);
        } else if (property.provider_name === "RelatedModels") {
          var model_select = jQuery(".model_select", property_div);
          model_select.attr("value", parameters.name);
          model_select.change();

          var nested_model_div = jQuery(".model_container", property_div);

          var number_input = jQuery("input#number", nested_model_div)[0];
          number_input.value = parameters.number;

          loadModelProperties(parameters, nested_model_div);
        } else {

          // Fill each input box with the value from the configuration sheet
          jQuery.each(parameters,
            function(parameter_name, parameter) {
              var query = ".provider_parameter_input[parameter_name="
                + parameter_name + "]";
              var input = jQuery(query, property_div)[0];

              input.value = parameter;
            }
          );
        }
      }
    );
  }

  /**
   * Load a configuration sheet and display it to the user.
   *
   * @param configuration_sheet
   *          The configuration sheet.
   */
  var loadConfigurationSheet = function (configuration_sheet) {
    melange.seeder.log(5, "Loading configuration sheet.");
    var configuration_sheet = JSON.parse(configuration_sheet);

    jQuery.each(configuration_sheet,
      function(index, model_data) {
        var model_div = addModelToRoot(model_data.name);

        var number_input = jQuery("input#number", model_div)[0];
        number_input.value = model_data.number;

        loadModelProperties(model_data, model_div);
      }
    );
  }

  /**
   * Initialize toggle operations on the specified element. Hides all containers
   * an add handlers for all triggers.
   */
  var initializeToggle = function(element) {
    // Hide (Collapse) the toggle containers on load
    jQuery(".toggle_container", element).hide();

    // Switch the "Open" and "Close" state per click then slide up/down
    // (depending on open/close state)
    jQuery(".trigger", element).click(
      function(){
        jQuery(this).toggleClass("active").next().slideToggle("fast");
      }
    );
  }

  /**
   * Initializes UI elements.
   */
  var initializeUI = function() {
    jQuery("#add_model_button").click(onAddModelClicked);
    jQuery("#validate_configuration_sheet_button").click(
        onValidateConfigurationSheetClicked);
    jQuery("#download_configuration_sheet_button").click(
        onDownloadConfigurationSheetClicked);
    jQuery("#send_configuration_sheet_button").click(
        onSendConfigurationSheetClicked);

    jQuery("#add_model_button").hide();
    jQuery("#validate_configuration_sheet_button").hide();
    jQuery("#send_configuration_sheet_button").hide();

    jQuery("#download_configuration").hide();
    jQuery("#load_configuration").hide();

    _self.modelSelectorRenderer = $p("#models_selector").compile(
        MODEL_SELECTOR_DIRECTIVE);
    jQuery("#models_selector").empty();
    jQuery("#models_selector").text("Loading, please wait...");

    _self.modelContainerRenderer = $p(".model_container").compile(
        MODEL_CONTAINER_DIRECTIVE);
    jQuery(".model_container").remove();

    _self.nestedModelContainerRenderer = $p(".nested_model_container").compile(
        NESTED_MODEL_CONTAINER_DIRECTIVE);
    jQuery(".nested_model_container").remove();

    _self.providerContainerRenderer = $p(".provider_container").compile(
        PROVIDER_CONTAINER_DIRECTIVE);
    jQuery(".provider_container").remove();

    _self.referenceModelSelectorRenderer = $p(".reference_model_selector").compile(
        REFERENCE_MODEL_SELECTOR_DIRECTIVE);
    jQuery(".reference_model_selector").remove();

    initializeToggle();
  }

  /**
   * Populates the list of models with data received from the server.
   *
   * @param models
   *          An object containing model information.
   */
  var populateModelList = function(models) {
    data = {
        models: melange.seeder.getModels()
    };
    jQuery("#models_selector").html(_self.modelSelectorRenderer(data));
    jQuery("#add_model_button").show();
    jQuery("#validate_configuration_sheet_button").show();
    jQuery("#send_configuration_sheet_button").show();

    jQuery("#download_configuration").show();
    jQuery("#load_configuration").show();
    melange.seeder.log(5, "Model list populated!");
  }

  /**
   * Called when the data from the server has been received.
   */
  var gotData = function() {
    melange.seeder.log(5, "Got data!");
    populateModelList(melange.seeder.getModels());

    configuration_sheet = this.context.configuration_sheet;
    if (configuration_sheet !== "") {
      loadConfigurationSheet(configuration_sheet);
    }
  }

  jQuery(document).ready(function() {
    melange.logging.setDebug();
    initializeUI();
    melange.seeder.getData(gotData);
  });

}());

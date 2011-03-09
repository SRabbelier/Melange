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
 * @author <a href="mailto:sttwister@gmail.com">Felix Kerekes</a>
 */
(function () {
  /** @lends melange.seeder */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all data seeder related functions
    * @name melange.seeder
    * @namespace melange.seeder
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.seeder = window.melange.seeder = function () {
    return new melange.seeder();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.seeder);

  var data = null;

  var NEW_MODEL_PROVIDER = {
      "name": "NewModel",
      "parameters": {},
      "Description": "KBLA"
  };

  var RELATED_MODELS_PROVIDER = {
      "name": "RelatedModels",
      "parameters": {},
      "Description": "KBLA"
  };

  melange.error.createErrors([
  ]);

  /** Queries the server for a JSON containing model and and data providers
   *  data. Calls a callback on success.
   *  @namespace melange.seeder
   *  @param callback The function to call on success.
   */
  $m.getData = function(callback) {
    jQuery.getJSON("/seeder/get_data",
      function(new_data) {
        data = new_data;

        data.providers["ReferenceProperty"].push(NEW_MODEL_PROVIDER);
        data.providers["_ReverseReferenceProperty"].push(RELATED_MODELS_PROVIDER);

        // For each property of each model, set the list of available providers
        jQuery.each(data.models,
          function(index, model) {
            jQuery.each(model.properties,
              function(index, property) {
                property.providers = $m.getProviders(property.type);
              }
            );
          }
        );

        callback();
      }
    );
  }

  /** Returns an array of models information.
   *  @return An object containing models information.
   */
  $m.getModels = function() {
    return data.models;
  }

  /** Returns information about a specific model.
   *  @param model_name The name of the model.
   *  @return Object containing information about the model.
   */
  $m.getModel = function(model_name) {
    result = null;
    jQuery.each(this.getModels(),
      function(index, model) {
        if (model.name === model_name)
          result = model;
      }
    );
    return result;
  }

  /**
   * Returns a list of the children of the model. The parent model is also
   * included in the list. Also recurses to children.
   *
   * @param model_name The name of the model whose children to return.
   * @return A list of children model.
   */
  $m.getModelChildren = function(model_name, level) {
    if (level === undefined) {
      level = 0;
    }

    model = $m.getModel(model_name);
    model.level = level;

    var result = [ model ];

    var children = jLinq
        .from($m.getModels(), "name")
        .contains("parent", model_name)
        .select();

    jQuery.each(children, function(index, child) {
      var tmp = $m.getModelChildren(child.name, level+1);
      result = result.concat(tmp);
    });

    return result;
  }

  /** Returns an object containing providers information, mapped by
   *  the type which the provider seeds.
   *  @return An object containing providers information.
   */
  $m.getProvidersData = function() {
    return data.providers;
  }

  /** Returns an object containing information about all data providers,
   *  mapped by data provider name.
   *  @return An object containing data providers information.
   */
  $m.getProvidersList = function() {
    var result = [];
    jQuery.each(this.getProvidersData(),
      function(property_type, providers) {
        jQuery.each(providers,
          function(index, provider) {
            result.push(provider);
          }
        );
      }
    );
    return result;
  }

  /** Returns a list of providers matching the specified property_type.
   *  @return A list of providers.
   */
  $m.getProviders = function(property_type) {
    return $m.getProvidersData()[property_type];
  };

  /** Returns information about a specific provider.
   *  @param provider_name The name of the provider.
   *  @return Object containing information about the provider.
   */
  $m.getProvider = function(provider_name) {
    result = null;
    jQuery.each(this.getProvidersList(),
      function(index, provider) {
        if (provider.name === provider_name)
          result = provider;
      }
    );
    return result;
  }

  /** Returns an object containing properties information about a specific
   *  model. The data is represented as an array containing properties for each
   *  model and parent.
   *  @param model_name The name of the model whose properties are returned.
   *  @return An object containing properties information for the model.
   */
  $m.getProperties = function(model_name) {
    var properties_container = [];
    var model = this.getModel(model_name);

    // Get the properties from all the parents
    while (model != undefined) {
      properties_data = {
        name: model_name,
        properties: model.properties
      }

      properties_container.push(properties_data);
      model_name = model.parent;
      model = this.getModel(model_name);
    }

    return properties_container;
  }

  /** Sends the configuration sheet to the server to begin seeding.
   */
  $m.sendConfigurationSheet = function(sheet, callback) {
    json = JSON.stringify(sheet);
    jQuery.post(
      "/seeder/seed",
      {
        xsrf_token: window.xsrf_token,
        data: json
      },
      callback
    );
  }

}());
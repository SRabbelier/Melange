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
  /** @lends melange */

  /** General melange package.
    * @name melange
    * @namespace melange
    */
  var melange = window.melange = function () {
    return new melange();
  };

  if (window.jQuery === undefined) {
    throw new Error("jQuery package must be loaded exposing jQuery namespace");
  }

  /** Shortcut to current package.
    * @private
    */
  var $m = melange;

  /** Contains general configuration for melange package.
    * @variable
    * @public
    * @name melange.config
    */
  $m.config = {};

  $m.init = function (configuration) {
    if (configuration) {
      $m.config = jQuery.extend($m.config, configuration);
    }
  };

  /** Shortcut to clone objects using jQuery.
    * @function
    * @public
    * @name melange.clone
    * @param {Object} object the object to clone
    * @returns {Object} a new, cloned object
    */
  $m.clone = function (object) {
    // clone object, see
    // http://stackoverflow.com/questions/122102/
    // what-is-the-most-efficent-way-to-clone-a-javascript-object
    return jQuery.extend(true, {}, object);
  };

  /** Set melange general options.
    * @function
    * @public
    * @name melange.setOptions
    * @param {Object} options Options to set/unset
    */
  $m.setOptions = function (options) {
    switch (options.debug) {
    case true:
      $m.logging.setDebug();
      break;
    case false:
      $m.logging.unsetDebug();
      break;
    default:
      $m.logging.setDebug();
    }
    if (options.debugLevel) {
      $m.logging.setDebugLevel(options.debugLevel);
    }
  };

  /** Facility to load google API.
    * @function
    * @public
    * @name melange.loadGoogleApi
    * @param {String} modulename Google Ajax module to load
    * @param {String|Number} moduleversion Google Ajax module version to load
    * @param {Object} settings Google Ajax settings for the module
    * @param {Function} callback to be called as soon as module is loaded
    */
  $m.loadGoogleApi = function (modulename, moduleversion, settings, callback) {

    if (!modulename || !moduleversion) {
      throw new TypeError("modulename must be defined");
    }

    /** Options to be sent to google.load constructor
      * @private
      * @name melange.loadGoogleApi.options
      */
    var options = {
      name : modulename,
      version : moduleversion,
      settings : settings
    };
    jQuery.extend(options.settings, {callback: callback});
    google.load(options.name, options.version, options.settings);
  };

  (function () {
    /** @lends melange.error */

    /** Package that handles melange errors
      * @namespace melange.error
      */
    melange.error = window.melange.error = function () {
      return new melange.error();
    };

    /** Shortcut to current package.
      * @property
      * @private
      */
    var $m = melange.error;

    /** List of default custom error types to be created.
      * @property
      * @private
      */
    var error_types = [
      "DependencyNotSatisfied",
      "notImplementedByChildClass"
    ];

    /** Create errors
      * @function
      * @public
      * @name melange.error.createErrors
      * @param {String[]} error_types Array of strings with errors names
      */
    $m.createErrors = function (error_types) {
      jQuery.each(error_types, function () {
        melange.error[this] = Error;
      });
    };

    $m.createErrors(error_types);
  }());

  (function () {
    /** @lends melange.logging */

    /** Package that contains all log related functions.
      * @name melange.logging
      * @namespace melange.logging
      */
    melange.logging = window.melange.logging = function () {
      return new melange.logging();
    };

    /** Shortcut to current package.
      * @property
      * @private
      */
    var $m = melange.logging;
    /** @private */
    var debug = false;
    /** @private */
    var current_debug_level = 5;

    /** Set debug logging on.
      * @function
      * @public
      * @name melange.logging.setDebug
      */
    $m.setDebug = function () {
      debug = true;
    };

    /** Set debug logging off.
      * @function
      * @public
      * @name melange.logging.unsetDebug
      */
    $m.unsetDebug = function () {
      debug = false;
    };

    /** Check if debug is active.
      * @function
      * @public
      * @name melange.logging.isDebug
      * @returns {boolean} true if debug is on, false otherwise
      */
    $m.isDebug = function () {
      return debug ? true : false;
    };

    /** Set the current debug level.
      * @function
      * @public
      * @name melange.logging.setDebugLevel
      * @param level The log level to set
      * @throws {TypeError} if the parameter given is not a number
      */
    $m.setDebugLevel = function (level) {
      if (isNaN(level)) {
        throw new melange.error.TypeError(
          "melange.logging.setDebugLevel: parameter must be a number"
        );
      }
      if (level <= 0) {
        level = 1;
      }
      if (level >= 6) {
        level = 5;
      }
      current_debug_level = level;
    };

    /** Get the current debug level.
      * @function
      * @public
      * @name melange.logging.getDebugLevel
      * @returns {Number} The current debug level
      */
    $m.getDebugLevel = function () {
      return current_debug_level;
    };

    /** A decorator for logging.
      * @function
      * @public
      * @name melange.logging.debugDecorator
      * @param {Object} object_to_decorate The Function/Object to decorate
      * @returns {Object} Same object,decorated with log(level,message) func
    */
    $m.debugDecorator = function (object_to_decorate) {
      /** Function to handle output of logs.
        * @function
        * @name melange.logging.debugDecorator.log
        * @param level The log level
        * @param message The string
        */
      object_to_decorate.log = function (level, message) {
          if (melange.logging.isDebug() && current_debug_level >= level) {
            console.debug(message);
          }
        };
      return object_to_decorate;
    };
  }());

  (function () {
    /** @lends melange.templates */

    /** Package that provides basic templates functions
      * @name melange.templates
      * @namespace melange.templates
      */
    melange.templates = window.melange.templates = function () {
      return new melange.templates();
    };

    /** Shortcut to current package
      * @private
      */
    var $m = melange.logging.debugDecorator(melange.templates);

    melange.error.createErrors([
    ]);

    /** Contains a queue of all loaded templates
      *
      * This is needed to keep track of all loaded templates
      * and to give them appropriate contexts using the
      * following setContextToLast function.
      * @private
      */
    var templatesQueue = [];

    /** Assign a context to the template
      *
      * @function
      * @public
      * @name melange.templates.setContextToLast
      */
    $m.setContextToLast = function (context) {
      var last_template = templatesQueue[(templatesQueue.length - 1)];
      last_template.context = jQuery.extend(last_template.context, context);
    };

    /** Parent prototype for all templates
      * @class
      * @constructor
      * @name melange.templates._baseTemplate
      * @public
      */
    $m._baseTemplate = function () {
      // Create internal context variable and push this template to the queue
      this.context = {};
      templatesQueue.push(this);
    };
  }());
}());
window.melange = window.melange.logging.debugDecorator(window.melange);

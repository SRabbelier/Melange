#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Custom optparse OptionParser and functions for reading Python settings files.

  Option:  class derived from optparse.Option that adds a 'required' parameter
  OptionParser:  class derived from optparse.OptionParser for use with Option

  readPythonSettings():  interprets a valid Python file as a settings file
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import os
import optparse
import sys


DEF_SETTINGS_FILE_DIR = "~"
DEF_SETTINGS_FILE_NAME = '.soc_scripts_settings'


class Error(Exception):
  """Base exception class for all exceptions in the settings module."""
  pass


class Option(optparse.Option):
  """Class derived from optparse.Option that adds a 'required' parameter."""

  ATTRS = optparse.Option.ATTRS + ['required']

  def _check_required(self):
    """Insures that 'required' option can accept a value."""
    if self.required and (not self.takes_value()):
      raise optparse.OptionError(
          "'required' parameter set for option that does not take a value",
          self)

  # Make sure _check_required() is called from the constructor!
  CHECK_METHODS = optparse.Option.CHECK_METHODS + [_check_required]

  def process(self, opt, value, values, parser):
    optparse.Option.process(self, opt, value, values, parser)
    parser.option_seen[self] = 1


class OptionParser(optparse.OptionParser):
  """Class derived from optparse.OptionParser for use with Option."""

  def _init_parsing_state(self):
    """Sets up dict to track options seen so far."""
    optparse.OptionParser._init_parsing_state(self)
    self.option_seen = {}

  def error(self, *args):
    """Convert errors reported by optparse.OptionParser to Error exceptions.

    Args:
      *args:  passed through to the Error exception __init__() constructor,
        usually a list of strings

    Raises:
      Error with the supplied *args
    """
    raise Error(*args)

  def check_values(self, values, args):
    """Checks to make sure all required=True options were supplied.

    Args:
      values, args:  passed through unchanged (see Returns:)

    Returns:
      (values, args) unchanged.

    Raises:
      Error if an option was not supplied that had required=True;  exception
      positional arguments are the error message strings.
    """
    errors = []

    for option in self.option_list:
      if (isinstance(option, Option)
          and option.required
          and (not self.option_seen.has_key(option))):
        errors.append(
            'required %s option not supplied' % option)

    if errors:
      self.error(*errors)

    return values, args


def readPythonSettings(defaults={},  # {} OK since defaults is always copied
                       settings_dir=DEF_SETTINGS_FILE_DIR,
                       settings_file=DEF_SETTINGS_FILE_NAME):
  """Executes a Python-syntax settings file and returns the local variables.

  Args:
    defaults:  dict of default values to use when settings are not present
      in the settings file (or if no settings file is present at all);  this
      dict is *copied* and is not altered at all
    settings_dir:  optional directory containing settings_file
    settings_file:  optional settings file name found in settings_dir

  Returns:
    dict of setting name/value pairs (possibly including some values from the
    defaults parameter).  Since the settings file is full-fledged Python
    source, the values could be any valid Python object.

  Raises:
    Error if some error occurred parsing the present settings file;  exception
    positional arguments are the error message strings.
  """
  # do not let the original defaults be altered
  defaults = defaults.copy()

  # form absolute path to the settings file, expanding any environment
  # variables and "~", then removing excess . and .. path elements
  path = os.path.abspath(
      os.path.normpath(
          os.path.expanduser(
              os.path.expandvars(
                  os.path.join(settings_dir, settings_file)))))

  # empty dict to capture the local variables in the settings file
  settings_locals = {}

  try:
    # execute the Python source file and recover the local variables as settings
    execfile(path, {}, settings_locals)
  except IOError:
    # If the settings file is not present, there are no defaults.
    pass
  except Exception, error:
    # Other exceptions usually mean a faulty settings file.
    raise Error(
        'faulty settings file:',
        ('  %s: %s' % (error.__class__.__name__, str(error))),
        ('  %s' % path))

  # overwrite defaults copy with values from the (possibly empty) settings file
  defaults.update(settings_locals)

  return defaults

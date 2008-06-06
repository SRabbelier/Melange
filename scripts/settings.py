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

Default values for trunk/scripts flags can be specified in valid Python syntax
in the ~/.soc_scripts_settings file.  For example, a default value for the
--user flag can be specified with a variable assignment in the settings file
like:

  user = 'joeuser'

Defaults in the ~/.soc_scripts_settings file can be explicitly overridden by
supplied the actual flag.  For example, supplying:

  --user=someotheruser

would override the default value present in the settings file.

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
            'required %s option not supplied'
            ' (and default settings not allowed)' % option)

    if errors:
      self.error(*errors)

    return values, args


def printErrors(errors, exit_code=1):
  """Prints error message strings to sys.stderr and returns an exit code.

  Args:
    errors: error message string or list of error message strings to be printed
      to sys.stderr
    exit_code: exit code to return (so that this function can be used as an
      expression in sys.exit() for example); default is 1

  Returns:
    exit_code
  """
  sys.stderr.write('\nERRORS:\n')

  if (not isinstance(errors, tuple)) and (not isinstance(errors, list)):
    errors = [errors]

  for msg in errors:
    sys.stderr.write('  %s\n' % msg)

  sys.stderr.write('\n')

  return exit_code


def printErrorsAndUsage(errors, parser, exit_code=1):
  """Prints error messages and usage text to sys.stderr and returns exit code.

  Args:
    errors: error message string or list of error message strings to be printed
      to sys.stderr
    parser: OptionParser with a print_help() method
    exit_code: exit code to return (so that this function can be used as an
      expression in sys.exit() for example); default is 1

  Returns:
    exit_code
  """
  exit_code = printErrors(errors, exit_code=exit_code)
  parser.print_help(file=sys.stderr)

  return exit_code


def getExpandedPath(path):
  """Returns an expanded, normalized, absolute path.

  Args:
    path: path (possibly relative, possibly containing environment variables,
      etc.) to be expanded, normalized and made absolute

  Returns:
    absolute path, after expanding any environment variables and "~", then
    removing excess . and .. path elements
  """
  return os.path.abspath(
      os.path.normpath(
          os.path.expanduser(
              os.path.expandvars(path))))


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
  path = getExpandedPath(os.path.join(settings_dir, settings_file))

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


def readPythonSettingsOrDie(parser=None,
                            defaults={},  # {} OK since defaults is always copied
                            settings_dir=DEF_SETTINGS_FILE_DIR,
                            settings_file=DEF_SETTINGS_FILE_NAME):
  """Calls readPythonSettings(), calling sys.exit() on any errors.

  Args:
    parser: if supplied, an OptionParser instance used to call print_help()
      to print usage information if errors occur
    defaults, settings_dir, settings_file: see readPythonSettings()

  Returns:
    On success, returns results of readPythonSettings().

  Exits:
    On any error from readPythonSettings(), prints error messages to stderr,
    possibly prints usage information, and calls sys.exit(1).
  """
  try:
    return readPythonSettings(defaults=defaults, settings_dir=settings_dir,
                              settings_file=settings_file)
  except Error, error:
    if parser:
      sys.exit(printErrorsAndUsage(error.args, parser))
    else:
      sys.exit(printErrors(error.args))


def makeOptionParserOrDie(*args, **kwargs):
  """Creates and returns an OptionParser, calling sys.exit() on any errors.

  Args:
    *args, **kwargs: supplied directly to OptionParser constructor

  Returns:
    On success, returns an OptionParser instance.

  Exits:
    On any error, prints error messages to stderr and calls sys.exit(1).
  """
  try:
    return OptionParser(*args, **kwargs)
  except Error, error:
    sys.exit(printErrors(error.args))


def parseOptionsOrDie(parser, args):
  """Parses command-line options, calling sys.exit() on any errors.

  Args:
    parser: an OptionParser instance
    args: list of command-line arguments to supply to parser

  Returns:
    On success, returns (options, args) returned by parser.parse_args(args).

  Exits:
    On any error, prints error messages and usage information to stderr and
    calls sys.exit(1).
  """
  try:
    return parser.parse_args(args)
  except Error, error:
    sys.exit(printErrorsAndUsage(error.args, parser))


def checkCommonSvnOptions(options):
  """Checks a common subset of command-line options.

  Multiple scripts accept a subset of common command-line options.

  Args:
    options: OptionParser.parse_args() options instance to check

  Returns:
    list of error message strings, or an empty list if no errors
  """
  errors = []

  if not options.repo:
    errors.extend(
        ['--repo must be supplied or have a settings file default'])

  if not options.wc:
    errors.extend(
        ['--wc must be supplied or have a settings file default'])

  if not options.branch:
    if not options.user:
      errors.extend(
          ['at least one of --branch or --user must be supplied'])

  return errors


def checkCommonSvnOptionsOrDie(options, parser):
  """Checks subset of command-line options, calling sys.exit() on any errors.

  Args:
    options: see checkCommonSvnOptions()
    parser: an OptionParser instance used to call print_help() to print
      usage information if errors occur

  Exits:
    On any error messages returned by checkCommonSvnOptions(), prints error
    messages and usage information to stderr and calls sys.exit(1).
  """
  errors = checkCommonSvnOptions(options)

  if errors:
    sys.exit(printErrorsAndUsage(errors, parser))

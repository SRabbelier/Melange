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

# __doc__ string is slightly unconventional because it is used as usage text
"""%prog [OPTIONS] [FIND_REGEX] [REPLACE_FORMAT]

Script to list, search, and modify files using Python regex patterns.

OPTIONS:  optional command-line flags; see %prog --help

FIND_REGEX:  an optional valid Python regular expression pattern;
  if supplied, only files containing at least one match will be processed;
  matching file paths will be printed; if supplied, REPLACE_FORMAT will be
  used to convert the match groups into formatted output.

REPLACE_FORMAT:  an optional valid Python format string;
  FIND_REGEX must be supplied first if REPLACE_FORMAT is supplied;
  positional arguments will be replaced with ordered groups from
  FIND_REGEX matches, and named arguments will be replaced with named
  groups from FIND_REGEX matches."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


import dircache
import errno
import os
import optparse
import re
import sre_constants
import sys


class Error(Exception):
  """Base class of all exceptions in this module.
  """
  pass


def compileRegex(pattern):
  """Compiles a Python regex pattern into a regex object.

  Args:
    pattern: valid Python regex pattern string, or an already-compiled
      regex object (in which case this function is is a no-op)

  Returns:
    regex object compiled from pattern

  Raises:
    Error if pattern could not be compiled.
  """
  try:
    return re.compile(pattern)
  except sre_constants.error, error:
    msg = 're.compile: %s\n%s' % (error.args[0], pattern)
    raise Error(errno.EINVAL, msg)


def findAll(text_to_search, pattern):
  """Returns all matches of a regex in a string.
  
  Args:
    text_to_search: string in which to find matches
    pattern: Python regex pattern (or already-compiled regex object)
      indicating which matches to retrieve

  Returns:
    a (possibly empty) list of the matches found, as strings 
  """
  matches = []

  def _captureMatchText(match):
    match_text = match.group()
    matches.append(match_text)
    return match_text

  compileRegex(pattern).sub(_captureMatchText, text_to_search)

  return matches 


def getFileContents(file_path):
  """Reads the contents of a file as a single string, then closes the file.
  
  Args:
    file_path: path to the file to read its contents into a string
    
  Returns:
    a single string containing the entire contents of the file
  """
  file_to_read = open(file_path)
  file_contents = file_to_read.read()
  file_to_read.close()
  return file_contents


def findAllInFile(file_path, pattern, *ignored_args, **ignored_kwargs): 
  """Action to return a list of all pattern matches in a file.
  
  Args:
    file_path: path of file to manipulate
    pattern: see findAll()
    *ignored_args: other positional arguments which are ignored
      command-line arguments not used by this action callable
    **ignored_kwargs: other keyword arguments which are ignored
      command-line options not used by this action callable
    
  Returns:
    two-tuple of boolean indicating if any match was found and a
    (possibly empty) list of the matches found, as strings (to be used
    as printable output of the action)
  """
  matches = findAll(getFileContents(file_path), pattern)

  if matches:
    found = True
  else:
    found = False

  return found, matches


def replaceAll(original, pattern, format):
  """Substitutes formatted text for all matches in a string.
  
  Args:
    original: original string in which to find and replace matches
    pattern: Python regex pattern (or already-compiled regex object)
      indicating which matches to replace
    format: Python format string specifying how to format the
      replacement text; how this format string is interpreted depends
      on the contents of the pattern;  if the pattern contains:
        named groups: format is expected to contain named format specifiers
        unnamed groups: format is expected to contain exactly the same
          number of unnamed format specifiers as the number of groups in
          pattern
        no groups: format is expected to contain a single format specifier
          (in which case the entire match is supplied to it), or no format
          specifier at all (in which case the "format" string simply
          replaces the match with no substitutions from the match itself)

  Returns:
    two-tuple of the text with all matches replaced as specified by
    pattern and format, and a list of the original matches, each followed
    by its replacement 
  """
  matches_and_replacements = []

  def _replaceWithFormat(match):
    formatted_match = None

    if match.groupdict():
      try:
        formatted_match = format % match.groupdict()
      except TypeError:
        pass

    if (not formatted_match) and match.groups():
      try:
        formatted_match = format % match.groups()
      except TypeError:
        pass

    if (not formatted_match):
      try:
        formatted_match = format % match.group()
      except TypeError:
        formatted_match = format

    matches_and_replacements.append(match.group())
    matches_and_replacements.append(formatted_match)
    return formatted_match

  replaced = compileRegex(pattern).sub(_replaceWithFormat, original)

  return replaced, matches_and_replacements


def writeAltFileIfExt(path, ext, contents):
  """Writes a file if path and additional extension are supplied.

  If path or ext are not supplied, no file is written.

  Args:
    path: path of file to be written, to which ext will be appended
    ext: additional file extension that will be appended to path
    contents: contents of file to be written, as a string
  """
  if (not path) or (not ext):
    return

  if ext.startswith('.'):
    ext = ext[1:]
 
  alt_path = '%s.%s' % (path, ext)
  alt_file = open(alt_path, 'w')
  alt_file.write(contents) 
  alt_file.close()


def replaceAllInFile(file_path, pattern, format,
                     new_ext=None, backup_ext=None,
                     overwrite_files=False,
                     *ignored_args, **ignored_kwargs): 
  """Substitutes formatted text for all matches in a file.
  
  Args:
    file_path: path of file to manipulate
    pattern, format: see replaceAll()
    *ignored_args: other positional arguments which are ignored
      command-line arguments not used by this action callable
    **ignored_kwargs: other keyword arguments which are ignored
      command-line options not used by this action callable
    
  Returns:
    two-tuple of boolean indicating if any match was found and a
    list of printable output text lines containing pairs of original
    pattern matches each followed by the formatted replacement
  """
  original = getFileContents(file_path)

  replaced, matches_and_replacements = replaceAll(
    original, pattern, format)

  if matches_and_replacements:
    found = True
    writeAltFileIfExt(file_path, new_ext, replaced)
    writeAltFileIfExt(file_path, backup_ext, original)

    if overwrite_files:
      if replaced != original:
        replaced_file = open(file_path, 'w')
        replaced_file.write(replaced)
        replaced_file.close()
  else:
    found = False

  return found, matches_and_replacements


def listFile(*ignored_args, **ignored_kwargs): 
  """No-op action callable that ignores arguments and returns (True, []).
  """
  return True, []  # match only based on file names, which was done by caller


def applyActionToFiles(action, action_args,
                       start_path='', abs_path=False, files_pattern='',
                       recurse_dirs=False, dirs_pattern='',
                       follow_symlinks=False, quiet_output=False,
                       hide_paths=False, **action_options):
  """Applies a callable action to files, based on options and arguments.
  
  Args:
    action: callable that expects a file path argument, positional arguments
      (action_args), and keyword options from the command-line options dict;
      and returns a "matched" boolean and a list of output strings
    action_args: list of positional arguments, if any; passed to action
      callable unchanged
    start_path: required path of initial directory to visit
    abs_path: optional boolean indicating to use absolute paths
    files_pattern: required Python regex (object or pattern) which selects
      which files to pass to the action callable
    recurse_dirs: boolean indicating if subdirectories should be traversed 
    dirs_pattern: Python regex (object or pattern) which selects which
      subdirectories to traverse if recurse_dirs is True
    follow_symlinks: boolean indicating if symlinks should be traversed
    quiet_output: optional boolean indicating if output should be suppressed
    hide_paths: optional boolean indicating to omit file paths from output
    **action_options: remaining keyword arguments that are passed unchanged
      to the action callable

  Returns:
    two-tuple containing an exit code and a (possibly empty) list of
    output strings
    
  Raises:
    Error exception if problems occur (file I/O, invalid regex, etc.).
  """
  exit_code = errno.ENOENT
  output = []

  start_path = os.path.expandvars(os.path.expanduser(start_path))

  if abs_path:
    start_path = os.path.abspath(start_path)

  paths = [start_path]

  files_regex = compileRegex(files_pattern)
  
  if recurse_dirs:
    dirs_regex = compileRegex(dirs_pattern)

  while paths:
    sub_paths = []

    for path in paths:
      # expand iterator into an actual list and sort it
      try:
        items = dircache.listdir(path)[:]
      except (IOError, OSError), error:
        raise Error(error.args[0], '%s: %s' % (
                    error.__class__.__name__, error.args[1]))

      items.sort()

      for item in items:
        item_path = os.path.join(path, item)

        if os.path.islink(item_path):
          if not follow_symlinks:
            continue  # do not follow symlinks (ignore them)

        if os.path.isdir(item_path):
          if recurse_dirs:
            if dirs_regex.match(item):
              sub_paths.append(item_path)
          continue
      
        if files_regex.match(item):
          try:
            matched, found_output = action(item_path, *action_args,
                                           **action_options)
          except (IOError, OSError), error:
            raise Error(error.args[0], '%s: %s' % (
                        error.__class__.__name__, error.args[1]))

          if matched:
            exit_code = 0  # at least one matched file has now been found

            if (not quiet_output) and (not hide_paths):
              output.append(item_path)

          if not quiet_output:
            output.extend(found_output)

    paths = sub_paths
  
  return exit_code, output


class _ErrorOptionParser(optparse.OptionParser):
  """Customized optparse.OptionParser that does not call sys.exit().
  """

  def error(self, msg):
    """Raises an Error exception, instead of calling sys.exit().
    """
    raise Error(errno.EINVAL, msg)


def _buildParser():
  """Returns a custom OptionParser for parsing command-line arguments.
  """
  parser = _ErrorOptionParser(__doc__)

  filter_group = optparse.OptionGroup(parser,
    'File Options',
    'Options used to select which files to process.')

  filter_group.add_option(
    '-f', '--files', dest='files_pattern', default='^.*$',
    metavar='FILES_REGEX',
    help=('Python regex pattern (*not* a glob!) defining files to process'
          ' in each directory [default: %default]'))

  filter_group.add_option(
    '-F', '--follow', dest='follow_symlinks', default=False,
    action='store_true',
    help=('follow file and subdirectory symlinks (possibly *DANGEROUS*)'
          ' [default: %default]'))

  parser.add_option_group(filter_group)

  dir_group = optparse.OptionGroup(parser,
    'Directory Options',
    'Options used to indicate which directories to traverse.')

  dir_group.add_option(
    '-s', '--start', dest='start_path', default=os.curdir, metavar='PATH',
    help='directory in which to start processing files [default: %default]')

  dir_group.add_option(
    '-R', '--recursive', dest='recurse_dirs', default=False,
    action='store_true',
    help='recurse into subdirectories [default: %default]')

  dir_group.add_option(
    '-d', '--dirs', dest='dirs_pattern', default='^.*$',
    metavar='SUBDIRS_REGEX',
    help=('Python regex pattern (*not* a glob!) defining subdirectories to'
          ' recurse into (if --recursive) [default: %default]'))

  parser.add_option_group(dir_group)

  output_group = optparse.OptionGroup(parser,
    'Output Options',
    'Options used to control program output.')

  output_group.add_option(
    '-a', '--abspath', dest='abs_path', default=False, action='store_true',
    help=('output absolute paths instead of relative paths'
          ' [default: %default]'))

  output_group.add_option(
    '-p', '--nopaths', dest='hide_paths', default=False, action='store_true',
    help=('suppress printing of file path names for successfully matched'
          ' files to stdout [default: %default]'))

  output_group.add_option(
    '-q', '--quiet', dest='quiet_output', default=False, action='store_true',
    help=('suppress *all* printed output to stdout (but still perform'
          ' replacements if specified) [default: %default]'))

  parser.add_option_group(output_group)

  replace_group = optparse.OptionGroup(parser,
    'Replace Options',
    'Options applied when matches in files are replaced with substitutions.'
    ' (Only possible if REPLACE_FORMAT is supplied.)')

  replace_group.add_option(
    '-o', '--overwrite', dest='overwrite_files', default=False,
    action='store_true',
    help=('overwrite original files with formatted text substituted for'
          ' matches [default: %default]'))  

  replace_group.add_option(
    '-b', '--backup', dest='backup_ext', default='', metavar='EXTENSION',
    help=('if supplied, and file would be overwritten, backup original'
          ' file with the supplied extension [default is no backups of'
          ' overwritten files are kept]'))

  replace_group.add_option(
    '-n', '--new', dest='new_ext', default='', metavar='EXTENSION',
    help=('if supplied, and file has matches and and is altered by'
          ' substitutions, create a new file with the supplied extension'
          ' [default is no new file is created]'))

  parser.add_option_group(replace_group)

  return parser


def _parseArgs(cmd_line_args):
  """Builds a command-line option parser and parses command-line arguments.
  
  Args:
    cmd_line_args: command-line arguments, excluding the argv[0] program name
    
  Returns:
    four-tuple of action callable, supplied command-line options (including
    those defined by defaults in the command-line parser) as a dict,
    remaining positional command-line arguments, and the parser itself
    
  Raises:
    Error if problems occurred during commmand-line argument parsing.
  """
  parser = _buildParser()
  options, args = parser.parse_args(args=cmd_line_args)

  if not args:
    # no FIND_REGEX or REPLACE_PATTERN supplied, so just match based
    # on file name and subdirectory name patterns
    action = listFile
  elif len(args) == 1:
    # FIND_REGEX supplied, but not REPLACE_PATTERN, so just match based
    # on file name and subdirectory name patterns, and then on file
    # contents
    action = findAllInFile
  elif len(args) == 2:
    # FIND_REGEX and REPLACE_PATTERN both supplied, so match based
    # on file name and subdirectory name patterns, and then do a find and
    # replace on file contents
    action = replaceAllInFile
  else:
    raise Error(errno.EINVAL,'too many (%d) arguments supplied:\n%s' % (
                len(args), ' '.join(args)))

  return action, vars(options), args, parser

 
def _main(argv):
  """Wrapper that catches exceptions, prints output, and returns exit status.
  
  Normal program output is printed to stdout.  Error output (including
  exception text) is printed to stderr.
  
  Args:
    argv: script arguments, usually sys.argv; argv[0] is expected to be the
      program name
      
  Returns:
    exit code suitable for sys.exit()
  """
  options = {}  # empty options, used if _parseArgs() fails

  try:
    action, options, args, parser = _parseArgs(argv[1:])
    exit_code, output = applyActionToFiles(action, args, **options)

    if output:  print '\n'.join(output)

  except Error, error:
    if not options.get('quiet_output'):
      print >>sys.stderr, '\nERROR: (%s: %s) %s\n' % (
        error.args[0], os.strerror(error.args[0]), error.args[1])
      print >>sys.stderr, parser.get_usage()

    exit_code = error.args[0]

  return exit_code


if __name__ == '__main__':
  sys.exit(_main(sys.argv))

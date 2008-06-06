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

"""Script to export a Google App Engine "image" of a Melange application.

For details:
  trunk/scripts/export_image.py --help

Default values for flags can be specified in valid Python syntax in the
~/.soc_scripts_settings file.  See settings.py for details.
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import os
import sys

import pysvn

from trunk.scripts import app_image
from trunk.scripts import settings
from trunk.scripts import svn_helper


def buildOptionList(defaults):
  """Returns a list of command-line settings.Options for this script.

  Args:
    defaults: dict of possible pre-loaded default values (may be empty)
  """
  def_repo = defaults.get('repo')

  if def_repo:
    repo_help_msg = 'SVN repository; default is %s' % def_repo
  else:
    repo_help_msg = 'SVN repository; REQUIRED if default unavailable'

  return [
      settings.Option(
          '-R', '--repo', action='store', dest='repo',
          default=def_repo, help=repo_help_msg),
      settings.Option(
          '-s', '--src', action='store', dest='src', required=True,
          help='(REQUIRED) name of source app in /trunk/apps/ to export'),
      settings.Option(
          '-i', '--image', action='store', dest='image', required=True,
          help='(REQUIRED) exported image destination'),
      settings.Option(
          '-r', '--rev', type='int', action='store', dest='rev',
          default=None, help='optional revision number on which to export'),
  ]


def main(args):
  # attempt to read the common trunk/scripts settings file
  defaults = settings.readPythonSettingsOrDie(
      parser=settings.OptionParser(option_list=buildOptionList({})))

  # create the command-line options parser
  parser = settings.makeOptionParserOrDie(
      option_list=buildOptionList(defaults))

  # parse the command-line options
  options, args = settings.parseOptionsOrDie(parser, args)

  # ensure that various paths end with the / separator
  src, image, repo = svn_helper.formatDirPaths(
      options.src, options.image, options.repo)

  # expand and make "OS-agnostic" the proposed App Engine image path
  # (which is why no working copy path is needed or supplied)
  image = svn_helper.getExpandedWorkingCopyPath(image)

  setup_errors = []

  # dirname() called twice because image always ends with os.sep
  parent_dir = os.path.dirname(os.path.dirname(image))

  if os.path.isdir(image):
    setup_errors.extend(
        ['--image destination directory must not already exist:',
         '  %s' % image])

  if not os.path.isdir(parent_dir):
    try:
      os.makedirs(parent_dir)
      print 'Created --image parent directory:\n %s\n' % parent_dir
    except (IOError, OSError), fs_err:
      setup_errors.extend(
          ['--image parent directory could not be created:',
           '  %s' % parent_dir,
           '  %s: %s' % (fs_err.__class__.__name__,
                       ' '.join([str(arg) for arg in fs_err.args]))])

  if not options.repo:
    setup_errors.extend(
        ['--repo must be supplied or have a settings file default'])

  if setup_errors:
    return settings.printErrorsAndUsage(setup_errors, parser)

  def callbackGetLogMessage():
    return True, 'trunk/apps/%s application exported to %s' % (src, image)

  client = svn_helper.getPySvnClient()
  # this should never actually be called, but just in case...
  client.callback_get_log_message = callbackGetLogMessage

  # export trunk/apps/<src> first, so image root directory will exist
  app_image.exportFromSrcApp(src, repo, image, rev=options.rev)
  app_image.exportFromThirdParty(repo, image, rev=options.rev)
  app_image.exportFromFramework(repo, image, rev=options.rev)

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv))

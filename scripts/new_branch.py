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

"""Script to make a Google App Engine "image" branch of a Melange application.

For details:
  trunk/scripts/new_branch.py --help

Default values for flags can be specified in valid Python syntax in the
~/.soc_scripts_settings file.  See settings.py for details.
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


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
  help_user = defaults.get('user', '<user>')
  user_help_msg = (
      'user name, used for default /users/%s/ branch' % help_user)
  dest_help_msg = (
      'if supplied, new name of branched app, users/%s/<dest>' % help_user)
  branch_help_msg = (
      'destination branch, defaults to <wc>/users/%s/<src|dest>' % help_user)

  def_repo = defaults.get('repo')

  if def_repo:
    repo_help_msg = 'SVN repository; default is %s' % def_repo
  else:
    repo_help_msg = 'SVN repository; REQUIRED if default unavailable'

  def_wc = defaults.get('wc')

  if def_wc:
    wc_help_msg = 'working copy directory; default is %s' % def_wc
  else:
    wc_help_msg = 'working copy directory; REQUIRED if default unavailable'

  return [
      settings.Option(
          '-R', '--repo', action='store', dest='repo',
          default=def_repo, help=repo_help_msg),
      settings.Option(
          '-w', '--wc', action='store', dest='wc',
          default=def_wc, help=wc_help_msg),
      settings.Option(
          '-s', '--src', action='store', dest='src', required=True,
          help='(REQUIRED) name of source app in /trunk/apps/ to branch'),
      settings.Option(
          '-d', '--dest', action='store', dest='dest', help=dest_help_msg),
      settings.Option(
          '-u', '--user', action='store', dest='user',
          default=defaults.get('user'), help=user_help_msg),
      settings.Option(
          '-b', '--branch', action='store', dest='branch',
          help=branch_help_msg),
      settings.Option(
          '-r', '--rev', type='int', action='store', dest='rev',
          default=None, help='optional revision number on which to branch'),
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
  src, dest, user, repo, wc = svn_helper.formatDirPaths(
      options.src, options.dest, options.user, options.repo, options.wc)

  settings.checkCommonSvnOptionsOrDie(options, parser)

  branch = app_image.formDefaultAppBranchPath(options.branch, user, src, dest)
  branch_path = svn_helper.getExpandedWorkingCopyPath(branch, wc_root=wc)

  # setup a callback used by pysvn if it needs a log message (it actually
  # should not be needed, since nothing is being committed, but exceptions
  # were being raised by pysvn without it)
  def callbackGetLogMessage():
    return True, 'trunk/apps/%s application branched to %s' % (src, branch)

  client = svn_helper.getPySvnClient()
  client.callback_get_log_message = callbackGetLogMessage

  # validate choice of "image" branch location
  if not options.branch:
    users = svn_helper.lsDirs(repo + 'users/')

    if user not in users:
      return settings.printErrorsAndUsage(
          ['%susers/%s not found; existing users are:' % (repo, user),
           ' '.join(users)], parser)

  if svn_helper.exists(branch_path):
    return settings.printErrorsAndUsage(
        ['%s already exists;' % branch_path,
         'use merge_branch.py to update instead'],
        parser)

  # branch trunk/apps/<src> first, so parent destination directory will exist
  app_image.branchFromSrcApp(src, repo, branch_path, rev=options.rev)
  app_image.branchFromThirdParty(repo, branch_path, rev=options.rev)
  app_image.branchFromFramework(repo, branch_path, rev=options.rev)

  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv))

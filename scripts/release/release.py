#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

from __future__ import with_statement

"""Google Summer of Code Melange release script.

This script provides automation for the various tasks involved in
pushing a new release of Melange to the official Google Summer of Code
app engine instance.

It does not provide a turnkey autopilot solution. Notably, each stage
of the release process must be started by a human operator, and some
commands will request confirmation or extra details before
proceeding. It is not a replacement for a cautious human
operator.

Note that this script requires:
 - Python 2.5 or better (for various language features)

 - Subversion 1.5.0 or better (for working copy depth control, which
     cuts down checkout/update times by several orders of
     magnitude).
"""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]


import functools
import os
import re
import subprocess
import sys

import error
import log
import subversion
import util


# Default repository URLs for Melange and the Google release
# repository.
MELANGE_REPOS = 'http://soc.googlecode.com/svn'
GOOGLE_SOC_REPOS = 'https://soc-google.googlecode.com/svn'


# Regular expression matching an apparently well formed Melange
# release number.
MELANGE_RELEASE_RE = re.compile(r'\d-\d-\d{8}p\d+')


class Error(error.Error):
  pass


class AbortedByUser(Error):
  """The operation was aborted by the user."""
  pass


class FileAccessError(Error):
  """An error occured while accessing a file."""
  pass


def getString(prompt):
  """Prompt for and return a string."""
  prompt += ' '
  log.stdout.write(prompt)
  log.stdout.flush()

  response = sys.stdin.readline()
  log.terminal_echo(prompt + response.strip())
  if not response:
    raise AbortedByUser('Aborted by ctrl+D')

  return response.strip()


def confirm(prompt, default=False):
  """Ask a yes/no question and return the answer.

  Will reprompt the user until one of "yes", "no", "y" or "n" is
  entered. The input is case insensitive.

  Args:
    prompt: The question to ask the user.
    default: The answer to return if the user just hits enter.

  Returns:
    True if the user answered affirmatively, False otherwise.
  """
  if default:
    question = prompt + ' [Yn]'
  else:
    question = prompt + ' [yN]'
  while True:
    answer = getString(question)
    if not answer:
      return default
    elif answer in ('y', 'yes'):
      return True
    elif answer in ('n', 'no'):
      return False
    else:
      log.error('Please answer yes or no.')


def getNumber(prompt):
  """Prompt for and return a number.

  Will reprompt the user until a number is entered.
  """
  while True:
    value_str = getString(prompt)
    try:
      return int(value_str)
    except ValueError:
      log.error('Please enter a number. You entered "%s".' % value_str)


def getChoice(intro, prompt, choices, done=None, suggest=None):
  """Prompt for and return a choice from a menu.

  Will reprompt the user until a valid menu entry is chosen.

  Args:
    intro: Text to print verbatim before the choice menu.
    prompt: The prompt to print right before accepting input.
    choices: The list of string choices to display.
    done: If not None, the list of indices of previously
      selected/completed choices.
    suggest: If not None, the index of the choice to highlight as
      the suggested choice.

  Returns:
    The index in the choices list of the selection the user made.
  """
  done = set(done or [])
  while True:
    print intro
    print
    for i, entry in enumerate(choices):
      done_text = ' (done)' if i in done else ''
      indent = '--> ' if i == suggest else '    '
      print '%s%2d. %s%s' % (indent, i+1, entry, done_text)
    print
    choice = getNumber(prompt)
    if 0 < choice <= len(choices):
      return choice-1
    log.error('%d is not a valid choice between %d and %d' %
              (choice, 1, len(choices)))
    print


def fileToLines(path):
  """Read a file and return it as a list of lines."""
  try:
    with file(path) as f:
      return f.read().split('\n')
  except (IOError, OSError), e:
    raise FileAccessError(str(e))


def linesToFile(path, lines):
  """Write a list of lines to a file."""
  try:
    with file(path, 'w') as f:
      f.write('\n'.join(lines))
  except (IOError, OSError), e:
    raise FileAccessError(str(e))


#
# Decorators for use in ReleaseEnvironment.
#
def pristine_wc(f):
  """A decorator that cleans up the release repository."""
  @functools.wraps(f)
  def revert_wc(self, *args, **kwargs):
    self.wc.revert()
    return f(self, *args, **kwargs)
  return revert_wc


def requires_branch(f):
  """A decorator that checks that a release branch is active."""
  @functools.wraps(f)
  def check_branch(self, *args, **kwargs):
    if self.branch is None:
      raise error.ExpectationFailed(
        'This operation requires an active release branch')
    return f(self, *args, **kwargs)
  return check_branch


class ReleaseEnvironment(util.Paths):
  """Encapsulates the state of a Melange release rolling environment.

  This class contains the actual releasing logic, and makes use of
  the previously defined utility classes to carry out user commands.

  Attributes:
    release_repos: The URL to the Google release repository root.
    upstream_repos: The URL to the Melange upstream repository root.
    wc: A Subversion object encapsulating a Google SoC working copy.
  """

  BRANCH_FILE = 'BRANCH'

  def __init__(self, root, release_repos, upstream_repos):
    """Initializer.

    Args:
      root: The root of the release environment.
      release_repos: The URL to the Google release repository root.
      upstream_repos: The URL to the Melange upstream repository root.
    """
    util.Paths.__init__(self, root)
    self.wc = subversion.WorkingCopy(self.path('google-soc'))
    self.release_repos = release_repos.strip('/')
    self.upstream_repos = upstream_repos.strip('/')

    if not self.wc.exists():
      self._InitializeWC()
    else:
      self.wc.revert()

      if self.exists(self.BRANCH_FILE):
        branch = fileToLines(self.path(self.BRANCH_FILE))[0]
        self._switchBranch(branch)
      else:
        self._switchBranch(None)

  def _InitializeWC(self):
    """Check out the initial release repository.

    Will also select the latest release branch, if any, so that
    the end state is a fully ready to function release environment.
    """
    log.info('Checking out the release repository')

    # Check out a sparse view of the relevant repository paths.
    self.wc.checkout(self.release_repos, depth='immediates')
    self.wc.update('vendor', depth='immediates')
    self.wc.update('branches', depth='immediates')
    self.wc.update('tags', depth='immediates')

    # Locate the most recent release branch, if any, and switch
    # the release environment to it.
    branches = self._listBranches()
    if not branches:
      self._switchBranch(None)
    else:
      self._switchBranch(branches[-1])

  def _listBranches(self):
    """Return a list of available Melange release branches.

    Branches are returned in sorted order, from least recent to
    most recent in release number ordering.
    """
    assert self.wc.exists('branches')
    branches = self.wc.ls('branches')

    # Some early release branches used a different naming scheme
    # that doesn't sort properly with new-style release names. We
    # filter those out here, along with empty lines.
    branches = [b.strip('/') for b in branches
          if MELANGE_RELEASE_RE.match(b.strip('/'))]

    return sorted(branches)

  def _switchBranch(self, release):
    """Activate the branch matching the given release.

    Once activated, this branch is the target of future release
    operations.

    None can be passed as the release. The result is that no
    branch is active, and all operations that require an active
    branch will fail until a branch is activated again. This is
    used only at initialization, when it is detected that there
    are no available release branches to activate.

    Args:
      release: The version number of a Melange release already
        imported in the release repository, or None to activate 
        no branch.

    """
    if release is None:
      self.branch = None
      self.branch_dir = None
      log.info('No release branch available')
    else:
      self.wc.update()
      assert self.wc.exists('branches/' + release)
      linesToFile(self.path(self.BRANCH_FILE), [release])
      self.branch = release
      self.branch_dir = 'branches/' + release
      self.wc.update(self.branch_dir, depth='infinity')
      log.info('Working on branch ' + self.branch)

  def _branchPath(self, path):
    """Return the given path with the release branch path prepended."""
    assert self.branch_dir is not None
    return os.path.join(self.branch_dir, path)

  #
  # Release engineering commands. See further down for their
  # integration into a commandline interface.
  #
  @pristine_wc
  def update(self):
    """Update and clean the release repository"""
    self.wc.update()

  @pristine_wc
  def switchToBranch(self):
    """Switch to another Melange release branch"""
    branches = self._listBranches()
    if not branches:
      raise error.ExpectationFailed(
        'No branches available. Please import one.')

    choice = getChoice('Available release branches:',
               'Your choice?',
               branches,
               suggest=len(branches)-1)
    self._switchBranch(branches[choice])

  def _addAppYaml(self):
    """Create a Google production app.yaml configuration.

    The file is copied and modified from the upstream
    app.yaml.template, configure for Google's Summer of Code App
    Engine instance, and committed.
    """
    if self.wc.exists(self._branchPath('app/app.yaml')):
      raise ObstructionError('app/app.yaml exists already')

    yaml_path = self._branchPath('app/app.yaml')
    self.wc.copy(yaml_path + '.template', yaml_path)

    yaml = fileToLines(self.wc.path(yaml_path))
    out = []
    for i, line in enumerate(yaml):
      stripped_line = line.strip()
      if 'TODO' in stripped_line:
        continue
      elif stripped_line == '# application: FIXME':
        out.append('application: socghop')
      elif stripped_line.startswith('version:'):
        out.append(line.lstrip() + 'g0')
        out.append('# * initial Google fork of Melange ' + self.branch)
      else:
        out.append(line)
    linesToFile(self.wc.path(yaml_path), out)

    self.wc.commit('Create app.yaml with Google patch version g0 '
             'in branch ' + self.branch)

  def _applyGooglePatches(self):
    """Apply Google-specific patches to a vanilla Melange release.

    Each patch is applied and committed in turn.
    """
    # Edit the base template to point users to the Google fork
    # of the Melange codebase instead of the vanilla release.
    tmpl_file = self.wc.path(
      self._branchPath('app/soc/templates/soc/base.html'))
    tmpl = fileToLines(tmpl_file)
    for i, line in enumerate(tmpl):
      if 'http://code.google.com/p/soc/source/browse/tags/' in line:
        tmpl[i] = line.replace('/p/soc/', '/p/soc-google/')
        break
    else:
      raise error.ExpectationFailed(
        'No source code link found in base.html')
    linesToFile(tmpl_file, tmpl)

    self.wc.commit(
      'Customize the Melange release link in the sidebar menu')

  @pristine_wc
  def importTag(self):
    """Import a new Melange release"""
    release = getString('Enter the Melange release to import:')
    if not release:
      AbortedByUser('No release provided, import aborted')

    branch_dir = 'branches/' + release
    if self.wc.exists(branch_dir):
      raise ObstructionError('Release %s already imported' % release)

    tag_url = '%s/tags/%s' % (self.upstream_repos, release)
    release_rev = subversion.find_tag_rev(tag_url)

    if confirm('Confirm import of release %s, tagged at r%d?' %
           (release, release_rev)):
      # Add an entry to the vendor externals for the Melange
      # release.
      externals = self.wc.propget('svn:externals', 'vendor/soc')
      externals.append('%s -r %d %s' % (release, release_rev, tag_url))
      self.wc.propset('svn:externals', '\n'.join(externals), 'vendor/soc')
      self.wc.commit('Add svn:externals entry to pull in Melange '
          'release %s at r%d.' % (release, release_rev))

      # Export the tag into the release repository's branches
      subversion.export(tag_url, release_rev, self.wc.path(branch_dir))

      # Add and commit the branch add (very long operation!)
      self.wc.add([branch_dir])
      self.wc.commit('Branch of Melange release %s' % release, branch_dir)
      self._switchBranch(release)

      # Commit the production GSoC configuration and
      # google-specific patches.
      self._addAppYaml()
      self._applyGooglePatches()

      # All done!
      log.info('Melange release %s imported and googlified' % self.branch)

  @requires_branch
  @pristine_wc
  def cherryPickChange(self):
    """Cherry-pick a change from the Melange trunk"""
    rev = getNumber('Revision number to cherry-pick:')
    bug = getNumber('Issue fixed by this change:')

    diff = subversion.diff(self.upstream_repos + '/trunk', rev)
    if not diff.strip():
      raise error.ExpectationFailed(
        'Retrieved diff is empty. '
        'Did you accidentally cherry-pick a branch change?')
    util.run(['patch', '-p0'], cwd=self.wc.path(self.branch_dir), stdin=diff)
    self.wc.addRemove(self.branch_dir)

    yaml_path = self.wc.path(self._branchPath('app/app.yaml'))
    out = []
    updated_patchlevel = False
    for line in fileToLines(yaml_path):
      if line.strip().startswith('version: '):
        version = line.strip().split()[-1]
        base, patch = line.rsplit('g', 1)
        new_version = '%sg%d' % (base, int(patch) + 1)
        message = ('Cherry-picked r%d from /p/soc/ to fix issue %d' %
            (rev, bug))
        out.append('version: ' + new_version)
        out.append('# * ' + message)
        updated_patchlevel = True
      else:
        out.append(line)

    if not updated_patchlevel:
      log.error('Failed to update Google patch revision')
      log.error('Cherry-picking failed')

    linesToFile(yaml_path, out)

    log.info('Check the diff about to be committed with:')
    log.info('svn diff ' + self.wc.path(self.branch_dir))
    if not confirm('Commit this change?'):
      raise AbortedByUser('Cherry-pick aborted')
    self.wc.commit(message)
    log.info('Cherry-picked r%d from the Melange trunk.' % rev)

  MENU_ORDER = [
    update,
    switchToBranch,
    importTag,
    cherryPickChange,
    ]

  MENU_STRINGS = [d.__doc__ for d in MENU_ORDER]

  MENU_SUGGESTIONS = {
    None: update,
    update: cherryPickChange,
    switchToBranch: cherryPickChange,
    importTag: cherryPickChange,
    cherryPickChange: None,
    }

  def interactiveMenu(self):
    done = []
    last_choice = None
    while True:
      # Show the user their previously completed operations and
      # a suggested next op, to remind them where they are in
      # the release process (useful after long operations that
      # may have caused lunch or an extended context switch).
      if last_choice is not None:
        last_command = self.MENU_ORDER[last_choice]
      else:
        last_command = None
      suggested_next = self.MENU_ORDER.index(
        self.MENU_SUGGESTIONS[last_command])

      try:
        choice = getChoice('Main menu:', 'Your choice?',
          self.MENU_STRINGS, done=done, suggest=suggested_next)
      except (KeyboardInterrupt, AbortedByUser):
        log.info('Exiting.')
        return
      try:
        self.MENU_ORDER[choice](self)
      except error.Error, e:
        log.error(str(e))
      else:
        done.append(choice)
        last_choice = choice


def main(argv):
  if not (1 <= len(argv) <= 3):
    print ('Usage: gsoc-release.py [release repos root URL] '
           '[upstream repos root URL]')
    sys.exit(1)

  release_repos, upstream_repos = GOOGLE_SOC_REPOS, MELANGE_REPOS
  if len(argv) >= 2:
    release_repos = argv[1]
  if len(argv) == 3:
    upstream_repos = argv[2]

  log.init('release.log')

  log.info('Release repository: ' + release_repos)
  log.info('Upstream repository: ' + upstream_repos)

  r = ReleaseEnvironment(os.path.abspath('_release_'),
                         release_repos,
                         upstream_repos)
  r.interactiveMenu()


if __name__ == '__main__':
  main(sys.argv)

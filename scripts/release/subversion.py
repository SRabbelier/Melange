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

"""Subversion commandline wrapper.

This module provides access to a restricted subset of the Subversion
commandline tool. The main functionality offered is an object wrapping
a working copy, providing version control operations within that
working copy.

A few standalone commands are also implemented to extract data from
arbitrary remote repositories.
"""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]


import error
import util


def export(url, revision, dest_path):
  """Export the contents of a repository to a local path.

  Note that while the underlying 'svn export' only requires a URL, 
  we require that both a URL and a revision be specified, to fully
  qualify the data to export.

  Args:
    url: The repository URL to export.
    revision: The revision to export.
    dest_path: The destination directory for the export. Note that
      this is an absolute path, NOT a working copy relative path.
    """
  assert os.path.isabs(dest_path)
  if os.path.exists(dest_path):
    raise error.ObstructionError('Cannot export to obstructed path %s' %
                                 dest_path)
  util.run(['svn', 'export', '-r', str(revision), url, dest_path])


def find_tag_rev(url):
  """Return the revision at which a remote tag was created.

  Since tags are immutable by convention, usually the HEAD of a tag
  should be the tag creation revision. However, mistakes can happen,
  so this function will walk the history of the given tag URL,
  stopping on the first revision that was created by copy.

  This detection is not foolproof. For example: it will be fooled by a
  tag that was created, deleted, and recreated by copy at a different
  revision. It is not clear what the desired behavior in these edge
  cases are, and no attempt is made to handle them. You should request
  user confirmation before using the result of this function.

  Args:
    url: The repository URL of the tag to examine.
  """
  try:
    output = util.run(['svn', 'log', '-q', '--stop-on-copy', url],
                      capture=True)
  except util.SubprocessFailed:
    raise error.ExpectationFailed('No tag at URL ' + url)
  first_rev_line = output[-2]
  first_rev = int(first_rev_line.split()[0][1:])
  return first_rev


def diff(url, revision):
  """Retrieve a revision from a remote repository as a unified diff.

  Args:
    url: The repository URL on which to perform the diff.
    revision: The revision to extract at the given url.

  Returns:
    A string containing the changes extracted from the remote
    repository, in unified diff format suitable for application using
    'patch'.
  """
  try:
    return util.run(['svn', 'diff', '-c', str(revision), url],
                    capture=True, split_capture=False)
  except util.SubprocessFailed:
    raise error.ExpectationFailed('Could not get diff for r%d '
                                  'from remote repository' % revision)


class WorkingCopy(util.Paths):
  """Wrapper for operations on a Subversion working copy.

  An instance of this class is bound to a specific working copy
  directory, and provides an API to perform various Subversion
  operations on this working copy.

  Some methods take a 'depth' argument. Depth in Subversion is a
  feature that allows the creation of arbitrarily shallow or deep
  working copies on a per-directory basis. Possible values are
  'none' (no files or directories), 'files' (only files in .),
  'immediates' (files and directories in ., directories checked out
  at depth 'none') or 'infinity' (a normal working copy with
  everything).

  Note that this wrapper also doubles as a Paths object, offering an
  easy way to get or check the existence of paths in the working
  copy.
  """

  def __init__(self, wc_dir):
    util.Paths.__init__(self, wc_dir)

  def _unknownAndMissing(self, path):
    """Returns lists of unknown and missing files in the working copy.

    Args:
      path: The working copy path to scan.

    Returns:
      Two lists. The first is a list of all unknown paths
      (subversion has no knowledge of them), the second is a list
      of missing paths (subversion knows about them, but can't
      find them). Paths in either list are relative to the input
      path.
    """
    assert self.exists()
    unknown = []
    missing = []
    for line in self.status(path):
      if not line.strip():
        continue
      if line[0] == '?':
        unknown.append(line[7:])
      elif line[0] == '!':
        missing.append(line[7:])
    return unknown, missing

  def checkout(self, url, depth='infinity'):
    """Check out a working copy from the given URL.

    Args:
      url: The Subversion repository URL to check out.
      depth: The depth of the working copy root.
    """
    assert not self.exists()
    util.run(['svn', 'checkout', '--depth=' + depth, url, self.path()])

  def update(self, path='', depth=None):
    """Update a working copy path, optionally changing depth.

    Args:
      path: The working copy path to update.
      depth: If set, change the depth of the path before updating.
    """
    assert self.exists()
    if depth is None:
      util.run(['svn', 'update', self.path(path)])
    else:
      util.run(['svn', 'update', '--set-depth=' + depth, self.path(path)])

  def revert(self, path=''):
    """Recursively revert a working copy path.

    Note that this command is more zealous than the 'svn revert'
    command, as it will also delete any files which subversion
    does not know about.
    """
    util.run(['svn', 'revert', '-R', self.path(path)])

    unknown, missing = self._unknownAndMissing(path)
    unknown = [os.path.join(self.path(path), p) for p in unknown]

    if unknown:
      # rm -rf makes me uneasy. Verify that all paths to be deleted
      # are within the release working copy.
      for p in unknown:
        assert p.startswith(self.path())

      util.run(['rm', '-rf', '--'] + unknown)

  def ls(self, dir=''):
    """List the contents of a working copy directory.

    Note that this returns the contents of the directory as seen
    by the server, not constrained by the depth settings of the
    local path.
    """
    assert self.exists()
    return util.run(['svn', 'ls', self.path(dir)], capture=True)

  def copy(self, src, dest):
    """Copy a working copy path.

    The copy is only scheduled for commit, not committed.

    Args:
      src: The source working copy path.
      dst: The destination working copy path.
    """
    assert self.exists()
    util.run(['svn', 'cp', self.path(src), self.path(dest)])

  def propget(self, prop_name, path):
    """Get the value of a property on a working copy path.

    Args:
      prop_name: The property name, eg. 'svn:externals'.
      path: The working copy path on which the property is set.
    """
    assert self.exists()
    return util.run(['svn', 'propget', prop_name, self.path(path)],
            capture=True)

  def propset(self, prop_name, prop_value, path):
    """Set the value of a property on a working copy path.

    The property change is only scheduled for commit, not committed.

    Args:
      prop_name: The property name, eg. 'svn:externals'.
      prop_value: The value that should be set.
      path: The working copy path on which to set the property.
    """
    assert self.exists()
    util.run(['svn', 'propset', prop_name, prop_value, self.path(path)])

  def add(self, paths):
    """Schedule working copy paths for addition.

    The paths are only scheduled for addition, not committed.

    Args:
      paths: The list of working copy paths to add.
    """
    assert self.exists()
    paths = [self.path(p) for p in paths]
    util.run(['svn', 'add'] + paths)

  def remove(self, paths):
    """Schedule working copy paths for deletion.

    The paths are only scheduled for deletion, not committed.

    Args:
      paths: The list of working copy paths to delete.
    """
    assert self.exists()
    paths = [self.path(p) for p in paths]
    util.run(['svn', 'rm'] + paths)

  def status(self, path=''):
    """Return the status of a working copy path.

    The status returned is the verbatim output of 'svn status' on
    the path.

    Args:
      path: The path to examine.
    """
    assert self.exists()
    return util.run(['svn', 'status', self.path(path)], capture=True)

  def addRemove(self, path=''):
    """Perform an "addremove" operation a working copy path.

    An "addremove" runs 'svn status' and schedules all the unknown
    paths (listed as '?') for addition, and all the missing paths
    (listed as '!') for deletion. Its main use is to synchronize
    working copy state after applying a patch in unified diff
    format.

    Args:
      path: The path under which unknown/missing files should be
        added/removed.
    """
    assert self.exists()
    unknown, missing = self._unknownAndMissing(path)
    if unknown:
      self.add(unknown)
    if missing:
      self.remove(missing)

  def commit(self, message, path=''):
    """Commit scheduled changes to the source repository.

    Args:
      message: The commit message to use.
      path: The path to commit.
    """
    assert self.exists()
    util.run(['svn', 'commit', '-m', message, self.path(path)])

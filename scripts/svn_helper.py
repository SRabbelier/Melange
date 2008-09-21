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

"""Helper functions that wrap the pysvn Python svn bindings.

ls(): returns list of selected directory entries from an SVN repository
lsDirs(): wrapper around ls() that only returns node_kind.dir entries
lsFiles(): wrapper around ls() that only returns node_kind.files entries
exists(): returns True if repo_path exists in the svn repository

PYSVN_ALL_NODE_KINDS: all directory entry node_kinds supported by pysvn
PYSVN_FILE_DIR_NODE_KINDS: actual file and directory node_kinds

This module requires that the pysvn module be installed.
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import os
import pysvn

# top level script needs to use a relative import
import settings


#: all of the directory entry node_kinds supported py pysvn
PYSVN_ALL_NODE_KINDS = set([pysvn.node_kind.none, pysvn.node_kind.dir,
                            pysvn.node_kind.file, pysvn.node_kind.unknown])

#: actual file and directory node_kinds (includes dir and file, but excludes
#: the "non-file" none and unknown)
PYSVN_FILE_DIR_NODE_KINDS = set([pysvn.node_kind.dir, pysvn.node_kind.file])


# pysvn Client object initialized lazily the first time getPySvnClient()
# is called.
_client = None


def getPySvnClient():
  """Returns the module-global pysvn Client object (creating one if needed).

  Lazily initializes a global pysvn Client object, returning the same one
  once it exists.
  """
  global _client

  if not _client:
    _client = pysvn.Client()

  return _client


def formatDirPath(path):
  """Appends trailing separator to non-empty path if it is missing.

  Args:
    path:  path string, which may be with or without a trailing separator,
      or even empty or None

  Returns:
    path unchanged if path evaluates to False or already ends with a trailing
    separator; otherwise, a / separator is appended
  """
  if path and not path.endswith('/'):
    path = path + '/'
  return path


def formatDirPaths(*args):
  """Apply formatDirPath() to all supplied arguments, returning them in order.
  """
  return tuple([formatDirPath(arg) for arg in args])


def getCanonicalSvnPath(path):
  """Returns the supplied svn repo path *without* the trailing / character.

  Some pysvn methods raise exceptions if svn directory URLs end with a
  trailing / ("non-canonical form") and some do not.  Go figure...
  """
  if path and path.endswith('/'):
    path = path[:-1]
  return path


def useLocalOsSep(path):
  """Return path with all / characters replaced with os.sep, to be OS-agnostic.

  Args:
    path: an SVN path (either working copy path or relative path, but not a
      full repository URL) that uses the canonical / separators
  """
  return path.replace('/', os.sep)


def getExpandedWorkingCopyPath(path, wc_root=None):
  """Returns expanded, local, native filesystem working copy path.

  Args:
    path: path to expand and convert to local filesystem directory separators
    wc_root: if present, prepended to path first
  """
  path = useLocalOsSep(path)

  if wc_root:
    # prepend (Windows-compatible) working copy root if one was supplied
    path = os.path.join(useLocalOsSep(wc_root), path)

  path = settings.getExpandedPath(path)

  if not path.endswith(os.sep):
    path = path + os.sep

  return path


def encodeRevision(rev):
  """Encode supplied revision into a pysvn.Revision instance.

  This function is currently very simplistic and does not produce all possible
  types of pysvn.Revision object.  See below for current limitations.

  Args:
    rev: integer revision number or None

  Returns:
    HEAD pysvn.Revision object if rev is None,
    otherwise a pysvn.opt_revision_kind.number pysvn.Revision object created
    using the supplied integer revision number
  """
  if rev is None:
    return pysvn.Revision(pysvn.opt_revision_kind.head)

  return pysvn.Revision(pysvn.opt_revision_kind.number, int(rev))


def ls(repo_path, client=None, keep_kinds=PYSVN_FILE_DIR_NODE_KINDS, **kwargs):
  """Returns a list of (possibly recursive) svn repo directory entries.

  Args:
    repo_path: absolute svn repository path URL, including the server and
      directory path within the repo
    client: pysvn Client instance; default is None, which will use the pysvn
      Client created by first call to getPySvnClient() (or create one if
      necessary)
    keep_kinds: types of directory entries to keep in the returned list; a
      collection of pysvn.node_kind objects; default is
      PYSVN_FILE_DIR_NODE_KINDS
    **kwargs: keyword arguments passed on to Client.list(), including:
      recurse: indicates if return results should include entries from
        subdirectories of repo_path as well; default is False

  Returns:
    list of (Unicode, coming from pysvn) strings representing the entries
    of types indicated by keep_kinds; strings are altered to match the
    output of the actual 'svn ls' command: repo_path prefix is removed,
    directories end with the / separator.
  """
  if not client:
    client = getPySvnClient()

  raw_entries = client.list(repo_path, **kwargs)
  entries = []

  # Find shortest repos_path that is a 'dir' entry; will be prefix of all
  # other entries, since Client.list() always returns repo_path as one of
  # the entries.  It is easier and more reliable to do this search than to
  # try to manipulate repo_path into the prefix (since the user could supply
  # any number of valid, but different, formats).
  shortest_path = raw_entries[0][0].repos_path

  for svn_list, _ in raw_entries:
    if svn_list.kind == pysvn.node_kind.dir:
      entry_path = svn_list.repos_path

      if len(entry_path) < len(shortest_path):
        shortest_path = entry_path

  # normalize the path name of entry_prefix to include a trailing separator
  entry_prefix = formatDirPath(shortest_path)

  for svn_list,_ in raw_entries:
    # only include requested node kinds (dir, file, etc.)
    if svn_list.kind not in keep_kinds:
      continue

    entry_path = svn_list.repos_path

    # omit the repo_path directory entry itself (simiilar to omitting '.' as
    # is done by the actual 'svn ls' command)
    if entry_path == shortest_path:
      continue

    # all entry_paths except for the shortest should start with that
    # shortest entry_prefix, so assert that and remove the prefix
    assert entry_path.startswith(entry_prefix)
    entry_path = entry_path[len(entry_prefix):]

    # normalize directory entry_paths to include a trailing separator
    if ((svn_list.kind == pysvn.node_kind.dir)
        and (not entry_path.endswith('/'))):
      entry_path = entry_path + '/'

    entries.append(entry_path)

  return entries


def lsDirs(repo_path, **kwargs):
  """Wrapper around ls() that only returns node_kind.dir entries.
  """
  return ls(repo_path, keep_kinds=(pysvn.node_kind.dir,), **kwargs)


def lsFiles(repo_path, **kwargs):
  """Wrapper around ls() that only returns node_kind.files entries.
  """
  return ls(repo_path, keep_kinds=(pysvn.node_kind.file,), **kwargs)


def exists(repo_path, client=None):
  """Returns True if repo_path exists in the svn repository."""
  if not client:
    client = getPySvnClient()

  try:
    raw_entries = client.list(repo_path)
    return True
  except pysvn._pysvn.ClientError:
    # Client.list() raises an exception if the path is not present in the repo
    return False


def branchItems(src, dest, items, rev=None, client=None):
  """Branch a list of items (files and/or directories).

  Using the supplied pysvn client object, a list of items (expected to be
  present in the src directory) is branched from the absolute svn repo src
  path URL to the relative working client dest directory.

  Args:
    src: absolute svn repository source path URL, including the server and
      directory path within the repo
    dest: relative svn repository destination path in the current working copy
    items: list of relative paths of items in src/ to branch to dest/ (no item
      should begin with the / separator)
    client: pysvn Client instance; default is None, which will use the pysvn
      Client created by first call to getPySvnClient() (or create one if
      necessary)
  """
  if not client:
    client = getPySvnClient()

  src = formatDirPath(src)
  dest = useLocalOsSep(formatDirPath(dest))

  for item in items:
    assert not item.startswith('/')
    src_item = getCanonicalSvnPath(src + item)
    # attempt to be compatible with Windows working copy paths
    item = useLocalOsSep(item)
    client.copy(src_item, dest + item, src_revision=encodeRevision(rev))


def branchDir(src, dest, client=None, rev=None):
  """Branch one directory to another.

  Using the supplied pysvn client object, the absolute svn repo path URL src
  directory is branched to the relative working client dest directory.

  Args:
    src: absolute svn repository source path URL, including the server and
      directory path within the repo
    dest: relative svn repository destination path in the current working copy
    client: pysvn Client instance; default is None, which will use the pysvn
      Client created by first call to getPySvnClient() (or create one if
      necessary)
  """
  if not client:
    client = getPySvnClient()

  src = getCanonicalSvnPath(src)
  dest = useLocalOsSep(formatDirPath(dest))

  client.copy(src, dest, src_revision=encodeRevision(rev))


def exportItems(src, dest, items, rev=None, client=None):
  """Export a list of items (files and/or directories).

  Using the supplied pysvn client object, a list of items (expected to be
  present in the src directory) is exported from the absolute svn repo src
  path URL to the local filesystem directory.

  Args:
    src: absolute svn repository source path URL, including the server and
      directory path within the repo
    dest: local filesystem destination path
    items: list of relative paths of items in src/ to export to dest/ (no item
      should begin with the / separator)
    client: pysvn Client instance; default is None, which will use the pysvn
      Client created by first call to getPySvnClient() (or create one if
      necessary)
  """
  if not client:
    client = getPySvnClient()

  src = formatDirPath(src)
  dest = useLocalOsSep(formatDirPath(dest))

  for item in items:
    assert not item.startswith('/')
    src_item = getCanonicalSvnPath(src + item)
    # attempt to be compatible with Windows local filesystem paths
    dest_item = useLocalOsSep(getCanonicalSvnPath(dest + item))
    client.export(src_item, dest_item, revision=encodeRevision(rev))


def exportDir(src, dest, client=None, rev=None):
  """Export one directory to another.

  Using the supplied pysvn client object, the absolute svn repo path URL src
  directory is exported to the the local filesystem directory.

  Args:
    src: absolute svn repository source path URL, including the server and
      directory path within the repo
    dest: local filesystem destination path
    client: pysvn Client instance; default is None, which will use the pysvn
      Client created by first call to getPySvnClient() (or create one if
      necessary)
  """
  if not client:
    client = getPySvnClient()

  src = getCanonicalSvnPath(src)
  dest = useLocalOsSep(getCanonicalSvnPath(dest))

  client.export(src, dest, revision=encodeRevision(rev))

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

DEF_SVN_REPO: default HTTPS path to the SoC project SVN repo
PYSVN_ALL_NODE_KINDS: all directory entry node_kinds supported by pysvn
PYSVN_FILE_DIR_NODE_KINDS: actual file and directory node_kinds
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import pysvn


#: default HTTPS path to the SoC project SVN repo
DEF_SVN_REPO = 'https://soc.googlecode.com/svn/'

#: all of the directory entry node_kinds supported py pysvn
PYSVN_ALL_NODE_KINDS = set([pysvn.node_kind.none, pysvn.node_kind.dir,
                            pysvn.node_kind.file, pysvn.node_kind.unknown])

#: actual file and directory node_kinds (includes dir and file, but excludes
#: the "non-file" none and unknown)
PYSVN_FILE_DIR_NODE_KINDS = set([pysvn.node_kind.dir, pysvn.node_kind.file])


def ls(client, repo_path, keep_kinds=PYSVN_FILE_DIR_NODE_KINDS, **kwargs):
  """Returns a list of (possibly recursive) svn repo directory entries.

  Args:
    client: pysvn Client instance
    repo_path: absolute svn repository path URL, including the server and
      directory path within the repo
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
  entry_prefix = shortest_path

  if not entry_prefix.endswith('/'):
    entry_prefix = entry_prefix + '/'

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


def lsDirs(client, repo_path, **kwargs):
  """Wrapper around ls() that only returns node_kind.dir entries.
  """
  return ls(client, repo_path, keep_kinds=(pysvn.node_kind.dir,), **kwargs)


def lsFiles(client, repo_path, **kwargs):
  """Wrapper around ls() that only returns node_kind.files entries.
  """
  return ls(client, repo_path, keep_kinds=(pysvn.node_kind.file,), **kwargs)


def exists(client, repo_path):
  """Returns True if repo_path exists in the svn repository."""
  try:
    raw_entries = client.list(repo_path)
    return True
  except pysvn._pysvn.ClientError:
    # Client.list() raises an exception if the path is not present in the repo
    return False

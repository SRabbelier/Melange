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

"""Path and link ID manipulation functions.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import re


# start with ASCII digit or lowercase
#   (additional ASCII digit or lowercase
#     -OR-
#   underscore and ASCII digit or lowercase)
#     zero or more of OR group
LINK_ID_PATTERN_CORE = r'[0-9a-z](?:[0-9a-z]|_[0-9a-z])*'
LINK_ID_ARG_PATTERN = r'(?P<link_id>%s)' % LINK_ID_PATTERN_CORE
LINK_ID_PATTERN = r'^%s$' % LINK_ID_PATTERN_CORE
LINK_ID_REGEX = re.compile(LINK_ID_PATTERN)

# scope path is multiple link_id chunks,
# each separated by a trailing /
# (at least 1)
SCOPE_PATH_ARG_PATTERN = (r'(?P<scope_path>%(link_id)s'
                             '(?:/%(link_id)s)*)' % {
                               'link_id': LINK_ID_PATTERN_CORE})
SCOPE_PATH_PATTERN = r'^%s$' % SCOPE_PATH_ARG_PATTERN
SCOPE_PATH_REGEX = re.compile(SCOPE_PATH_PATTERN)

# path is multiple link_id chunks,
#   each separated by a trailing /
#     (at least 1)
# followed by a single link_id with no trailing /
PATH_LINK_ID_ARGS_PATTERN = (
    r'%(scope_path)s/'
     '(?P<link_id>%(link_id)s)' % {
       'scope_path' : SCOPE_PATH_ARG_PATTERN,
       'link_id': LINK_ID_PATTERN_CORE})
PATH_LINK_ID_PATTERN = r'^%s$' % PATH_LINK_ID_ARGS_PATTERN
PATH_LINK_ID_REGEX = re.compile(PATH_LINK_ID_PATTERN)


def getPartsFromPath(path):
  """Splits path string into scope_path and link_id.
  
  Returns:
    {'scope_path': 'everything/but',
     'link_id': 'link_id'}
    or {} (empty dict) if string did not match PATH_LINK_ID_PATTERN.
  """
  path_link_name_match = PATH_LINK_ID_REGEX.match(path)
  
  if not path_link_name_match:
    return {}

  return path_link_name_match.groupdict()


def combinePath(path_parts):
  """Returns path components combined into a single string.
  
  Args:
    path_parts: a single path string, or a list of path part strings,
      or a nested list of path part strings (where the zeroeth element in
      the list is itself a list); for example:
        'a/complete/path/in/one/string'
        ['some', 'path', 'parts']
        [['path', 'parts', 'and', 'a'], 'link ID']

  Returns:
    None if path_parts is False (None, empty string, etc.) or if
    any list elements are False (an empty list, empty string, etc.);
    otherwise, the combined string with the necessary separators.
  """
  if not path_parts:
    # completely empty input, so return early
    return None

  if not isinstance(path_parts, (list, tuple)):
    # a single path string, so just return it as-is (nothing to do)
    return path_parts
  
  flattened_parts = []
  
  for part in path_parts:
    if not part:
      # encountered a "False" element, which invalidates everything else
      return None    
  
    if isinstance(part, (list, tuple)):
      flattened_parts.extend(part)
    else:
      flattened_parts.append(part)

  return '/'.join(flattened_parts)

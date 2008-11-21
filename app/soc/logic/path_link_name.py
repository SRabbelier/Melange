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

from soc.models import linkable


def getPartsFromPath(path):
  """Splits path string into scope_path and link_id.
  
  Returns:
    {'scope_path': 'everything/but',
     'link_id': 'link_id'}
    or {} (empty dict) if string did not match PATH_LINK_ID_PATTERN.
  """
  path_link_name_match = linkable.PATH_LINK_ID_REGEX.match(path)
  
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

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

"""Common helper functions.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import re


LINKNAME_PATTERN = r'''(?x)
    ^
    [0-9a-z]   # start with ASCII digit or lowercase
    (
     [0-9a-z]  # additional ASCII digit or lowercase
     |         # -OR-
     _[0-9a-z] # underscore and ASCII digit or lowercase
    )*         # zero or more of OR group
    $
'''

LINKNAME_REGEX = re.compile(LINKNAME_PATTERN)

def isLinkNameFormatValid(link_name):
  """Returns True if link_name is in a valid format.

  Args:
    link_name: link name used in URLs for identification
  """
  if LINKNAME_REGEX.match(link_name):
    return True
  return False
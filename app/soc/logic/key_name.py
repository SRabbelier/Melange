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

"""Functions for composing Model entity key names.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


# start with ASCII digit or lowercase
#   (additional ASCII digit or lowercase
#     -OR-
#   underscore and ASCII digit or lowercase)
#     zero or more of OR group
LINKNAME_PATTERN_CORE = r'[0-9a-z](?:[0-9a-z]|_[0-9a-z])*'

LINKNAME_PATTERN = r'^%s$' % LINKNAME_PATTERN_CORE
LINKNAME_ARG_PATTERN = r'(?P<linkname>%s)' % LINKNAME_PATTERN_CORE


# partial path is multiple linkname chunks,
#   each separated by a trailing /
#     (at least 1)
# followed by a single linkname with no trailing /
WORK_PATH_LINKNAME_ARGS_PATTERN = (
    r'(?P<partial_path>%(linkname)s(?:/%(linkname)s)*)/'
     '(?P<linkname>%(linkname)s)' % {
        'linkname': LINKNAME_PATTERN_CORE})

WORK_PATH_LINKNAME_PATTERN = r'^%s$' % WORK_PATH_LINKNAME_ARGS_PATTERN


class Error(Exception):
  """Base class for all exceptions raised by this module."""
  pass


def getFullClassName(cls):
  """Returns fully-qualified module.class name string.""" 
  return '%s.%s' % (cls.__module__, cls.__name__) 


def combinePath(path_parts):
  """Returns path components combined into a single string.
  
  Args:
    path_parts: a single path string, or a list of path part strings,
      or a nested list of path part strings (where the zeroeth element in
      the list is itself a list); for example:
        'a/complete/path/in/one/string'
        ['some', 'path', 'parts']
        [['path', 'parts', 'and', 'a'], 'link name']

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


def nameDocument(partial_path, link_name=None):
  """Returns a Document key name constructed from a path and link name.
    
  Args:
    partial_path: the first portion of the path to the Document that uniquely
      identifies it
    link_name: optional link name to append to path (when omitted,
      partial_path is actually the entire path, with the link_name already
      appended)

  Raises:
    Error if partial_path and link_Name produce a "False" path (None,
    empty string, etc.)
  """
  path = [partial_path]
  
  if link_name:
    path.append(link_name)

  path = combinePath(path)

  if not path:
    raise Error('"path" must be non-False: "%s"' % path)

  return 'Document:%s' % path


def nameSiteSettings(path):
  """Returns a SiteSettings key name constructed from a supplied path.
  
  Raises:
    Error if path is "False" (None, empty string, etc.)
  """
  if not path:
    raise Error('"path" must be non-False: "%s"' % path)

  return 'SiteSettings:%s' % path


def nameUser(email):
  """Returns a User key name constructed from a supplied email address.
  
  Raises:
    Error if email is "False" (None, empty string, etc.)
  """
  if not email:
    raise Error('"email" must be non-False: "%s"' % email)

  return 'User:%s' % email


def nameSponsor(link_name):
  """Returns a Sponsor key name constructed from a supplied link name.

  Raises:
    Error if link_name is "False" (None, empty string, etc.)
  """
  if not link_name:
    raise Error('"link_name" must be non-False: "%s"' % link_name)

  return 'Group/Sponsor:%s' % link_name


def nameSchool(sponsor_ln, program_ln, link_name):
  """Returns a School key name constructed from link names.
     
  Args:
    sponsor_ln: Sponsor link name
    program_ln: Program link name
    link_name: School link name

  Raises:
    Error if sponsor_ln, program_ln, and link_Name combine to produce
    a "False" path (None, empty string, etc.)
  """
  path = combinePath([[sponsor_ln, program_ln], link_name])
  
  if not path:
    raise Error('"path" must be non-False: "%s"' % path)
  
  return 'Group/School:%s' % path


def nameOrganization(sponsor_ln, program_ln, link_name):
  """Returns a Organization key name constructed from link names.
     
  Args:
    sponsor_ln: Sponsor link name
    program_ln: Program link name
    link_name: Organization link name

  Raises:
    Error if sponsor_ln, program_ln, and link_Name combine to produce
    a "False" path (None, empty string, etc.)
  """
  path = combinePath([[sponsor_ln, program_ln], link_name])
  
  if not path:
    raise Error('"path" must be non-False: "%s"' % path)
  
  return 'Group/Organization:%s' % path 


def nameClub(link_name):
  """Returns a Club key name constructed from a supplied link name.

  Raises:
    Error if link_name is "False" (None, empty string, etc.)
  """
  if not link_name:
    raise Error('"link_name" must be non-False: "%s"' % link_name)

  return 'Group/Club:%s' % link_name

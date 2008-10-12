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


from soc.logic import path_link_name


class Error(Exception):
  """Base class for all exceptions raised by this module."""
  pass


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

  path = path_link_name.combinePath(path)

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
  path = path_link_name.combinePath([[sponsor_ln, program_ln], link_name])
  
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
  path = path_link_name.combinePath([[sponsor_ln, program_ln], link_name])
  
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


def nameWork(link_name):
  """Placeholder for work namer"""

  if not link_name:
    raise Error('"link_name" must be non-False: "%s"' % link_name)

  return 'Work:%s' % link_name


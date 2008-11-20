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


def nameDocument(scope_path, link_id=None):
  """Returns a Document key name constructed from a path and link ID.
    
  Args:
    scope_path: the first portion of the path to the Document that uniquely
      identifies it
    link_id: optional link ID to append to path (when omitted,
      scope_path is actually the entire path, with the link_id already
      appended)

  Raises:
    Error if scope_path and link_id produce a "False" path (None,
    empty string, etc.)
  """
  path = [scope_path]
  
  if link_id:
    path.append(link_id)

  path = path_link_name.combinePath(path)

  if not path:
    raise Error('"path" must be non-False: "%s"' % path)

  return 'Document:%s' % path


def nameSiteSettings(scope_path, link_id):
  """Returns a SiteSettings key name constructed from a supplied path.
  
  Raises:
    Error if path is "False" (None, empty string, etc.)
  """

  if not scope_path:
    raise Error('"scope_path" must be non-False: "%s"' % scope_path)

  if not link_id:
    raise Error('"link_id" must be non-False: "%s"' % link_id)

  return 'SiteSettings:%s:%s' % (scope_path, link_id)


def nameHomeSettings(scope_path, link_id):
  """Returns a HomeSettings key name constructed from a supplied path.

  Raises:
    Error if path is "False" (None, empty string, etc.)
  """

  if not scope_path:
    raise Error('"scope_path" must be non-False: "%s"' % scope_path)

  if not link_id:
    raise Error('"link_id" must be non-False: "%s"' % link_id)

  return 'HomeSettings:%s:%s' % (scope_path, link_id)


def nameUser(email):
  """Returns a User key name constructed from a supplied email address.
  
  Raises:
    Error if email is "False" (None, empty string, etc.)
  """
  if not email:
    raise Error('"email" must be non-False: "%s"' % email)

  return 'User:%s' % email


def nameSponsor(link_id):
  """Returns a Sponsor key name constructed from a supplied link ID.

  Raises:
    Error if link_id is "False" (None, empty string, etc.)
  """
  if not link_id:
    raise Error('"link_id" must be non-False: "%s"' % link_id)

  return 'Group/Sponsor:%s' % link_id


def nameSchool(sponsor_ln, program_ln, link_id):
  """Returns a School key name constructed from link IDs.
     
  Args:
    sponsor_ln: Sponsor link ID
    program_ln: Program link ID
    link_id: School link ID

  Raises:
    Error if sponsor_ln, program_ln, and link_id combine to produce
    a "False" path (None, empty string, etc.)
  """
  path = path_link_name.combinePath([[sponsor_ln, program_ln], link_id])
  
  if not path:
    raise Error('"path" must be non-False: "%s"' % path)
  
  return 'Group/School:%s' % path


def nameOrganization(sponsor_ln, program_ln, link_id):
  """Returns a Organization key name constructed from link IDs.
     
  Args:
    sponsor_ln: Sponsor link ID
    program_ln: Program link ID
    link_id: Organization link ID

  Raises:
    Error if sponsor_ln, program_ln, and link_id combine to produce
    a "False" path (None, empty string, etc.)
  """
  path = path_link_name.combinePath([[sponsor_ln, program_ln], link_id])
  
  if not path:
    raise Error('"path" must be non-False: "%s"' % path)
  
  return 'Group/Organization:%s' % path 


def nameClub(link_id):
  """Returns a Club key name constructed from a supplied link ID.

  Raises:
    Error if link_id is "False" (None, empty string, etc.)
  """
  if not link_id:
    raise Error('"link_id" must be non-False: "%s"' % link_id)

  return 'Group/Club:%s' % link_id


def nameWork(link_id):
  """Placeholder for work namer.
  """

  if not link_id:
    raise Error('"link_id" must be non-False: "%s"' % link_id)

  return 'Work:%s' % link_id


def nameHost(sponsor_ln, user_ln):
  """Placeholder for host namer.
  """

  if not sponsor_ln:
    raise Error('"sponsor_ln" must be non-False: "%s"' % sponsor_ln)

  if not user_ln:
    raise Error('"user_ln" must be non-False: "%s"' % user_ln)

  return 'Host:%s:%s' % (sponsor_ln, user_ln)

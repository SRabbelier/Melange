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


import soc.models.club
import soc.models.group
import soc.models.organization
import soc.models.school
import soc.models.sponsor
import soc.models.document
import soc.models.site_settings
import soc.models.user


def nameSiteSettings(path):
  """Returns a SiteSettings key name constructed from a supplied path."""
  return '%(type)s:%(path)s' % {
      'type': soc.models.site_settings.SiteSettings.__name__,
      'path': path,
      }


def nameDocument(path, link_name):
  """Returns a Document key name constructed from a path and link name."""
  return '%(type)s:%(path)s/%(link_name)s' % {
      'type': soc.models.document.Document.__name__,
      'path': path,
      'link_name': link_name,
      }


def nameUser(email):
  """Returns a User key name constructed from a supplied email address."""
  return '%(type)s:%(email)s' % {
      'type': soc.models.user.User.__name__,
      'email': email,
      }


def nameSponsor(link_name):
  """Returns a Sponsor key name constructed from a supplied link name."""
  return '%(group)s/%(type)s:%(link_name)s' % {
      'group': soc.models.group.Group.__name__,
      'type': soc.models.sponsor.Sponsor.__name__,
      'link_name': link_name,
      }


def nameSchool(sponsor_ln, program_ln, link_name):
  """Returns a School key name constructed from a supplied sponsor,
     program and school link names.
  """
  return '%(group)s/%(type)s:%(sponsor)s/%(program)s/%(link_name)s' % {
      'group': soc.models.group.Group.__name__,
      'type': soc.models.school.School.__name__,
      'sponsor': sponsor_ln,
      'program': program_ln,
      'link_name': link_name,
      }


def nameOrganization(sponsor_ln, program_ln, link_name):
  """Returns a Organization key name constructed from a supplied sponsor,
     program and organization link names.
  """
  return '%(group)s/%(type)s:%(sponsor)s/%(program)s/%(link_name)s' % {
      'group': soc.models.group.Group.__name__,
      'type': soc.models.organization.Organization.__name__,
      'sponsor': sponsor_ln,
      'program': program_ln,
      'link_name': link_name,
      }


def nameClub(link_name):
  """Returns a Club key name constructed from a supplied link name."""
  return '%(group)s/%(type)s:%(link_name)s' % {
      'group': soc.models.group.Group.__name__,
      'type': soc.models.sponsor.Sponsor.__name__,
      'link_name': link_name,
      }
  
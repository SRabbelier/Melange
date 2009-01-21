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

"""Redirect related methods.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.ext import db


def getInviteRedirect(entity, params):
  """Returns the invitation redirect for the specified entity.
  """

  result ='/%s/invite/%s' % (
      params['url_name'], entity.key().name())

  return result


def getCreateRedirect(entity, params):
  """Returns the create program redirect for the specified entity.
  """

  result ='/%s/create/%s' % (
      params['url_name'], entity.key().name())

  return result


def getEditRedirect(entity, params):
  """Returns the edit redirect for the specified entity.
  """

  return '/%s/edit/%s' % (
      params['url_name'], entity.key().name())


def getPublicRedirect(entity, params):
  """Returns the public redirect for the specified entity.
  """

  return '/%s/show/%s' % (
      params['url_name'], entity.key().name())


def getExportRedirect(entity, params):
  """Returns the export redirect for the specified entity.
  """

  return '/%s/export/%s' % (
      params['url_name'], entity.key().name())


def getReviewRedirect(entity, params):
  """Returns the redirect to review the specified entity
  """
  
  return '/%s/review/%s' % (
      params['url_name'], entity.link_id)


def getCreateRequestRedirect(entity, params):
  """Returns the create request redirect for the specified entity.
  """

  result ='/request/create/%s/%s/%s' % (
      params['group_scope'], params['url_name'], entity.key().name())

  return result


def inviteAcceptedRedirect(entity, _):
  """Returns the redirect for accepting an invite.
  """

  return '/%s/create/%s/%s' % (
      entity.role, entity.scope_path, entity.link_id)


def getApplicantRedirect(entity, params):
  """Returns the redirect for processing accepted Applications.
  """

  return '/%s/applicant/%s' % (
      params['url_name'], entity.link_id)


def getToSRedirect(presence):
  """Returns link to 'show' the ToS Document if it exists, None otherwise.

  Args:
    presence: Presence entity that may or may not have a tos property
  """
  if not presence:
    return None

  try:
    tos_doc = presence.tos
  except db.Error:
    return None

  if not tos_doc:
    return None

  return getPublicRedirect(tos_doc, {'url_name': 'document'})

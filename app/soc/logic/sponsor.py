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

"""Sponsor (Model) query functions.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic import key_name
from soc.logic import out_of_band

import soc.models.sponsor
import soc.logic.model


def doesLinkNameExist(link_name=None):
  """Returns True if link name exists in the Datastore.

  Args:
    link_name: link name used in URLs to identify Sponsor
  """
  if getSponsorFromLinkName(link_name):
    return True
  else:
    return False


def getSponsorFromLinkName(link_name):
  """Returns Sponsor entity for a given link name, or None if not found.  
    
  Args:
    link_name: a link name of the Sponsor that uniquely identifies it
  """
  # lookup by Sponsor key name
  sponsor_key_name = getSponsorKeyNameForLinkName(link_name)
  
  if key_name:
    sponsor = soc.models.sponsor.Sponsor.get_by_key_name(sponsor_key_name)
  else:
    sponsor = None
  
  return sponsor


def getSponsorIfLinkName(link_name=None):
  """Returns Sponsor entity for supplied link name if one exists.

  Args:
    link_name: a link name of the Sponsor that uniquely identifies it

  Returns:
    * None if link name is false.
    * Sponsor entity for supplied linkname

  Raises:
    out_of_band.ErrorResponse if link name is not false, but no Sponsor entity
    with the supplied link name exists in the Datastore
  """
  if not link_name:
    # exit without error, to let view know that link_name was not supplied
    return None

  linkname_sponsor = getSponsorFromLinkName(link_name=link_name)

  if linkname_sponsor:
    # a Sponsor exist for this linkname, so return that Sponsor entity
    return linkname_sponsor

  # else: a linkname was supplied, but there is no Sponsor that has it
  raise out_of_band.ErrorResponse(
      'There is no sponsor with a "link name" of "%s".' % link_name, status=404)


def getSponsorKeyNameForLinkName(link_name):
  """Return a Datastore key_name for a Sponsor from the link name.
  
  Args:
    link_name: a link name of the Sponsor that uniquely identifies it
  """
  if not link_name:
    return None

  return key_name.nameSponsor(link_name)


def getSponsorsForOffsetAndLimit(offset=0, limit=0):
  """Returns Sponsors entities for given offset and limit or None if not found.

  Args:
    offset: offset in entities list which defines first entity to return
    limit: max amount of entities to return
  """
  query = soc.models.sponsor.Sponsor.all()
  
  # Fetch one more to see if there should be a 'next' link
  return query.fetch(limit+1, offset)


def updateOrCreateSponsorFromLinkName(sponsor_link_name, **sponsor_properties):
  """Update existing Sponsor entity, or create new one with supplied properties.

  Args:
    sponsor_name: a linkname of the Sponsor that uniquely identifies it
    **sponsor_properties: keyword arguments that correspond to Sponsor entity
      properties and their values

  Returns:
    the Sponsor entity corresponding to the path, with any supplied
    properties changed, or a new Sponsor entity now associated with the 
    supplied path and properties.
  """
  # attempt to retrieve the existing Sponsor
  sponsor = getSponsorFromLinkName(sponsor_link_name)

  if not sponsor:
    # sponsor did not exist, so create one in a transaction
    sponsor_key_name = getSponsorKeyNameForLinkName(sponsor_link_name)
    sponsor = soc.models.sponsor.Sponsor.get_or_insert(
      sponsor_key_name, **sponsor_properties)

  # there is no way to be sure if get_or_insert() returned a new Sponsor or
  # got an existing one due to a race, so update with sponsor_properties anyway,
  # in a transaction
  return soc.logic.model.updateModelProperties(sponsor, **sponsor_properties)
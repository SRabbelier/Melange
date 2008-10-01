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

"""Document (Model) query functions.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import re

from google.appengine.ext import db

from soc.logic import key_name
from soc.logic import out_of_band
from soc.logic.site import id_user

import soc.logic.model

import soc.models.document
import soc.models.work

 
WORK_PATH_LINKNAME_REGEX = re.compile(key_name.WORK_PATH_LINKNAME_PATTERN)

def getPartsFromPath(path):
  """Splits path string into partial_path and link_name.
  
  Returns:
    {'partial_path': 'everything/but',
     'link_name': 'link_name'}
    or {} (empty dict) if string did not match WORK_PATH_LINKNAME_PATTERN.
  """
  path_linkname_match = WORK_PATH_LINKNAME_REGEX.match(path)
  
  if not path_linkname_match:
    return {}

  return path_linkname_match.groupdict()


def getDocument(path, link_name=None):
  """Returns Document entity for a given path, or None if not found.  
    
  Args:
    path: a request path of the Document that uniquely identifies it
    link_name: optional link name to append to path (when supplied,
      path is actually a "partial path" that needs to link name appended
      to it)
  """
  # lookup by Doc:path key name
  name = key_name.nameDocument(path, link_name=link_name)
  
  if name:
    document = soc.models.document.Document.get_by_key_name(name)
  else:
    document = None
  
  return document


def getDocumentIfPath(path, link_name=None):
  """Returns Document entity for supplied path if one exists.
  
  Args:
    path: path used in URLs to identify document

  Returns:
    * None if path is false.
    * Document entity that has supplied path

  Raises:
    out_of_band.ErrorResponse if path is not false, but no Document entity
    with the supplied path exists in the Datastore
  """
  if not path:
    # exit without error, to let view know that link_name was not supplied
    return None

  path_doc = getDocument(path, link_name=link_name)
    
  if path_doc:
    # a Document has this path, so return that corresponding Document entity
    return path_doc

  # else: a path was supplied, but there is no Document that has it
  raise out_of_band.ErrorResponse(
      'There is no document with a "path" of "%s".' % path, status=404)


def updateOrCreateDocument(**document_properties):
  """Update existing Document entity, or create new one with supplied properties.

  Args:
    path: a request path of the Document that uniquely identifies it
    **document_properties: keyword arguments that correspond to Document entity
      properties and their values

  Returns:
    the Document entity corresponding to the path, with any supplied
    properties changed, or a new Document entity now associated with the 
    supplied path and properties.
  """
  # attempt to retrieve the existing Document
  document = getDocument(document_properties['partial_path'],
                         link_name=document_properties['link_name'])

  if not document:
    # document did not exist, so create one in a transaction
    name = key_name.nameDocument(document_properties['partial_path'],
                                 document_properties['link_name'])
    document = soc.models.document.Document.get_or_insert(
        name, **document_properties)

  # there is no way to be sure if get_or_insert() returned a new Document or
  # got an existing one due to a race, so update with document_properties anyway,
  # in a transaction
  return soc.logic.model.updateModelProperties(document, **document_properties)


def getWorksForOffsetAndLimit(offset=0, limit=0, cls=soc.models.work.Work):
  """Returns Works for given offset and limit or None if not found.
    
  Args:
    offset: offset in entities list which defines first entity to return
    limit: max amount of entities to return
    cls: Model class of items to return (including sub-classes of that type);
      default is Work
  """
  query = db.GqlQuery(
      'SELECT * FROM Work WHERE inheritance_line = :1 ORDER BY title',
      key_name.getFullClassName(cls))

  # Fetch one more to see if there should be a 'next' link
  return query.fetch(limit+1, offset)  

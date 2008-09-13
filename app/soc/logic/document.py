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

from google.appengine.ext import db

import soc.models.document
import soc.logic.model

def getDocumentFromPath(path):
  """Returns Document entity for a given path, or None if not found.  
    
  Args:
    id: a Google Account (users.User) object
  """
  # lookup by Doc:path key name
  key_name = getDocumentKeyNameForPath(path)
  
  if key_name:
    document = soc.models.document.Document.get_by_key_name(key_name)
  else:
    document = None
  
  return document

def getDocumentKeyNameForPath(path):
  """Return a Datastore key_name for a Document from the path.
  
  Args:
    path: a request path of the Document that uniquely identifies it
  """
  if not path:
    return None

  return 'Doc:%s' % path


def updateOrCreateDocumentFromPath(path, **document_properties):
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
  document = getDocumentFromPath(path)

  if not document:
    # document did not exist, so create one in a transaction
    key_name = getDocumentKeyNameForPath(path)
    document = soc.models.document.Document.get_or_insert(
      key_name, **document_properties)

  # there is no way to be sure if get_or_insert() returned a new Document or
  # got an existing one due to a race, so update with document_properties anyway,
  # in a transaction
  return soc.logic.model.updateModelProperties(document, **document_properties)




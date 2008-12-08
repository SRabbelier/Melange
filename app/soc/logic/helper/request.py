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

"""Functions that are useful when dealing with requests.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import soc.logic.models as model_logic


def removeRequestForRole(role_entity):
  """Removes the request that leads to the creation of the given entity.
  
  Args:
    role_entity : A datastore entity that is either a role or a subclass of the role model
   
  """
  
  # get the type of the role entity using the classname
  role_type = role_entity.__class__.__name__
  
  # get the request logic so we can query the datastore
  request_logic = model_logic.request.logic
  
  # create the query properties for the specific role
  properties = {'scope' : role_entity.scope,
      'link_id' : role_entity.link_id,
      'role' : role_type.lower() }
  
  # get the request that complies with properties
  request_entity = request_logic.getForFields(properties, unique=True)
  
  # delete the request from the datastore, if there is any
  if request_entity:
    request_logic.delete(request_entity)
    
    
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


def completeRequestForRole(role_entity, role_name):
  """Marks the request that leads to the given role_entity as completly accepted.
  
  Args:
    role_entity : A datastore entity that is either a role or a subclass of the role model
    role_name : The name in the request that is used to describe the type of the role_entity
   
  """

  # get the request logic so we can query the datastore
  request_logic = model_logic.request.logic

  # create the query properties for the specific role
  properties = {'scope_path' : role_entity.scope_path,
      'link_id' : role_entity.link_id,
      'role' : role_name}

  # get the request that complies with properties
  request_entity = request_logic.getForFields(properties, unique=True)

  # mark the request completed, if there is any
  if request_entity:
    request_logic.updateModelProperties(request_entity,
        {'state' : 'completed'})

#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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


"""Utils for manipulating role data.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.modules.seeder.logic.seeder import logic as seeder_logic


class GSoCRoleHelper(object):
  """Helper class to aid in manipulating role data.
  """

  def __init__(self, program):
    self.program = program
    self.user = None

  def create(self):
    """Creates a profile for the current user.
    """
    from soc.models.user import User
    from soc.modules.gsoc.models.profile import GSoCProfile
    from soc.modules.seeder.logic.providers.user import CurrentUserProvider
    properties = {'account': CurrentUserProvider(), 'status': 'valid'}
    self.user = user = seeder_logic.seed(User, properties=properties)
    properties = {'link_id': user.link_id, 'user': user, 'parent': user, 'scope': self.program}
    self.role = seeder_logic.seed(GSoCProfile, properties)

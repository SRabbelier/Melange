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


__authors__ = [
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


import unittest

from google.appengine.api import users

from soc.logic.models.user import logic as user_logic
from soc.logic.models.job import logic as job_logic
from soc.logic.models.priority_group import logic as priority_group_logic
from soc.cron.unique_user_id_adder import setupUniqueUserIdAdder, \
    addUniqueUserIds, DEF_USER_STEP_SIZE


class UniqueUserIdAdderTest(unittest.TestCase):
  """Tests related to soc.cron.unique_user_id_adder.
  """
  def setUp(self):
    """Set up required for the tests.
    """
    # Create DEF_USER_STEP_SIZE+1 users
    #The string order of users' link_id is the same with that of users in the
    #array in order to make sure the last user is handled last
    size = DEF_USER_STEP_SIZE
    num_digits = 0
    while True:
      size /= 10
      num_digits += 1
      if size == 0:
        break
    user_entities = []
    user_properties = {}
    for i in xrange(DEF_USER_STEP_SIZE+1):
      link_id = ('user%0'+str(num_digits)+'d') % i
      email = link_id + '@email.com'
      account = users.User(email=email)
      user_properties.update({
          'link_id': link_id,
          'account': account,
          'name': link_id,
          })
      user_entities.append(user_logic.updateOrCreateFromFields(user_properties))
    self.user_entities = user_entities

  def testSetupUniqueUserIdAdder(self):
    """Test that the job of add unique user ids to users has been created for
    all users.
    """
    priority_group_properties = {
        'link_id': 'a_priority_group',
        }
    priority_group = priority_group_logic.updateOrCreateFromFields(
                                                     priority_group_properties)
    job_properties = {
        'priority_group': priority_group,
        'task_name': 'addUniqueUserIds',
        'key_data': [self.user_entities[0].key()],
        }
    job = job_logic.updateOrCreateFromFields(job_properties)
    setupUniqueUserIdAdder(job)
    self.assertEqual(job.key_data[0], self.user_entities[-1].key())

  def testAddUniqueUserIds(self):
    """Test that a unique user id is added to the user.
    """
    self.assertEqual(self.user_entities[0].user_id, None)
    # set the default fields for the jobs we are going to create
    priority_group = priority_group_logic.getGroup(priority_group_logic.EMAIL)
    job_properties = {
        'priority_group': priority_group,
        'task_name': 'addUniqueUserIds',
        'key_data': [self.user_entities[0].key()],
          }
    job = job_logic.updateOrCreateFromFields(job_properties)
    addUniqueUserIds(job)
    user = user_logic.getFromKeyName(self.user_entities[0].key().name())
    self.assertNotEqual(user.user_id, None)

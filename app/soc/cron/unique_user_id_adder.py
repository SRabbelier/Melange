#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Cron job handler for adding unique user id.
"""

__authors__ = [
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.ext import db
from google.appengine.api import users
from soc.logic.models.job import logic as job_logic
from soc.logic.models.priority_group import logic as priority_logic
from soc.logic.models.user import logic as user_logic


# amount of users to create jobs for before updating
DEF_USER_STEP_SIZE = 10


class TempUserWithUniqueId(db.Model):
  """Helper model for temporary storing User Property with unique id.
  """
  user = db.UserProperty(required=True)


def emailToAccountAndUserId(address):
  """Return a stable user_id string based on an email address, or None if
  the address is not a valid/existing google account.
  """
  user = users.User(address)
  key = TempUserWithUniqueId(user=user).put()
  obj = TempUserWithUniqueId.get(key)
  # pylint: disable-msg=E1103
  return (obj, obj.user.user_id())


def setupUniqueUserIdAdder(job_entity):
  """Job that setup jobs that will add unique user ids to all Users.

  Args:
    job_entity: a Job entity with key_data set to 
                [last_completed_user]
  """

  key_data = job_entity.key_data
  user_fields = {'user_id': None}
  
  if len(key_data) == 1:
    # start where we left off
    user_fields['__key__ >'] = key_data[0]

  m_users = user_logic.getForFields(user_fields,
                                    limit=DEF_USER_STEP_SIZE)

  # set the default fields for the jobs we are going to create
  priority_group = priority_logic.getGroup(priority_logic.CONVERT)
  job_fields = {
      'priority_group': priority_group,
      'task_name': 'addUniqueUserIds'}

  job_query_fields = job_fields.copy()

  while m_users:
    # for each user create a adder job
    for user in m_users:

      job_query_fields['key_data'] = user.key()
      adder_job = job_logic.getForFields(job_query_fields, unique=True)

      if not adder_job:
        # this user doesn't have unique id yet
        job_fields['key_data'] = [user.key()]
        job_logic.updateOrCreateFromFields(job_fields)

    # update our own job
    last_user_key = m_users[-1].key()

    if len(key_data) == 1:
      key_data[0] = last_user_key
    else:
      key_data.append(last_user_key)

    updated_job_fields = {'key_data': key_data}
    job_logic.updateEntityProperties(job_entity, updated_job_fields)

    # rinse and repeat
    user_fields['__key__ >'] = last_user_key
    m_users = user_logic.getForFields(user_fields,
                                      limit=DEF_USER_STEP_SIZE)

  # we are finished
  return


def addUniqueUserIds(job_entity):
  """Job that will add unique user id to a User.

  Args:
    job_entity: a Job entity with key_data set to [user_key]
  """

  from soc.cron.job import FatalJobError

  user_keyname = job_entity.key_data[0].name()
  user_entity = user_logic.getFromKeyName(user_keyname)

  if not user_entity:
    raise FatalJobError('The User with keyname %s does not exist!' % (
        user_keyname))

  # add unique user id
  account, user_id = emailToAccountAndUserId(user_entity.account.email())
  user_entity.account = account
  user_entity.user_id = user_id
  user_entity.put()
  
  # we are done here
  return
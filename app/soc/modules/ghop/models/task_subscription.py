#!/usr/bin/env python2.5
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

"""This module contains the GHOP Task Subscription Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db

import soc.models.base

import soc.modules.ghop.models.task


class GHOPTaskSubscription(soc.models.base.ModelWithFieldAttributes):
  """GHOP Subscription model for tasks.
  """

  # Property holding reference to the GHOPTask for which this subscription
  # entity exists.
  task = db.ReferenceProperty(
      reference_class=soc.modules.ghop.models.task.GHOPTask,
      required=True, collection_name='task_subscribers')

  # Property holding the list of users who are subscribed to the task.
  subscribers = db.ListProperty(item_type=db.Key, default=[])


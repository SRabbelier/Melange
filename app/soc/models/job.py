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

"""This module contains the Job Model."""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

from soc.models import base

import soc.models.priority_group


class Job(base.ModelWithFieldAttributes):
  """The Job model.
  """

  #: reference to the priority group this job belongs to
  priority_group = db.ReferenceProperty(
      reference_class=soc.models.priority_group.PriorityGroup,
      required=True, collection_name='jobs')

  #: the name of the task as defined in soc.cron.job
  task_name = db.StringProperty(required=True)

  #: field storing the status of this job
  #: Waiting means that this job is waiting to be run.
  #: Started means that this job has a worker that is running it.
  #: Finished means that this job has been completed.
  #: Aborted means that this job has been aborted due to a fatal error.
  status = db.StringProperty(default='waiting',
      choices=['waiting','started','finished', 'aborted'])

  #: the date this job was last modified on
  last_modified_on = db.DateTimeProperty(auto_now_add=True)

  #: the amount of times this job raised an Exception (other than an
  #: DeadlineExceededException).
  errors = db.IntegerProperty(default=0)

  #: the data that the worker will use to process this job
  text_data = db.TextProperty(required=False, default="")

  #: the data that the worker will use to process this job
  key_data = db.ListProperty(db.Key, default=[])

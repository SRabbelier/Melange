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

"""This module contains the GCI specific Program Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.program


class GCIProgram(soc.models.program.Program):
  """GCI Program model extends the basic Program model.
  """

  homepage_url_name = "gci_homepage"

  #: Required property containing the number of Tasks Students can work
  #: on simultaneously. For GCI it is 1
  nr_simultaneous_tasks = db.IntegerProperty(
      required=True, default=1,
      verbose_name=ugettext('Simultaneous tasks'))
  nr_simultaneous_tasks.group = ugettext('Contest Rules')
  nr_simultaneous_tasks.help_text = ugettext(
      'Number of tasks students can work on simultaneously in the program.')

  #: A list of difficulty levels that can be assigned for each Task created
  task_difficulties = db.StringListProperty(
      required=True, default=[''],
      verbose_name=ugettext('Difficulty levels'))
  task_difficulties.group = ugettext('Task Settings')
  task_difficulties.help_text = ugettext(
      'List all the difficulty levels that can be assigned to a task.')

  #: A list of task types that a Task can belong to
  task_types = db.StringListProperty(
      required=True, default=['Any'],
      verbose_name=ugettext('Task Types'))
  task_types.group = ugettext('Task Settings')
  task_types.help_text = ugettext(
      'List all the types a task can be in.')

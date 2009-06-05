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

"""This module contains the GHOP WorkSubmission Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.user

from soc.modules.ghop.models import program as ghop_program_model
from soc.modules.ghop.models import task as task_model


class GHOPWorkSubmission(soc.models.linkable.Linkable):
  """Model for work submissions for a task by students.

  Scope will be set to the Organization to which this work has been submitted.
  """

  #: Task to which this work was submitted
  task = db.ReferenceProperty(reference_class=task_model.GHOPTask,
                              required=True,
                              collection_name='work_submissions')

  #: User who submitted this work
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True,
                              collection_name='work_submissions')

  #: Program to which this work belongs to
  program = db.ReferenceProperty(
      reference_class=ghop_program_model.GHOPProgram,
      required=True, collection_name='work_submissions')

  #: Property allowing you to store information about your work
  information = db.TextProperty(
      required=True, verbose_name=ugettext('Info'))
  information.help_text = ugettext(
      'Information about the work you submit for this task')

  #: Property containing an URL to this work or more information about it
  url_to_work = db.LinkProperty(
      required=False, verbose_name=ugettext('URL to your Work'))
  url_to_work.help_text = ugettext(
      'URL to a resource containing your work or more information about it')

  #: Property containing the date when the work was submitted
  submitted_on = db.DateTimeProperty(required=True, auto_now_add=True,
                                     verbose_name=ugettext('Submitted on'))

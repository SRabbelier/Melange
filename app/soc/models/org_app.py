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

"""This module contains the Organization Application Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.document
import soc.models.group_app
import soc.models.user


class OrgApplication(soc.models.group_app.GroupApplication):
  """Specialized questions for the Organization application.

  These questions are in addition to those in the GroupApplication Model.

  Eventually, this will be replaced with a Question/Answer/Quiz/Response
  approach.  At that time, existing OrgApplication entities will be migrated
  (converted) to their new representations in the Datastore.
  """
  
  prior_participation = db.TextProperty(required=False,
    verbose_name=ugettext_lazy(
      'Has your group participated previously?'
      ' If so, please summarize your involvement and any past successes'
      ' and failures.'))

  prior_application = db.TextProperty(required=False,
    verbose_name=ugettext_lazy(
      'If your group has not previously participated, have you applied in'
      ' the past?  If so, for what sort of participation?'))
  
  license_name = db.StringProperty(required=True,
    verbose_name=ugettext_lazy(
      'What license does your organization use?'))
 
  ideas = db.ReferenceProperty(reference_class=soc.models.document.Document,
    required=True, collection_name='ideas_app',
    verbose_name=ugettext_lazy(
      'Please select the Document containing your ideas list.'))

  dev_mailing_list = db.StringProperty(required=False,
    verbose_name=ugettext_lazy(
      'What is the main development mailing list for your group?'
      ' (optional)'))
  dev_mailing_list.help_text = ugettext_lazy(
    'Mailing list email address, URL to sign-up page, etc.')

  backup_admin = db.ReferenceProperty(reference_class=soc.models.user.User,
    required=False,  collection_name='backup_admin_app',
    verbose_name=ugettext_lazy(
      'Please select your backup group administrator (if there is one).'
      ' They will be emailed to confirm, and this group will not be '
      ' accepted until they respond. (optional).'))

  contrib_template = db.ReferenceProperty(
    reference_class=soc.models.document.Document, required=False,
    collection_name='org_app_contrib_template',
    verbose_name=ugettext_lazy(
      'Please select the application template you would like contributors'
      ' to your group to use.  (optional).'))
  contrib_template.help_text = ugettext_lazy(
    'This template will be presented to contributors, such as students'
    ' and other non-member participants, when they apply to contribute'
    ' to the organization.')

  contrib_disappears = db.TextProperty(required=True,
    verbose_text=ugettext_lazy(
      'What is your plan for dealing with disappearing contributors?'))
  contrib_disappears.help_text = ugettext_lazy(
    'Contributors include students and other non-member participants.')

  member_disappears = db.TextProperty(required=True,
    verbose_text=ugettext_lazy(
      'What is your plan for dealing with disappearing members?'))
  member_disappears = ugettext_lazy(
    'Members include mentors, admininstrators, and the like.')

  encourage_contribs = db.TextProperty(required=True,
    verbose_text=ugettext_lazy(
      'What steps will you take to encourage contributors to interact with'
      ' your community before, during, and after the program?'))
  encourage_contribs.help_text = contrib_disappears.help_text

  continued_contribs = db.TextProperty(required=True,
    verbose_text=ugettext_lazy(
      'What will you do to ensure that your accepted contributors stick'
      ' with the project after the program concludes?'))
  continued_contribs.help_text = contrib_disappears.help_text

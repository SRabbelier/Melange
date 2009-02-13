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

"""This module contains the Organization Application Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

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
  
  prior_participation = db.TextProperty(required=False, verbose_name=ugettext(
      'Has your group participated previously?'
      ' If so, please summarize your involvement and any past successes'
      ' and failures.'))

  prior_application = db.TextProperty(required=False, verbose_name=ugettext(
      'If your group has not previously participated, have you applied in'
      ' the past?  If so, for what sort of participation?'))
  
  license_name = db.StringProperty(required=True, verbose_name=ugettext(
      'What license does your organization use?'))
 
  ideas = db.LinkProperty(required=True, verbose_name=ugettext(
      'What is the URL to the ideas list of your organization?'))
  ideas.help_text = ugettext('For instance a link to a Melange public '
      'document or some other URL')

  dev_mailing_list = db.StringProperty(required=False, verbose_name=ugettext(
      'What is the main development mailing list for your group?'))
  dev_mailing_list.help_text = ugettext(
      'Mailing list email address, URL to sign-up page, etc.')

  contrib_template = db.LinkProperty(required=False, verbose_name=ugettext(
      'What is the URL to the application template would you like contributors'
      ' to your organization to use.'))
  contrib_template.help_text = ugettext(
      'This template can be used by contributors, such as students'
      ' and other non-member participants, when they apply to contribute'
      ' to the organization.')
  contrib_template.help_text = ugettext('For instance a link to a Melange '
      'public document or some other URL')

  contrib_disappears = db.TextProperty(required=True, verbose_name=ugettext(
      'What is your plan for dealing with disappearing contributors?'))
  contrib_disappears.help_text = ugettext(
      'Contributors include students and other non-member participants.')

  member_disappears = db.TextProperty(required=True, verbose_name=ugettext(
      'What is your plan for dealing with disappearing members?'))
  member_disappears.help_text = ugettext(
      'Members include mentors, administrators, and the like.')

  encourage_contribs = db.TextProperty(required=True, verbose_name=ugettext(
      'What steps will you take to encourage contributors to interact with'
      ' your community before, during, and after the program?'))
  encourage_contribs.help_text = contrib_disappears.help_text

  continued_contribs = db.TextProperty(required=True, verbose_name=ugettext(
      'What will you do to ensure that your accepted contributors stick'
      ' with the project after the program concludes?'))
  continued_contribs.help_text = contrib_disappears.help_text

  #: field storing whether the User has agreed to the site-wide Terms of Service.
  #: (Not a required field because the Terms of Service might not be present
  #: when the first User profile is created when bootstrapping the site.)
  agreed_to_admin_agreement = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('I Agree to the Admin Agreement'))
  agreed_to_admin_agreement.help_text = ugettext(
      'Indicates whether the user agreed to the Admin Agreement.')

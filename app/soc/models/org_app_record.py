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

"""Contains the OrgAppRecord model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import licenses
from soc.models.survey_record import SurveyRecord

import soc.models.user


class OrgAppRecord(SurveyRecord):
  """Record which must have a main admin, backup admin and proposed link ID.

  This record also contains the status of the application.
  """

  #: field storing the name of the organization.
  name = db.StringProperty(
      verbose_name=ugettext('Organization Name'), required=True)

  #: field storing the description of the organization.
  description = db.TextProperty(
      verbose_name=ugettext('Organization Description'), required=True)

  #: Required field storing a home page URL of the organization.
  home_page = db.LinkProperty(
      required=True, verbose_name=ugettext('Organization Home Page URL'))

  #: Required field storing the main license an organization uses.
  license = db.StringProperty(
      required=True, choices=licenses.LICENSES,
      verbose_name=ugettext('Main Organization License'))

  #: field storing the user which first created the OrgApplicationRecord and 
  #: is therefore the main admin if the application is accepted.
  main_admin = db.ReferenceProperty(
      reference_class=soc.models.user.User, required=True,
      collection_name='main_admin_org_app')

  #: field storing the user reference of the backup admin.
  backup_admin = db.ReferenceProperty(
      reference_class=soc.models.user.User, required=True,
      collection_name='backup_admin_org_app')

  #: field storing whether the User has agreed to the site-wide 
  #: Terms of Service. (Not a required field because the Terms of 
  #: Service might not be present).
  agreed_to_admin_agreement = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('I Agree to the Admin Agreement'))
  agreed_to_admin_agreement.help_text = ugettext(
      'Indicates whether the user agreed to the Admin Agreement.')

  # property containing the status of the application
  # completed means that the application has been processed into a real group
  # pre-accepted: used to indicate that the application has been accepted
  # but the group cannot be made yet.
  # pre-rejected: used to indicate that the application has been rejected
  # but the applicant has not been informed yet.
  status = db.StringProperty(required=True,
      choices=['accepted','rejected','ignored','needs review','completed',
          'pre-accepted', 'pre-rejected'],
      default='needs review',
      verbose_name=ugettext('Application Status'))

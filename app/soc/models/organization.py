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

"""This module contains the Organization Model.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.group


class Organization(soc.models.group.Group):
  """Organization details.

  A Organization entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   reviewers)  a many:1 relationship associating Reviewers with
     a specific Organization. This relation is implemented as the
     'reviewers' back-reference Query of the Organization model 'org'
     reference.
  """
  
  #: Optional development mailing list.     
  dev_mailing_list = db.StringProperty(required=False,
    verbose_name=ugettext_lazy('Development Mailing List'))
  dev_mailing_list.help_text = ugettext_lazy(
    'Mailing list email address, URL to sign-up page, etc.')
    
  member_template = db.ReferenceProperty(
    reference_class=soc.models.document.Document, required=False,
    collection_name='group_app_member_template',
    verbose_name=ugettext_lazy('Application template'))
  member_template.help_text = ugettext_lazy(
    'This template will be presented to potential members when they'
    ' apply to the group.')


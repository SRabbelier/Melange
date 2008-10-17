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

"""This module contains the Organization Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from django.utils.translation import ugettext_lazy

from google.appengine.ext import db

from soc import models

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

  #: Type name used in templates
  TYPE_NAME = ugettext_lazy('Organization')
  #: Type short name used for example in urls
  TYPE_NAME_SHORT = 'org'
  #: Type plural name used in templates
  TYPE_NAME_PLURAL = ugettext_lazy('Organizations')
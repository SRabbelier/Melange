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

"""This module contains the GHOP specific Comment Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.comment


class GHOPComment(soc.models.comment.Comment):
  """GHOP Comment model for tasks, extends the basic Comment model.
  """

  #: Property containing the human readable string that should be
  #: shown for the comment when something in the task changes, 
  #: code.google.com issue tracker style
  change_in_task = db.StringProperty(required=True,
      verbose_name=ugettext('Changes in the task'))

#!/usr/bin/python2.5
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

"""This module contains the GCI Ranking Model.
"""

__authors__ = [
    '"Daniel Hans" <dhans@google.com>',
  ]


from google.appengine.ext import db

from django.utils import simplejson

import soc.models.linkable


class GCIRanking(soc.models.linkable.Linkable):
  """GCI Ranking model.
  """

  #: collected data
  raw_data = db.TextProperty(default='{}')

  #: Date of the last task that was taken into account by this ranking
  date_point = db.DateTimeProperty(required=False, auto_now_add=True)

  #: JSON representation of how the statistic should be collected
  schema = db.StringProperty(default='{}')

  def getData(self):
    """Returns current ranking data.
    """

    if not self.raw_data:
      return {}

    return simplejson.loads(self.raw_data)

  def setData(self, data):
    """Sets data for the ranking entity.
    """

    self.raw_data = simplejson.dumps(data)

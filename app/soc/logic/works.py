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

"""Works (Model) query functions.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.ext import db

from soc.logic import model

import soc.models.work


def getWorksForLimitAndOffset(limit, offset=0, cls=soc.models.work.Work):
  """Returns Works for given offset and limit or None if not found.
    
  Args:
    limit: max amount of entities to return
    offset: optional offset in entities list which defines first entity to
      return; default is zero (first entity)
    cls: Model class of items to return (including sub-classes of that type);
      default is Work
  """
  query = db.GqlQuery(model.buildOrderedQueryString(
      soc.models.work.Work, derived_class=cls, order_by='title'))
 
  return query.fetch(limit, offset)  

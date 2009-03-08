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

"""Review (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base
from soc.logic.models import linkable as linkable_logic

import soc.models.comment
import soc.models.review


class Logic(base.Logic):
  """Logic methods for the comment model
  """

  def __init__(self, model=soc.models.review.Review,
               base_model=soc.models.comment.Comment,
               scope_logic=linkable_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def getReviewsForEntity(self, entity, is_public, order=None):
    """Returns the reviews that have the given entity as scope.
    
    Args:
      entity: the entity which is the scope of the review
      is_public: determines if the public or non-public reviews are returned
      order: the optional ordering in which the reviews are returned
    """

    fields = {'scope': entity,
              'is_public': is_public}

    query = self.getQueryForFields(fields, order)

    return self.getAll(query)

logic = Logic()

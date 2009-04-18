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

"""Helpers used for list info functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


def getStudentProposalInfo(ranking, proposals_keys):
  """Returns a function that returns information about the rank and assignment.

  Args:
    ranking: dict with a mapping from Student Proposal key to rank
    proposals_keys: list of proposal keys assigned a slot
  """

  def wrapper(item, _):
    """Decorator wrapper method.
    """
    info = {'rank': ranking[item.key()]}

    if item.key() in proposals_keys:
      info['item_class'] =  'selected'
    else:
      info['item_class'] =  'normal'

    return info
  return wrapper

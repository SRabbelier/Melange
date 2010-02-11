#!/usr/bin/env python2.5
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

"""List generation logic.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


class Lists(object):
  """List array suitable for enumerating over with just 'for in'.
  """

  DEF_PASSTHROUGH_FIELDS = [
      'pagination',
      'pagination_form',
      'description',
      'export',
      'heading',
      'row',
      'limit',
      'newest',
      'prev',
      'next',
      'first',
      'last',
      'idx',
      ]

  def __init__(self, contents):
    """Constructs a new Lists object with the specified contents.
    """

    # All the contents of all the lists
    self._contents = contents
    self._content = {}

    # For iterating over all the lists
    self._lists = range(len(contents))

  def __getattr__(self, attr):
    """Delegate field lookup to the current list if appropriate.

    If, and only if, a lookup is done on one of the fields defined in
    DEF_PASSTHROUGH_FIELDS, and the current list defines this field,
    the value from the current list is returned.
    """

    if attr not in self.DEF_PASSTHROUGH_FIELDS:
      raise AttributeError()

    if attr not in self._content:
      raise AttributeError()

    return self.get(attr)

  def get(self, item):
    """Returns the item for the current list data.
    """

    return self._content[item]

  def nextList(self):
    """Shifts out the current list content.

    The main content of the next list is returned for further processing.
    """

    # Advance the list data once
    self._content = self._contents[0]
    self._contents = self._contents[1:]

    return self

  def empty(self):
    """Returns true iff there are no lists
    """

    return not self._lists

  def lists(self):
    """Returns a list of numbers the size of the amount of lists.

    This method can be used to iterate over all lists with shift,
    without using a while loop.
    """

    return self._lists

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

"""List generation logic
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


class Lists(object):
  """List array suitable for enumerating over with just 'for in'
  """

  DEF_PASSTHROUGH_FIELDS = [
      'pagination',
      'description',
      'heading',
      'row',
      'limit',
      'newest',
      'prev',
      'next',
      'first',
      'last',
      ]

  def __init__(self, contents):
    """Constructs a new Lists object with the specified contents
    """

    # All the contents of all the lists
    self.contents = contents
    self.content = {}

    # For iterating over all the lists
    self.lists = range(len(contents))
    self.list_data = []

    # For iterating over the rows
    self.rows = []
    self.row_data = []

  def __getattr__(self, attr):
    """Delegate field lookup to the current list if appropriate

    If, and only if, a lookup is done on one of the fields defined in
    DEF_PASSTHROUGH_FIELDS, and the current list defines this field,
    the value from the current list is returned.
    """

    if attr not in self.DEF_PASSTHROUGH_FIELDS:
      raise AttributeError()

    if attr not in self.content:
      raise AttributeError()

    return self.get(attr)

  def get(self, item):
    """Returns the item for the current list data
    """

    return self.content[item]

  def next_list(self):
    """Shifts out the current list content

    The main content of the next list is returned for further processing.
    """

    # Advance the list data once
    self.content = self.contents[0]
    self.contents = self.contents[1:]

    # Update internal 'iterators'
    self.list_data = self.get('data')
    self.rows = range(len(self.list_data))

    return self.get('main')

  def next_row(self):
    """Returns the next list row for the current list

    Before calling this method, next_list should be called at least once.
    """

    # Update internal 'iterators'
    self.row_data =  self.list_data[0]

    # Advance the row data once
    self.list_data = self.list_data[1:]

    return self.get('row')

  def lists(self):
    """Returns a list of numbers the size of the amount of lists.

    This method can be used to iterate over all lists with shift,
    without using a while loop.
    """

    return self.lists

  def rows(self):
    """Returns a list of numbers the size of the amount of items.

    This method can be used to iterate over all items with next for
    the current list, without using a while loop.
    """

    return self.rows

  def item(self):
    """Returns the current row item for the current list

    Before calling this method, next_row should be called at least once.
    """

    return self.row_data

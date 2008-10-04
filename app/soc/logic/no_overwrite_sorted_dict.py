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

"""Like Django SortedDict, but no repeated assignments to the same key.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from django.utils import datastructures


class NoOverwriteSortedDict(datastructures.SortedDict):
  """SortedDict where each key can be given a value only once.
  
  The purpose of this data structure is to be able to detect when
  an attempt is made to overwrite the value of an existing key
  in the SortedDict.  This is to catch, for example, cases such as
  a registry where two different callers attempt to register the
  same view, handler, etc.
 
  It is still possible to pop or del a key out of the dict and then
  add it back to the dict.
  """
  
  KEY_ALREADY_PRESENT_ERROR_FMT = \
    '%s already present, value cannot be overwritten'
  
  def __init__(self, data=None):
    if data is None:
      data = {}

    # call SortedDict's parent __init__()
    # (bypassing the __init__() of SortedDict itself, since it will not
    # enforce our no-overwrite requirement)
    super(datastructures.SortedDict, self).__init__(data)
    
    if isinstance(data, dict):
      self.keyOrder = data.keys()
    else:
      self.keyOrder = []

      for key, value in data:
        if key in self.keyOrder:
          # key has already been given a value, and that value is not
          # permitted to be overwritten, so raise an error
          raise KeyError(self.KEY_ALREADY_PRESENT_ERROR_FMT % key)

        self.keyOrder.append(key)

  def __setitem__(self, key, value):
    if key in self.keyOrder:
      # key has already been given a value, and that value is not permitted
      # to be overwritten, so raise an error
      raise KeyError(self.KEY_ALREADY_PRESENT_ERROR_FMT % key)

    super(NoOverwriteSortedDict, self).__setitem__(key, value)

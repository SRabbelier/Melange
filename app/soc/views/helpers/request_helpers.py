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

"""Helpers for manipulating HTTP requests.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


def getSingleIndexedParamValue(request, param_name, values=()):
  """Returns a value indexed by a query parameter in the HTTP request.
  
  Args:
    request: the Django HTTP request object
    param_name: name of the query parameter in the HTTP request
    values: list (or tuple) of ordered values; one of which is
      retrieved by the index value of the param_name argument in
      the HTTP request
      
  Returns:
    None if the query parameter was not present, was not an integer, or
      was an integer that is not a valid [0..len(values)-1] index into
      the values list.
    Otherwise, returns values[int(param_name value)]
  """
  value_idx = request.GET.get(param_name)
  
  if isinstance(value_idx, (tuple, list)):
    # keep only the first argument if multiple are present
    value_idx = value_idx[0]

  try:
    # GET parameter 'param_name' should be an integer value index
    value_idx = int(value_idx)
  except:
    # ignore bogus or missing parameter values, so return None (no message)
    return None
    
  if value_idx < 0:
    # value index out of range, so return None (no value)
    return None

  if value_idx >= len(values):
    # value index out of range, so return None (no value)
    return None

  # return value associated with valid value index
  return values[value_idx]


def getSingleIndexedParamValueIfMissing(value, request, param_name,
                                        values=()):
  """Returns missing value indexed by a query parameter in the HTTP request.
  
  Args:
    value: an existing value, or a "False" value such as None
    request, param_name, values: see getSingleIndexParamValue()
    
  Returns:
    value, if value is "non-False"
    Otherwise, returns getSingleIndexedParamValue() result.
  """
  if value:
    # value already present, so return it
    return value

  return getSingleIndexedParamValue(request, param_name, values=values)


# TODO(tlarsen):  write getMultipleIndexParamValues() that returns a
#   list of values if present, omitting those values that are
#   out of range

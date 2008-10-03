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

import urlparse


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


def isReferrerSelf(request,
                   expected_prefix=None, suffix=None):
  """Returns True if HTTP referrer path starts with the HTTP request path.
    
  Args:
    request: the Django HTTP request object; request.path is used if
      expected_path is not supplied (the most common usage)
    expected_prefix: optional HTTP path to use instead of the one in
      request.path; default is None (use request.path)
    suffix: suffix to remove from the HTTP request path before comparing
      it to the HTTP referrer path in the HTTP request object headers
      (this is often an link name, for example, that may be changing from
      a POST referrer to a GET redirect target) 
  
  Returns:
    True if HTTP referrer path begins with the HTTP request path (either
      request.path or expected_prefix instead if it was supplied), after
      any suffix was removed from that request path
    False otherwise
       
  """
  http_from = request.META.get('HTTP_REFERER')
      
  if not http_from:
    # no HTTP referrer, so cannot possibly start with expected prefix
    return False

  from_path = urlparse.urlparse(http_from).path
  
  if not expected_prefix:
    # use HTTP request path, since expected_prefix was not supplied
    expected_prefix = request.path

  if suffix:
    # remove suffix (such as a link name) before comparison
    chars_to_remove = len(suffix)
    
    if not suffix.startswith('/'):
      chars_to_remove = chars_to_remove + 1

    expected_prefix = expected_prefix[:-chars_to_remove]

  if not from_path.startswith(expected_prefix):
    # expected prefix did not match first part of HTTP referrer path
    return False
 
  # HTTP referrer started with (possibly truncated) expected prefix
  return True


def replaceSuffix(path, old_suffix, new_suffix=None, params=None):
  """Replace the last part of a URL path with something else.

  Also appends an optional list of query parameters.  Used for
  replacing, for example, one link name at the end of a relative
  URL path with another.

  Args:
    path: HTTP request relative URL path (with no query arguments)
    old_suffix: expected suffix at the end of request.path component;
      if any False value (such as None), the empty string '' is used
    new_suffix: if non-False, appended to request.path along with a
      '/' separator (after removing old_suffix if necessary)
    params: an optional dictionary of query parameters to append to
      the redirect target; appended as ?<key1>=<value1>&<key2>=...
      
  Returns:
    /path/with/new_suffix?a=1&b=2
  """    
  if not old_suffix:
    old_suffix = ''

  old_suffix = '/' + old_suffix

  if path.endswith(old_suffix):
    # also removes any trailing '/' if old_suffix was empty
    path = path[:-len(old_suffix)]

  if new_suffix:
    # if present, appends new_suffix, after '/' separator
    path = '%s/%s' % (path, new_suffix)

  if params:
    # appends any query parameters, after a '?' and separated by '&'
    path = '%s?%s' % (path, '&'.join(
        ['%s=%s' % (p,v) for p,v in params.iteritems()]))

  return path

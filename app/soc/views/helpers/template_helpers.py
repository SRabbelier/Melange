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

"""Helpers for manipulating templates.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>'
  ]


def makeSiblingTemplatesList(templates, new_template_file,
                             default_template=None):
  """Converts template paths into a list of "sibling" templates.
  
  Args:
    templates: search list of templates (or just a single template not in a
      list) from which template paths will be extracted (discarding the final
      template file name of each template)
    new_template_file: new "sibling" template file to append to each extracted
      template path
    default_template: a default template (or a list of them) to append to the
      end of the generated "sibling" template paths; default is None
 
  Returns:
    A list of potential "sibling" templates named by new_template_file located
    in the paths of the templates in the supplied list.  For example, from:
      ['foo/bar/the_old_template.html', 'foo/the_old_template.html']
    to:
      ['foo/bar/some_new_template.html', 'foo/some_new_template.html']
  """
  if not isinstance(templates, (list, tuple)):
    templates = [templates]

  if default_template is None:
    default_template = []

  if not isinstance(default_template, (list, tuple)):
    default_template = [default_template]

  sibling_templates = [
    '%s/%s' % (t.rsplit('/', 1)[0], new_template_file) for t in templates]

  return sibling_templates + default_template


def unescape(html): 
  """Returns the given HTML with ampersands, quotes and carets decoded.
  """ 
  if not isinstance(html, basestring): 
    html = str(html) 
  
  html.replace('&amp;', '&').replace('&lt;', '<')
  html.replace('&gt;', '>').replace('&quot;', '"').replace('&#39;',"'")
  return html


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

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

"""Module contains sidemap related functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


SITEMAP = []


def addPages(pages):
  global SITEMAP
  SITEMAP += pages


def getDjangoURLPatterns(params):
  """Retrieves a list of sidebar entries for this View.

  Params usage:
    The params dictionary is passed to the getKeyFieldsPatterns
    method, see it's docstring on how it is used.
    
    django_patterns: The django_patterns value is returned directly
      if it is non-False.
    django_patterns_defaults: The dajngo_patterns_defaults value is
      used to construct the url patterns. It is expected to be a
      list of tuples. The tuples should contain an url, a module
      name, and the name of the url. The name is used as the
      page_name passed as keyword argument, but also as the name
      by which the url is known to Django internally.
    url_name: The url_name argument is passed as argument to each
      url, together with the link_id pattern, the link_id core
      pattern, and the key fields for this View.

  Args:
    params: a dict with params for this View
  """

  # Return the found result
  if params['django_patterns']:
    return params['django_patterns']

  # Construct defaults manualy
  default_patterns = params['django_patterns_defaults']
  default_patterns += params['extra_django_patterns']

  patterns = []

  for url, module, name in default_patterns:
    name = name % params
    module = module % params

    url = url % {
        'url_name': params['url_name'],
        'lnp': params['link_id_arg_pattern'],
        'ulnp': params['link_id_pattern_core'],
        'key_fields': params['key_fields_pattern'],
        'scope': params['scope_path_pattern'],
        }

    kwargs = {'page_name': name}

    item = (url, module, kwargs, name)
    patterns.append(item)

  return patterns

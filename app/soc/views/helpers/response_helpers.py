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

"""Helpers used to display various views that are forms.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]

import os

from google.appengine.api import users
from django import http
from django import shortcuts

IS_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')

# DeadlineExceededError can live in two different places
try:
  # When deployed
  from google.appengine.runtime import DeadlineExceededError
except ImportError:
  # In the development server
  from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

def respond(request, template, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    template: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template, params) returns.

  Raises:
    Whatever render_to_response(template, params) raises.
  """
  if params is None:
    params = {}
  
  params['request'] = request
  params['id'] = users.get_current_user()
  params['is_admin'] = users.is_current_user_admin()
  params['is_dev'] = IS_DEV
  params['sign_in'] = users.create_login_url(request.path)
  params['sign_out'] = users.create_logout_url(request.path)
  try:
    return shortcuts.render_to_response(template, params)
  except DeadlineExceededError:
    logging.exception('DeadlineExceededError')
    return http.HttpResponse('DeadlineExceededError')
  except MemoryError:
    logging.exception('MemoryError')
    return http.HttpResponse('MemoryError')
  except AssertionError:
    logging.exception('AssertionError')
    return http.HttpResponse('AssertionError')
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

"""Module containing Melange Django 1.0+ configuration for Google App Engine.
"""

import logging
import os
import sys

__authors__ = [
  # alphabetical order by last name, please
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
  
  # Remove the standard version of Django.
  for k in [k for k in sys.modules if k.startswith('django')]:
    del sys.modules[k]

  # Force sys.path to have our own directory first, in case we want to import
  # from it. This lets us replace the built-in Django
  sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
  sys.path.insert(0, os.path.abspath('django'))
  sys.path.insert(0, os.path.abspath('django.zip'))

else:
  # Declare the Django version we need.
  from google.appengine.dist import use_library
  use_library('django', '1.0')

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.signals
import django.db

# Log errors.
def log_exception(*args, **kwds):
  """Function used for logging exceptions.
  """
  logging.exception('Exception in request:')

# Log all exceptions detected by Django.
django.core.signals.got_request_exception.connect(log_exception)

# Unregister the rollback event handler.
django.core.signals.got_request_exception.disconnect(
    django.db._rollback_on_exception)

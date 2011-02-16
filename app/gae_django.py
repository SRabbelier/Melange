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

"""Module containing Melange Django 1.2 configuration for Google App Engine.
"""

import logging
import os
import sys

__authors__ = [
  # alphabetical order by last name, please
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Declare the Django version we need.
from google.appengine.dist import use_library
use_library('django', '1.2')

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

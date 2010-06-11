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
"""Common testing utilities.
"""


__authors__ = [
  '"Augie Fackler" <durin42@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]

from django.test import TestCase

from soc.modules import callback

from soc.views.helper import responses
from tests.pymox import stubout


class MockRequest(object):
  """Shared dummy request object to mock common aspects of a request.

  Before using the object, start should be called, when done (and
  before calling start on a new request), end should be called.
  """

  def __init__(self, path=None, method='GET'):
    """Creates a new empty request object.

    self.REQUEST, self.GET and self.POST are set to an empty
    dictionary, and path to the value specified.
    """

    self.REQUEST = {}
    self.GET = {}
    self.POST = {}
    self.META = {}
    self.path = path
    self.method = method

  def start(self):
    """Readies the core for a new request.
    """

    core = callback.getCore()
    core.startNewRequest(self)

  def end(self):
    """Finishes up the current request.
    """

    core = callback.getCore()
    core.endRequest(self, False)


def get_general_raw(args_names):
  """Gets a general_raw function object.
  """

  def general_raw(*args, **kwargs):
    """Sends a raw information, that is the parameters
    passed to the return function that is mentioned
    in corresponding stubout.Set
    """

    num_args = len(args)
    result = kwargs.copy()
    for i, name in enumerate(args_names):
      if i < num_args:
        result[name] = args[i]
      else:
        result[name] = None
    if len(args_names) < num_args:
      result['__args__'] = args[num_args:]
    return result
  return general_raw


class StuboutHelper(object):
  """Utilities for view test.
  """

  def __init__(self):
    """Creates a new ViewTest object.
    """

    #Creates a StubOutForTesting object
    self.stubout = stubout.StubOutForTesting()

  def tearDown(self):
    """Tear down the stubs that were set up.
    """

    self.stubout.UnsetAll()

  def stuboutBase(self):
    """Applies basic stubout replacements.
    """

    self.stubout.Set(responses, 'respond', get_general_raw(['request', 'template', 'context', 'args', 'headers']))
    self.stubout.Set(responses, 'errorResponse', get_general_raw(['error', 'request', 'template', 'context']))

  def stuboutElement(self, parent, child_name, args_names):
    """Applies a specific stubout replacement.

    Replaces child_name's old definition with the new definition which has a list of arguments (args_names), in the context
    of the given parent.
    """

    self.stubout.Set(parent, child_name, get_general_raw(args_names))


class DjangoTestCase(TestCase):
  """Class extending Django TestCase in order to extend its functions as weel as remove the functions which are not supported by Google App Engine, e.g. database flush and fixtures loading without the assistance of Google App Engine Helper for Django.
  """

  def _pre_setup(self):
    """Performs any pre-test setup.
    """

    pass

  def _post_teardown(self):
    """ Performs any post-test cleanup.
    """

    pass

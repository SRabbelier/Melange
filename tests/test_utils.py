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
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Augie Fackler" <durin42@gmail.com>',
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]

import StringIO
import unittest

import gaetestbed
from mox import stubout

from django.test import client
from django.test import TestCase

from soc.logic.helper import xsrfutil
from soc.middleware.xsrf import XsrfMiddleware
from soc.modules import callback
from soc.views.helper import responses


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

  def get_full_path(self):
    # TODO: if needed add GET params
    return self.path

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
    """Sends a raw information.

    That is the parameters passed to the return function that is mentioned
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

    self.stubout.Set(
        responses, 'respond',
        get_general_raw(['request', 'template', 'context', 'args', 'headers']))
    self.stubout.Set(
        responses, 'errorResponse',
        get_general_raw(['error', 'request', 'template', 'context']))

  def stuboutElement(self, parent, child_name, args_names):
    """Applies a specific stubout replacement.

    Replaces child_name's old definition with the new definition which has
    a list of arguments (args_names), in the context of the given parent.
    """

    self.stubout.Set(parent, child_name, get_general_raw(args_names))

class NonFailingFakePayload(object):
  """Extension of Django FakePayload class that includes seek and readline
  methods.
  """

  def __init__(self, content):
    self.__content = StringIO.StringIO(content)
    self.__len = len(content)

  def read(self, num_bytes=None):
    if num_bytes is None:
        num_bytes = self.__len or 1
    assert self.__len >= num_bytes, \
      "Cannot read more than the available bytes from the HTTP incoming data."
    content = self.__content.read(num_bytes)
    self.__len -= num_bytes
    return content

  def seek(self, pos, mode=0):
    return self.__content.seek(pos, mode)
  
  def readline(self, length=None):
    return self.__content.readline(length)

class DjangoTestCase(TestCase):
  """Class extending Django TestCase in order to extend its functions.

  As well as remove the functions which are not supported by Google App Engine,
  e.g. database flush and fixtures loading without the assistance of Google
  App Engine Helper for Django.
  """

  def _pre_setup(self):
    """Performs any pre-test setup.
    """

    client.FakePayload = NonFailingFakePayload

  def _post_teardown(self):
    """ Performs any post-test cleanup.
    """

    pass

  @classmethod
  def getXsrfToken(cls, path=None, method='POST', data={}, **extra):
    """Returns an XSRF token for request context.

    It is signed by Melange XSRF middleware.
    Add this token to POST data in order to pass the validation check of
    Melange XSRF middleware for HTTP POST.
    """

    """
    request = HttpRequest()
    request.path = path
    request.method = method
    """
    # request is currently not used in _getSecretKey
    request = None
    xsrf = XsrfMiddleware()
    key = xsrf._getSecretKey(request)
    user_id = xsrfutil._getCurrentUserId()
    xsrf_token = xsrfutil._generateToken(key, user_id)
    return xsrf_token


def runTasks(url = None, name=None, queue_names = None):
  """Run tasks with specified url and name in specified task queues.
  """

  task_queue_test_case = gaetestbed.taskqueue.TaskQueueTestCase()
  # Get all tasks with specified url and name in specified task queues
  tasks = task_queue_test_case.get_tasks(url=url, name=name, 
                                         queue_names=queue_names)
  for task in tasks:
    postdata = task['params']
    xsrf_token = DjangoTestCase.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    client.FakePayload = NonFailingFakePayload
    c = client.Client()
    # Run the task with Django test client
    c.post(url, postdata)


class MailTestCase(gaetestbed.mail.MailTestCase, unittest.TestCase):
  """Class extending gaetestbed.mail.MailTestCase to extend its functions.

  Difference:
  * Subclass unittest.TestCase so that all its subclasses need not subclass
  unittest.TestCase in their code.
  * Override assertEmailSent method.
  """

  def setUp(self):
    """Sets up gaetestbed.mail.MailTestCase.
    """

    super(MailTestCase, self).setUp()

  def assertEmailSent(self, to=None, sender=None, subject=None,
                      body=None, html=None, n=None):
    """Override gaetestbed.mail.MailTestCase.assertEmailSent method.

    Difference:
    * It prints out all sent messages to facilitate debug in case of failure.
    * It accepts an optional argument n which is used to assert exactly n
    messages satisfying the criteria are sent out.
    """

    # Run all mail tasks first so that all mails will be sent out
    runTasks(url = '/tasks/mail/send_mail', queue_names = ['mail'])
    messages = self.get_sent_messages(
        to = to,
        sender = sender,
        subject = subject,
        body = body,
        html = html,
    )
    failed = False
    if not messages:
      failed = True
      failure_message = "Expected e-mail message sent. No messages sent"
      details = self._get_email_detail_string(to, sender, subject, body, html)
      if details:
        failure_message += ' with %s.' % details
      else:
        failure_message += '.'
    elif n:
      actual_n = len(messages)
      if n != actual_n:
        failed = True
        failure_message = ("Expected e-mail message sent."
                           "Expected %d messages sent" % n)
        details = self._get_email_detail_string(to, sender, subject, body, html)
        if details:
          failure_message += ' with %s;' % details
        else:
          failure_message += ';'
        failure_message += ' but actually %d.' % actual_n
    # If failed, raise error and display all messages sent
    if failed:
      all_messages = self.get_sent_messages()
      failure_message += '\nAll messages sent: '
      if all_messages:
        failure_message += '\n'
        for message in all_messages:
          failure_message += str(message)
      else:
        failure_message += 'None'
      self.fail(failure_message)


class TaskQueueTestCase(gaetestbed.taskqueue.TaskQueueTestCase,
                        unittest.TestCase):
  """Class extending gaetestbed.taskqueue.TaskQueueTestCase.

  Difference:
  * Subclass unittest.TestCase so that all its subclasses need not subclass
  unittest.TestCase in their code.
  """

  def setUp(self):
    """Sets up gaetestbed.taskqueue.TaskQueueTestCase.
    """

    super(TaskQueueTestCase, self).setUp()

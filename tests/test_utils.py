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


import os
import datetime
import httplib
import StringIO
import unittest

import gaetestbed
from mox import stubout

from google.appengine.ext import db

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

  def seed(self, model, properties):
    """Returns a instance of model, seeded with properties.
    """
    from soc.modules.seeder.logic.seeder import logic as seeder_logic
    return seeder_logic.seed(model, properties)

  def seedProperties(self, model, properties):
    """Returns seeded properties for the specified model.
    """
    from soc.modules.seeder.logic.seeder import logic as seeder_logic
    return seeder_logic.seed_properties(model, properties)

  def post(self, url, postdata):
    """Performs a post to the specified url with postdata.

    Takes care of setting the xsrf_token.
    """
    postdata['xsrf_token'] = self.getXsrfToken(url)
    response = self.client.post(url, postdata)
    postdata.pop('xsrf_token')
    return response

  def modelPost(self, url, model, properties):
    """Performs a post to the specified url after seeding for model.

    Calls post().
    """
    properties = self.seedProperties(model, properties)
    response = self.post(url, properties)
    return response, properties

  def init(self):
    """Performs test setup.

    Sets the following attributes:
      dev_test: True iff DEV_TEST is in environment
      gsoc: a GSoCProgram instance
      org_app: a OrgAppSurvey instance
      org: a GSoCOrganization instance
      timeline: a TimelineHelper instance
      data: a GSoCProfileHelper instance
    """
    from soc.models.site import Site
    from soc.models.document import Document
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.timeline import GSoCTimeline
    from soc.modules.gsoc.models.organization import GSoCOrganization
    from soc.modules.seeder.logic.providers.string import DocumentKeyNameProvider
    from soc.models.org_app_survey import OrgAppSurvey
    from tests.timeline_utils import TimelineHelper
    from tests.profile_utils import GSoCProfileHelper

    self.dev_test = 'DEV_TEST' in os.environ

    properties = {'timeline': self.seed(GSoCTimeline, {}),
                  'status': 'visible', 'apps_tasks_limit': 20}
    self.gsoc = self.seed(GSoCProgram, properties)

    properties = {
        'prefix': 'gsoc_program', 'scope': self.gsoc,
        'read_access': 'public', 'key_name': DocumentKeyNameProvider(),
    }
    document = self.seed(Document, properties=properties)

    self.gsoc.about_page = document
    self.gsoc.events_page = document
    self.gsoc.help_page = document
    self.gsoc.connect_with_us_page = document
    self.gsoc.privacy_policy = document
    self.gsoc.put()

    self.site = Site(key_name='site', link_id='site',
                     active_program=self.gsoc)
    self.site.put()

    properties = {'scope': self.gsoc}
    self.org_app = self.seed(OrgAppSurvey, properties)

    properties = {'scope': self.gsoc, 'status': 'active'}
    self.org = self.seed(GSoCOrganization, properties)

    self.timeline = TimelineHelper(self.gsoc.timeline, self.org_app)
    self.data = GSoCProfileHelper(self.gsoc, self.dev_test)

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

  def getJsonResponse(self, url):
    """Returns the list reponse for the specified url and index.
    """
    return self.client.get(url + '?fmt=json&marker=1')

  def getListResponse(self, url, idx):
    """Returns the list reponse for the specified url and index.
    """
    return self.client.get(url + '?fmt=json&marker=1&idx=' + str(idx))

  def assertErrorTemplatesUsed(self, response):
    """Assert that all the error templates were used.
    """
    self.assertNotEqual(response.status_code, httplib.OK)
    # TODO(SRabbelier): update this when we use an error template again
    # self.assertTemplateUsed(response, 'soc/error.html')

  def assertResponseCode(self, response, status_code):
    """Asserts that the response status is OK.
    """
    if (response.status_code in [httplib.NOT_FOUND, httplib.FORBIDDEN] and
        response.status_code != status_code):
      print response
    self.assertEqual(status_code, response.status_code)

  def assertResponseOK(self, response):
    """Asserts that the response status is OK.
    """
    self.assertResponseCode(response, httplib.OK)

  def assertResponseRedirect(self, response, url=None):
    """Asserts that the response status is FOUND.
    """
    self.assertResponseCode(response, httplib.FOUND)
    if url:
      url = "http://testserver" + url
      self.assertEqual(url, response["Location"])

  def assertResponseForbidden(self, response):
    """Asserts that the response status is FORBIDDEN.

    Does not raise an error if dev_test is set.
    """
    if self.dev_test:
      return
    self.assertResponseCode(response, httplib.FORBIDDEN)

  def assertGSoCTemplatesUsed(self, response):
    """Asserts that all the templates from the base view were used.
    """
    self.assertResponseOK(response)
    for contexts in response.context:
      for context in contexts:
        for value in context.values():
          # make it easier to debug render failures
          if hasattr(value, 'render'):
            value.render()
    self.assertTemplateUsed(response, 'v2/modules/gsoc/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/footer.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/header.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/mainmenu.html')

  def assertIsJsonResponse(self, response):
    """Asserts that all the templates from the base view were used.
    """
    self.assertResponseOK(response)
    self.assertEqual('application/json', response['Content-Type'])
    self.assertTemplateUsed(response, 'json_marker.html')

  def assertPropertiesEqual(self, properties, entity):
    """Asserts that all properties are set on the specified entity.

    Reference properties are compared by their key.
    Any date/time objects are ignored.
    """
    errors = []

    for key, value in properties.iteritems():
      if key == 'key_name':
        prop = entity.key().name()
      elif key == 'parent':
        prop = entity.parent()
      else:
        prop = getattr(entity, key)

      if isinstance(value, db.Model) or isinstance(prop, db.Model):
        value = repr(value.key()) if value else value
        prop = repr(prop.key()) if prop else prop

      if isinstance(value, datetime.date) or isinstance(value, datetime.time):
        continue

      msg = "property %s: '%s' != '%s'" % (key, value, prop)

      try:
        self.assertEqual(value, prop, msg=msg)
      except AssertionError, e:
        errors.append(msg)

    if errors:
      self.fail("\n".join(errors))


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

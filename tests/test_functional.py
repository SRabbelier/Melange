#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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


__authors__ = [
  '"Matthew Wilkes" <matthew@matthewwilkes.co.uk>',
  ]


from gaeftest.test import FunctionalTestCase

from zope.testbrowser import browser

import os.path

class MelangeFunctionalTestCase(FunctionalTestCase):
  """A base class for all functional tests in Melange.

  Tests MUST NOT be defined here, but the superclass requires a path
  attribute that points to the app.yaml.  Utility functions MAY be
  declared here to be shared by all functional tests, but any
  overridden unittest methods MUST call the superclass version.
  """

  path = os.path.abspath(__file__+"/../../app/app.yaml")


class TestBranding(MelangeFunctionalTestCase):
  """Tests that ensure Melange properly displays attribution.

  Other notices, as required by the project and/or law, are tested
  here as well.
  """

  def test_attribution(self):
    """Ensure that the front page asserts that it is a Melange app.
    """

    tb = browser.Browser()
    tb.open("http://127.0.0.1:8080/site/show/site")

    self.assertTrue("Powered by Melange" in tb.contents)

class TestLogin(MelangeFunctionalTestCase):
  """Tests that check the login system is functioning correctly.

  Also tests that users go through the correct registration workflow.
  """

  def test_firstLogin(self):
    """Ensure that new users are prompted to create a profile.

    Also test that only new users are prompted.
    """

    tb = browser.Browser()
    tb.open("http://127.0.0.1:8080")

    tb.getLink("Sign in").click()
    self.assertTrue("login" in tb.url)

    # fill in dev_appserver login form
    tb.getForm().getControl("Email").value = "newuser@example.com"
    tb.getForm().getControl("Login").click()

    self.assertTrue(tb.url.endswith("/show/site"))
    self.assertTrue('Please create <a href="/user/create_profile">'
        'User Profile</a> in order to view this page' in tb.contents)

    tb.getLink("User Profile").click()

    # fill in the user profile
    cp = tb.getForm(action="create_profile")
    cp.getControl(name="link_id").value = "exampleuser"
    cp.getControl(name="name").value = "Example user"
    cp.getControl("Save").click()

    # if all is well, we go to the edit page
    self.assertTrue("edit_profile" in tb.url)

    tb.open("http://127.0.0.1:8080")

    # call to action no longer on front page
    self.assertFalse('Please create <a href="/user/create_profile">'
        'User Profile</a> in order to view this page' in tb.contents)


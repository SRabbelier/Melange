#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing tests for GHOP Task View.
"""


__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


import os
import unittest

from fixture import DataSet
from fixture import GoogleDatastoreFixture
from fixture.style import NamedDataStyle

from tests.test_utils import MockRequest
from tests.test_utils import StuboutHelper

from tests import datasets
from tests.app.soc.modules.ghop.logic.models import test_task as ghop_test_task

from soc import models
from soc.views.out_of_band import AccessViolation

from soc.modules.ghop import models as ghop_models
from soc.modules.ghop.views.helper import access
from soc.modules.ghop.views.models import task


class TestView(task.View):
  """
  """

  def __init__(self):
    """
    """

    rights = access.GHOPChecker(None)
    rights['create'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin'], ['active'],
            []])]
    rights['edit'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open']])]
    rights['delete'] = [
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open']])]
    rights['show'] = ['checkStatusForTask']
    rights['list_org_tasks'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False])]
    rights['suggest_task'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin', 'ghop/mentor'], ['active'],
            ['Unapproved']])]
    rights['search'] = ['allow']


    params = {}
    params['name'] = "Test"
    params['logic'] = ghop_test_task.Logic()
    params['rights'] = rights

    super(TestView, self).__init__(params=params)


class TaskTest(unittest.TestCase):
  """Tests related to the GHOP task view.
  """

  def setUp(self):
    """Set up required for the view tests.
    """

    self.view = TestView()
    self.stubout_helper = StuboutHelper()
    self.stubout_helper.stuboutBase()
    self.stubout_helper.stuboutElement(task.View, 'select', ['request', 'view', 'redirect'])

    # map all the models
    models_dict = {
        'User': models.user.User,
        'Site': models.site.Site,
        'Sponsor': models.sponsor.Sponsor,
        'Host': models.host.Host,
        'GHOPTimeline': ghop_models.timeline.GHOPTimeline,
        'GHOPProgram': ghop_models.program.GHOPProgram,
        'GHOPOrganization': ghop_models.organization.GHOPOrganization,
        'GHOPOrgAdmin': ghop_models.org_admin.GHOPOrgAdmin,
        'GHOPMentor': ghop_models.mentor.GHOPMentor,
        'GHOPStudent': ghop_models.student.GHOPStudent,
        'GHOPTask': ghop_models.task.GHOPTask,
        }

    # create a fixture for Appengine datastore using the previous map
    datafixture = GoogleDatastoreFixture(env=models_dict,
                                         style=NamedDataStyle())

    # seed the data in the datastore
    self.data = datafixture.data(
        datasets.UserData, datasets.SiteData, datasets.SponsorData,
        datasets.HostData, datasets.GHOPTimelineData, datasets.GHOPProgramData,
        datasets.GHOPOrganizationData, datasets.GHOPOrgAdminData,
        datasets.GHOPMentorData, datasets.GHOPMentorData,
        datasets.GHOPTaskData)

    self.data.setup()

  def tearDown(self):
    """Clears everything that is setup for the tests
    """

    self.data.teardown()
    self.stubout_helper.tearDown()

  def testCreateRedirectAsDeveloper(self):
    """Tests if the Developer is redirected to the page containing
    all the Organizations under the Program to chose from
    """

    from soc.modules.ghop.views.models.organization import View

    request = MockRequest("/test/ghop/task/create")
    request.start()
    access_type = "create"
    page_name = "Create Task"
    kwargs = {}
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()

    self.assertTrue('redirect' in actual
        and isinstance(actual['redirect'], View))

  def testCreateRights(self):
    """Tests if the Developer/Org Admin have rights create tasks and
    other users don't have.
    """

    request = MockRequest("/test/ghop/task/create/google/ghop2009/melange")
    # test if the Org Admin of the Organization passes the access check
    os.environ['USER_EMAIL'] = 'melange_admin_0001@example.com'
    request.start()
    access_type = "create"
    page_name = "Create Task"
    kwargs = {'scope_path': 'google/ghop2009/melange'}
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if the Developer passes the access check
    os.environ['USER_EMAIL'] = 'test@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if the Org Admin of other Organization doesn't passes
    # the access check
    os.environ['USER_EMAIL'] = 'asf_admin_0001@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if the Mentor of the Organization doesn't passes
    # the access check
    os.environ['USER_EMAIL'] = 'melange_mentor_0001@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if the Mentor of other Organization doesn't passes
    # the access check
    os.environ['USER_EMAIL'] = 'asf_mentor_0001@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if the Student of the Organization doesn't passes
    # the access check
    os.environ['USER_EMAIL'] = 'melange_student_0001@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if person with no role in Melange doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'public@example.com'
    request.start()
    actual = self.view.create(request, access_type,
                              page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

  def testSuggestTask(self):
    """Tests if the Mentor have rights create tasks and
    other users don't have.
    """

    request = MockRequest(
        "/test/ghop/task/suggest_task/google/ghop2009/melange")

    # test if mentor of the Organization passes the access check
    os.environ['USER_EMAIL'] = 'melange_mentor_0001@example.com'
    request.start()
    access_type = "suggest_task"
    page_name = "Suggest Task"
    kwargs = {'scope_path': 'google/ghop2009/melange'}
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if mentor of other Organization doesn't pass the
    # access check
    os.environ['USER_EMAIL'] = 'asf_mentor_0001@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if Org Admin of the Organization passes the access check
    os.environ['USER_EMAIL'] = 'melange_admin_0001@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if Org Admin of other Organization doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'asf_admin_0001@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if Developer passes the access check
    os.environ['USER_EMAIL'] = 'test@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if student of the Organization doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'melange_student_0001@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if student of other Organization doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'asf_student_0001@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if user who doesn't have any role in Melange
    # doesn't pass the access check
    os.environ['USER_EMAIL'] = 'public@example.com'
    request.start()
    actual = self.view.suggestTask(request, access_type,
                                   page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

  def testEditTask(self):
    """Tests if the Mentor/OrgAdmin have rights to edit tasks and
    other users don't have.
    """

    request = MockRequest(
        "/test/ghop/task/edit/google/ghop2009/melange/t126518233415")

    # test if Developer passes the access check
    os.environ['USER_EMAIL'] = 'test@example.com' 
    access_type = "edit"
    page_name = "Edit Task"
    kwargs = {'scope_path': 'google/ghop2009/melange',
              'link_id': 't126518233415'}
    request.start()
    actual = self.view.edit(request, access_type,
                            page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if Org Admin of the Organization passes the access check
    os.environ['USER_EMAIL'] = 'melange_admin_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                            page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' not in actual)

    # test if Org Admin of other Organization doesn't passes the
    # access check
    os.environ['USER_EMAIL'] = 'asf_admin_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if mentor of the Organization doesn't passes the
    # access check
    os.environ['USER_EMAIL'] = 'melange_mentor_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if mentor of other Organization doesn't passes the
    # access check
    os.environ['USER_EMAIL'] = 'asf_mentor_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if student of the Organization doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'melange_student_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if student of other Organization doesn't pass
    # the access check
    os.environ['USER_EMAIL'] = 'asf_student_0001@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

    # test if user who doesn't have any role in Melange
    # doesn't pass the access check
    os.environ['USER_EMAIL'] = 'public@example.com'
    request.start()
    actual = self.view.edit(request, access_type,
                                page_name=page_name, **kwargs)
    request.end()
    self.assertTrue('error' in actual and isinstance(
        actual['error'], AccessViolation))

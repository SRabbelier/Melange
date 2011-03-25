#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module containing the RequestData object that will be created for each
request in the GSoC module.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


import datetime

from google.appengine.api import users
from google.appengine.ext import db

from django.core.urlresolvers import reverse

from soc.models import role
from soc.logic.models.host import logic as host_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.views.helper.access_checker import isSet
from soc.views.helper.request_data import RequestData

from soc.modules.gsoc.models import profile

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic


def isBefore(date):
  """Returns True iff date is before utcnow().

  Returns False if date is not set.
  """
  return date and datetime.datetime.utcnow() < date


def isAfter(date):
  """Returns True iff date is after utcnow().

  Returns False if date is not set.
  """
  return date and date < datetime.datetime.utcnow()


def isBetween(start, end):
  """Returns True iff utcnow() is between start and end.
  """
  return isAfter(start) and isBefore(end)


class TimelineHelper(object):
  """Helper class for the determination of the currently active period.

  Methods ending with "On", "Start", or "End" return a date.
  Methods ending with "Between" return a tuple with two dates.
  Methods ending with neither return a Boolean.
  """

  def __init__(self, timeline, org_app):
    self.timeline = timeline
    self.org_app = org_app

  def currentPeriod(self):
    """Return where we are currently on the timeline.
    """
    if not self.programActive():
      return 'offseason'

    if self.beforeOrgSignupStart():
      return 'kickoff_period'

    if self.studentsAnnounced():
      return 'coding_period'

    if self.afterStudentSignupStart():
      return 'student_signup_period'

    if self.afterOrgSignupStart():
      return 'org_signup_period'

    return 'offseason'

  def orgsAnnouncedOn(self):
    return self.timeline.accepted_organization_announced_deadline

  def programActiveBetween(self):
    return (self.timeline.program_start, self.timeline.program_end)

  def orgSignupStart(self):
    return self.org_app.survey_start

  def orgSignupBetween(self):
    return (self.org_app.survey_start, self.org_app.survey_end)

  def studentSignupStart(self):
    return self.timeline.student_signup_start

  def studentsSignupBetween(self):
    return (self.timeline.student_signup_start,
            self.timeline.student_signup_end)

  def studentsAnnouncedOn(self):
    return self.timeline.accepted_students_announced_deadline

  def programActive(self):
    start, end = self.programActiveBetween()
    return isBetween(start, end)

  def beforeOrgSignupStart(self):
    return self.org_app and isBefore(self.orgSignupStart())

  def afterOrgSignupStart(self):
    return self.org_app and isAfter(self.orgSignupStart())

  def orgSignup(self):
    if not self.org_app:
      return False
    start, end = self.orgSignupBetween()
    return isBetween(start, end)

  def orgsAnnounced(self):
    return isAfter(self.orgsAnnouncedOn())

  def afterStudentSignupStart(self):
    return isAfter(self.studentSignupStart())

  def studentSignup(self):
    start, end = self.studentsSignupBetween()
    return isBetween(start, end)

  def studentsAnnounced(self):
    return isAfter(self.studentsAnnouncedOn())


class RequestData(RequestData):
  """Object containing data we query for each request in the GSoC module.

  The only view that will be exempt is the one that creates the program.

  Fields:
    site: The Site entity
    user: The user entity (if logged in)
    program: The GSoC program entity that the request is pointing to
    program_timeline: The GSoCTimeline entity
    timeline: A TimelineHelper entity
    is_host: is the current user a host of the program
    org_admin_for: the organizations the current user is an admin for
    mentor_for: the organizations the current user is a mentor for
    student_info: the StudentInfo for the current user and program

  Raises:
    out_of_band: 404 when the program does not exist
  """

  def __init__(self):
    """Constructs an empty RequestData object.
    """
    super(RequestData, self).__init__()
    # program wide fields
    self.program = None
    self.program_timeline = None
    self.org_app = None

    # user profile specific fields
    self.profile = None
    self.is_host = False
    self.mentor_for = []
    self.org_admin_for = []
    self.student_info = None

  def populate(self, redirect, request, args, kwargs):
    """Populates the fields in the RequestData object.

    Args:
      request: Django HTTPRequest object.
      args & kwargs: The args and kwargs django sends along.
    """
    super(RequestData, self).populate(redirect, request, args, kwargs)

    if kwargs.get('sponsor') and kwargs.get('program'):
      program_keyfields = {'link_id': kwargs['program'],
                           'scope_path': kwargs['sponsor']}
      self.program = program_logic.getFromKeyFieldsOr404(program_keyfields)
    else:
      self.program =  self.site.active_program

    self.program_timeline = self.program.timeline

    org_app_fields = {'scope': self.program}
    self.org_app = org_app_logic.getOneForFields(org_app_fields)

    self.timeline = TimelineHelper(self.program_timeline, self.org_app)

    if kwargs.get('organization'):
      org_keyfields = {
          'link_id': kwargs.get('organization'),
          'scope_path': self.program.key().id_or_name(),
          }
      self.organization = org_logic.getFromKeyFieldsOr404(org_keyfields)

    if self.user:
      key_name = '%s/%s' % (self.program.key().name(), self.user.link_id)
      self.profile = profile.GSoCProfile.get_by_key_name(
          key_name, parent=self.user)

      self.is_host = self.program.scope.key() in self.user.host_for

    if self.profile:
      orgs = set(self.profile.mentor_for + self.profile.org_admin_for)
      org_map = dict((i.key(), i) for i in db.get(orgs))

      self.mentor_for = org_map.values()
      self.org_admin_for = [org_map[i] for i in self.profile.org_admin_for]
      self.student_info = self.profile.student_info


class RedirectHelper(object):
  """Helper for constructing redirects.
  """

  def __init__(self, data, response):
    """Initializes the redirect helper.
    """
    self._data = data
    self._response = response
    self._clear()

  def _clear(self):
    """Clears the internal state.
    """
    self._no_url = False
    self._url_name = None
    self._url = None
    self.args = []
    self.kwargs = {}

  def sponsor(self):
    """Sets kwargs for an url_patterns.SPONSOR redirect.
    """
    self._clear()
    self.kwargs['sponsor'] = self._data.program.scope_path

  def program(self):
    """Sets kwargs for an url_patterns.PROGRAM redirect.
    """
    self.sponsor()
    self.kwargs['program'] = self._data.program.link_id

  def organization(self, organization=None):
    """Sets the kwargs for an url_patterns.ORG redirect.
    """
    if not organization:
      assert isSet(self._data.organization)
      organization = self._data.organization
    self.program()
    self.kwargs['organization'] = organization.link_id

  def id(self, id=None):
    """Sets the kwargs for an url_patterns.ID redirect.
    """
    if not id:
      assert 'id' in self.data.kwargs
      id = self.data.kwargs['id']
    self.program()
    self.kwargs['id'] = id

  def review(self, id=None, student=None):
    """Sets the kwargs for an url_patterns.REVIEW redirect.
    """
    if not student:
      assert 'student' in self.data.kwargs
      student = self.data.kwargs['student']
    self.id(id)
    self.kwargs['student'] = student

  def invite(self, role=None):
    if not role:
      assert 'role' in self._data.kwargs
      role = self._data.kwargs['role']
    self.organization()
    self.kwargs['role'] = role

  def document(self, document):
    """Sets args for an url_patterns.DOCUMENT redirect.

    If document is not set, a call to url() will return None.
    """
    self._clear()
    if not document:
      self._no_url = True
      return self
    self.args = [document.prefix, document.scope_path + '/', document.link_id]
    self._url_name = 'show_gsoc_document'
    return self

  def urlOf(self, name):
    """Returns the resolved url for name.

    Uses internal state for args and kwargs.
    """
    if self.args:
      url = reverse(name, args=self.args)
    elif self.kwargs:
      url = reverse(name, kwargs=self.kwargs)
    else:
      url = reverse(name)
    return url

  def url(self):
    """Returns the url of the current state.
    """
    if self._no_url:
      return None
    assert self._url or self._url_name
    if self._url:
      return self._url
    return self.urlOf(self._url_name)

  def to(self, name=None, validated=False):
    """Redirects to the resolved url for name.

    Uses internal state for args and kwargs.
    """
    assert name or self._url_name
    url = self.urlOf(name or self._url_name)
    if validated:
      url = url + '?validated'
    self.toUrl(url)

  def toUrl(self, url):
    """Redirects to the specified url.
    """
    from django.utils.encoding import iri_to_uri
    self._response.set_status(302)
    self._response["Location"] = iri_to_uri(url)

  def login(self):
    """Sets url to the login url.
    """
    self._clear()
    self._url = users.create_login_url(self._data.full_path)
    return self

  def logout(self):
    """Sets url to the logout url.
    """
    self._clear()
    self._url = users.create_logout_url(self._data.full_path)
    return self

  def acceptedOrgs(self):
    """Returns the redirect for list all GSoC projects.
    """
    self.program()
    self._url_name = 'gsoc_accepted_orgs'
    return self

  def allProjects(self):
    """Returns the redirect for list all GSoC projects.
    """
    self.program()
    self._url_name = 'gsoc_accepted_projects'
    return self

  def homepage(self):
    """Returns the redirect for the homepage for the current GSOC program.
    """
    self.program()
    self._url_name = 'gsoc_homepage'
    return self

  def dashboard(self):
    """Returns the redirect for the dashboard page for the current GSOC program.
    """
    self.program()
    self._url_name = 'gsoc_dashboard'
    return self

  def projectDetails(self, student_project):
    """Returns the URL to the Student Project.

    Args:
      student_project: entity which represents the Student Project
    """
    # TODO: Use django reverse function from urlresolver once student_project
    # view is converted to the new infrastructure
    self._clear()
    self._url = '/gsoc/student_project/show/%s' % student_project.key().id_or_name()
    return self

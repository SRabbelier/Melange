# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing the core callback.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.tasks import grading_survey_group as grading_group_tasks
from soc.tasks import mailer as mailer_tasks
from soc.tasks import surveys as survey_tasks
from soc.tasks.updates import project_conversion
from soc.tasks.updates import proposal_conversion
from soc.tasks.updates import role_conversion
from soc.tasks.updates import start_update
from soc.views.models import club
from soc.views.models import club_admin
from soc.views.models import club_member
from soc.views.models import document
from soc.views.models import host
from soc.views.models import mentor
from soc.views.models import notification
from soc.views.models import organization
from soc.views.models import org_admin
from soc.views.models import program
from soc.views.models import request
from soc.views.models import role
from soc.views.models import site
from soc.views.models import sponsor
from soc.views.models import student
from soc.views.models import student_project
from soc.views.models import survey
from soc.views.models import timeline
from soc.views.models import user
from soc.views.models import user_self


class Callback(object):
  """Callback object that handles interaction between the core.
  """

  API_VERSION = 1

  def __init__(self, core):
    """Initializes a new Callback object for the specified core.
    """

    self.core = core
    self.views = []

    # disable clubs
    self.enable_clubs = False
    self.v2 = True

  def registerViews(self):
    """Instantiates all view objects.
    """
    from soc.views import legacy
    from soc.views import site

    self.views.append(legacy.Legacy())
    self.views.append(site.EditSitePage())
    self.views.append(site.SiteHomepage())

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    # Redesigned view registration
    for view in self.views:
      self.core.registerSitemapEntry(view.djangoURLPatterns())

    self.core.registerSitemapEntry(role_conversion.getDjangoURLPatterns())
    self.core.registerSitemapEntry(proposal_conversion.getDjangoURLPatterns())
    self.core.registerSitemapEntry(project_conversion.getDjangoURLPatterns())

    if self.v2:
      return

    if self.enable_clubs:
      self.core.registerSitemapEntry(club.view.getDjangoURLPatterns())
      self.core.registerSitemapEntry(club_admin.view.getDjangoURLPatterns())
      self.core.registerSitemapEntry(club_member.view.getDjangoURLPatterns())

    self.core.registerSitemapEntry(document.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(host.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(mentor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(notification.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(organization.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_admin.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(request.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(site.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(sponsor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_project.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(survey.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(timeline.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(user_self.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(user.view.getDjangoURLPatterns())

    # register task URL's
    self.core.registerSitemapEntry(grading_group_tasks.getDjangoURLPatterns())
    self.core.registerSitemapEntry(mailer_tasks.getDjangoURLPatterns())
    self.core.registerSitemapEntry(start_update.getDjangoURLPatterns())
    self.core.registerSitemapEntry(survey_tasks.getDjangoURLPatterns())

  def registerWithSidebar(self):
    """Called by the server when sidebar entries should be registered.
    """

    self.core.requireUniqueService('registerWithSidebar')

    if self.enable_clubs:
      self.core.registerSidebarEntry(club.view.getSidebarMenus)
      self.core.registerSidebarEntry(club.view.getExtraMenus)
      self.core.registerSidebarEntry(club_admin.view.getSidebarMenus)
      self.core.registerSidebarEntry(club_member.view.getSidebarMenus)

    self.core.registerSidebarEntry(host.view.getSidebarMenus)
    self.core.registerSidebarEntry(request.view.getSidebarMenus)
    self.core.registerSidebarEntry(site.view.getSidebarMenus)
    self.core.registerSidebarEntry(sponsor.view.getExtraMenus)
    self.core.registerSidebarEntry(sponsor.view.getSidebarMenus)
    self.core.registerSidebarEntry(user_self.view.getSidebarMenus)
    self.core.registerSidebarEntry(user.view.getSidebarMenus)

  def registerRights(self):
    """Called by the server when the document rights should be registered.
    """

    site_membership = {
        'admin': [],
        'restricted': ['host'],
        'member': ['host'],
        'list': ['host'],
        }

    club_membership = {
        'admin': ['host', 'club_admin'],
        'restricted': ['host', 'club_admin'],
        'member': ['host', 'club_admin', 'club_member'],
        'list': ['host', 'club_admin', 'club_member'],
        }

    sponsor_membership = {
        'admin': ['host'],
        'restricted': ['host'],
        'member': ['host'],
        'list': ['host'],
        }

    program_membership = {
        'admin': ['host'],
        'restricted': ['host', 'org_admin'],
        'member': ['host', 'org_admin', 'org_mentor', 'org_student'],
        'list': ['host', 'org_admin', 'org_mentor'],
        }

    organization_membership = {
        'admin': ['host', 'org_admin'],
        'restricted': ['host', 'org_admin', 'org_mentor'],
        'member': ['host', 'org_admin', 'org_mentor', 'org_student'],
        'list': ['host', 'org_admin', 'org_mentor'],
        }

    user_membership = {
        'admin': ['user_self'],
        'restricted': ['user_self'], # ,'friends'?
        'member': ['user_self'], # ,'friends'
        'list': ['user_self'],
        }

    self.core.registerRight('site', site_membership)
    self.core.registerRight('club', club_membership)
    self.core.registerRight('sponsor', sponsor_membership)
    self.core.registerRight('program', program_membership)
    self.core.registerRight('org', organization_membership)
    self.core.registerRight('user', user_membership)

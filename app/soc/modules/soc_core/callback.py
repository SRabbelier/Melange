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


from soc.modules import callback

from soc.views.models import club
from soc.views.models import club_app
from soc.views.models import club_admin
from soc.views.models import club_member
from soc.views.models import cron
from soc.views.models import document
from soc.views.models import host
from soc.views.models import job
from soc.views.models import mentor
from soc.views.models import notification
from soc.views.models import organization
from soc.views.models import org_admin
from soc.views.models import org_app
from soc.views.models import priority_group
from soc.views.models import program
from soc.views.models import request
from soc.views.models import site
from soc.views.models import sponsor
from soc.views.models import student
from soc.views.models import student_project
from soc.views.models import student_proposal
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

    # disable clubs
    self.enable_clubs = False

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    if self.enable_clubs:
      self.core.registerSitemapEntry(club.view.getDjangoURLPatterns())
      self.core.registerSitemapEntry(club_admin.view.getDjangoURLPatterns())
      self.core.registerSitemapEntry(club_app.view.getDjangoURLPatterns())
      self.core.registerSitemapEntry(club_member.view.getDjangoURLPatterns())

    self.core.registerSitemapEntry(cron.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(document.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(host.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(job.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(mentor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(notification.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(organization.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_admin.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_app.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(priority_group.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(request.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(site.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(sponsor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_project.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_proposal.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(timeline.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(user_self.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(user.view.getDjangoURLPatterns())

  def registerWithSidebar(self):
    """Called by the server when sidebar entries should be registered.
    """

    self.core.requireUniqueService('registerWithSidebar')

    if self.enable_clubs:
      self.core.registerSidebarEntry(club.view.getSidebarMenus)
      self.core.registerSidebarEntry(club.view.getExtraMenus)
      self.core.registerSidebarEntry(club_admin.view.getSidebarMenus)
      self.core.registerSidebarEntry(club_member.view.getSidebarMenus)
      self.core.registerSidebarEntry(club_app.view.getSidebarMenus)

    self.core.registerSidebarEntry(user_self.view.getSidebarMenus)
    self.core.registerSidebarEntry(site.view.getSidebarMenus)
    self.core.registerSidebarEntry(user.view.getSidebarMenus)
    self.core.registerSidebarEntry(sponsor.view.getSidebarMenus)
    self.core.registerSidebarEntry(sponsor.view.getExtraMenus)
    self.core.registerSidebarEntry(host.view.getSidebarMenus)
    self.core.registerSidebarEntry(request.view.getSidebarMenus)
    self.core.registerSidebarEntry(program.view.getSidebarMenus)
    self.core.registerSidebarEntry(program.view.getExtraMenus)
    self.core.registerSidebarEntry(student.view.getSidebarMenus)
    self.core.registerSidebarEntry(student_project.view.getSidebarMenus)
    self.core.registerSidebarEntry(student_proposal.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getExtraMenus)
    self.core.registerSidebarEntry(org_admin.view.getSidebarMenus)
    self.core.registerSidebarEntry(mentor.view.getSidebarMenus)
    self.core.registerSidebarEntry(org_app.view.getSidebarMenus)

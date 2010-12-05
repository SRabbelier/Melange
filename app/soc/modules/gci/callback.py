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

"""Module containing the GCI Callback.
"""

__authors__ = [
  '"Madhusudan C.S." <madhusudancs@gmail.com>',
  '"Daniel Hans" <dhans@google.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.modules.gci.tasks import bulk_create
from soc.modules.gci.tasks import org_app_survey as org_app_survey_tasks
from soc.modules.gci.tasks import parental_forms
from soc.modules.gci.tasks import ranking_update
from soc.modules.gci.tasks import task_update
from soc.modules.gci.views.models import mentor
from soc.modules.gci.views.models import organization
from soc.modules.gci.views.models import org_admin
from soc.modules.gci.views.models import org_app_survey
from soc.modules.gci.views.models import program
from soc.modules.gci.views.models import student
from soc.modules.gci.views.models import student_ranking
from soc.modules.gci.views.models import task
from soc.modules.gci.views.models import task_subscription
from soc.modules.gci.views.models import timeline
from soc.modules.gci.views.models import work_submission


class Callback(object):
  """Callback object that handles interaction between the core.
  """

  API_VERSION = 1

  def __init__(self, core):
    """Initializes a new Callback object for the specified core.
    """

    self.core = core

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    # register the GCI Views
    self.core.registerSitemapEntry(mentor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(organization.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_admin.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_app_survey.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_ranking.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(task.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(
        task_subscription.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(timeline.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(work_submission.view.getDjangoURLPatterns())

    # register GCI GAE Tasks URL's
    self.core.registerSitemapEntry(bulk_create.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_app_survey_tasks.getDjangoURLPatterns())
    self.core.registerSitemapEntry(parental_forms.getDjangoURLPatterns())
    self.core.registerSitemapEntry(ranking_update.getDjangoURLPatterns())
    self.core.registerSitemapEntry(task_update.getDjangoURLPatterns())

  def registerWithSidebar(self):
    """Called by the server when sidebar entries should be registered.
    """

    # Require that we had the chance to register the urls we need with the
    # sitemap.
    self.core.requireUniqueService('registerWithSidebar')

    # register the GCI menu entries
    self.core.registerSidebarEntry(mentor.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getExtraMenus)
    self.core.registerSidebarEntry(organization.view.getSidebarMenus)
    self.core.registerSidebarEntry(org_admin.view.getSidebarMenus)
    self.core.registerSidebarEntry(program.view.getExtraMenus)
    self.core.registerSidebarEntry(program.view.getSidebarMenus)
    self.core.registerSidebarEntry(student.view.getSidebarMenus)
    self.core.registerSidebarEntry(task.view.getSidebarMenus)
    self.core.registerSidebarEntry(task_subscription.view.getSidebarMenus)

  def registerRights(self):
    """Called by the server when the document rights should be registered.
    """

    gci_program_membership  = {
        'admin': ['host'],
        'restricted': ['host', 'gci_org_admin'],
        'member': ['host', 'gci_org_admin', 'gci_org_mentor',
                   'gci_org_student'],
        'list': ['host', 'gci_org_admin', 'gci_org_mentor'],
        }

    gci_organization_membership = {
        'admin': ['host', 'gci_org_admin'],
        'restricted': ['host', 'gci_org_admin', 'gci_org_mentor'],
        'member': ['host', 'gci_org_admin', 'gci_org_mentor',
                   'gci_org_student'],
        'list': ['host', 'gci_org_admin', 'gci_org_mentor'],
        }

    self.core.registerRight('gci_program', gci_program_membership)
    self.core.registerRight('gci_org', gci_organization_membership)

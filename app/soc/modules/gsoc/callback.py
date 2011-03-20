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

"""Module containing the GSoC Callback.
"""

__authors__ = [
    '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.views.models import role
from soc.modules.gsoc.logic.models import program as program_logic
from soc.modules.gsoc.tasks import accept_proposals
from soc.modules.gsoc.tasks import org_app_survey as org_app_survey_tasks
from soc.modules.gsoc.tasks import program_freezer
from soc.modules.gsoc.tasks import slot_assignment
from soc.modules.gsoc.tasks import proposal_duplicates as \
    proposal_duplicates_tasks
from soc.modules.gsoc.tasks import proposal_review
from soc.modules.gsoc.views.models import grading_project_survey as \
    grading_survey
from soc.modules.gsoc.views.models import grading_survey_group
from soc.modules.gsoc.views.models import mentor
from soc.modules.gsoc.views.models import org_admin
from soc.modules.gsoc.views.models import org_app_survey
from soc.modules.gsoc.views.models import organization
from soc.modules.gsoc.views.models import program
from soc.modules.gsoc.views.models import project_survey
from soc.modules.gsoc.views.models import student
from soc.modules.gsoc.views.models import student_project
from soc.modules.gsoc.views.models import student_proposal
from soc.modules.gsoc.views.models import timeline


class Callback(object):
  """Callback object that handles interaction between the core.
  """

  API_VERSION = 1

  def __init__(self, core):
    """Initializes a new Callback object for the specified core.
    """

    self.core = core
    self.v2 = True
    self.views = []

  def registerViews(self):
    """Instantiates all view objects.
    """
    from soc.modules.gsoc.views import dashboard
    from soc.modules.gsoc.views import document
    from soc.modules.gsoc.views import homepage
    from soc.modules.gsoc.views import invite
    from soc.modules.gsoc.views import org_app
    from soc.modules.gsoc.views import org_home
    from soc.modules.gsoc.views import profile
    from soc.modules.gsoc.views import proposal
    from soc.modules.gsoc.views import proposal_review
    from soc.modules.gsoc.views import program
    from soc.modules.gsoc.views import projects_list
    from soc.modules.gsoc.views import request

    self.views.append(dashboard.Dashboard())
    self.views.append(document.EditDocumentPage())
    self.views.append(document.DocumentPage())
    self.views.append(homepage.Homepage())
    self.views.append(org_app.OrgApp())
    self.views.append(org_home.OrgHome())
    self.views.append(profile.ProfilePage())
    self.views.append(proposal.ProposalPage())
    self.views.append(proposal.UpdateProposal())
    self.views.append(proposal_review.ReviewProposal())
    self.views.append(proposal_review.PostComment())
    self.views.append(proposal_review.PostScore())
    self.views.append(program.ProgramPage())
    self.views.append(projects_list.ListProjects())
    self.views.append(invite.InvitePage())
    self.views.append(invite.ShowInvite())
    self.views.append(request.RequestPage())

  def registerWithSitemap(self):
    """Called by the server when sitemap entries should be registered.
    """

    self.core.requireUniqueService('registerWithSitemap')

    # Redesigned view registration
    for view in self.views:
      self.core.registerSitemapEntry(view.djangoURLPatterns())

    if self.v2:
      return

    # register the GSoC Views
    self.core.registerSitemapEntry(
        grading_survey_group.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(grading_survey.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(mentor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_admin.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(organization.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_app_survey.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(project_survey.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(role.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_project.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student_proposal.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(timeline.view.getDjangoURLPatterns())

    # register the GSoC Tasks
    self.core.registerSitemapEntry(org_app_survey_tasks.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program_freezer.getDjangoURLPatterns())
    self.core.registerSitemapEntry(
        proposal_duplicates_tasks.getDjangoURLPatterns())
    self.core.registerSitemapEntry(accept_proposals.getDjangoURLPatterns())
    self.core.registerSitemapEntry(proposal_review.getDjangoURLPatterns())
    self.core.registerSitemapEntry(slot_assignment.getDjangoURLPatterns())

  def registerWithSidebar(self):
    """Called by the server when sidebar entries should be registered.
    """

    # Require that we had the chance to register the urls we need with the
    # sitemap.
    self.core.requireUniqueService('registerWithSidebar')

    # register the GSoC menu entries
    self.core.registerSidebarEntry(grading_survey_group.view.getSidebarMenus)
    self.core.registerSidebarEntry(mentor.view.getSidebarMenus)
    self.core.registerSidebarEntry(org_admin.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getExtraMenus)
    self.core.registerSidebarEntry(program.view.getSidebarMenus)
    self.core.registerSidebarEntry(program.view.getExtraMenus)
    self.core.registerSidebarEntry(student_project.view.getSidebarMenus)
    self.core.registerSidebarEntry(student_proposal.view.getSidebarMenus)
    self.core.registerSidebarEntry(student.view.getSidebarMenus)

  def registerRights(self):
    """Called by the server when the document rights should be registered.
    """

    gsoc_program_membership  = {
        'admin': ['host'],
        'restricted': ['host', 'gsoc_org_admin'],
        'member': ['host', 'gsoc_org_admin', 'gsoc_org_mentor',
                   'gsoc_org_student'],
        'list': ['host', 'gsoc_org_admin', 'gsoc_org_mentor'],
        }

    gsoc_organization_membership = {
        'admin': ['host', 'gsoc_org_admin'],
        'restricted': ['host', 'gsoc_org_admin', 'gsoc_org_mentor'],
        'member': ['host', 'gsoc_org_admin', 'gsoc_org_mentor',
                   'gsoc_org_student'],
        'list': ['host', 'gsoc_org_admin', 'gsoc_org_mentor'],
        }

    self.core.registerRight('gsoc_program', gsoc_program_membership)
    self.core.registerRight('gsoc_org', gsoc_organization_membership)

  def registerWithProgramMap(self):
    """Called by the server when program_map entries should be registered.
    """

    self.core.requireUniqueService('registerWithProgramMap')

    program_entities = program_logic.logic.getAllPrograms()
    map = ('GSoC Programs', [
        (str(e.key()), e.name) for e in program_entities])

    self.core.registerProgramEntry(map)

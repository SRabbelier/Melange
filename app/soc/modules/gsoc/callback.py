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
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]

from soc.modules.gsoc.views.models import mentor
from soc.modules.gsoc.views.models import org_admin
from soc.modules.gsoc.views.models import organization
from soc.modules.gsoc.views.models import program
from soc.modules.gsoc.views.models import student
from soc.modules.gsoc.views.models import timeline


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

    # register the GSoC Views
    self.core.registerSitemapEntry(mentor.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(org_admin.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(organization.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(program.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(student.view.getDjangoURLPatterns())
    self.core.registerSitemapEntry(timeline.view.getDjangoURLPatterns())

  def registerWithSidebar(self):
    """Called by the server when sidebar entries should be registered.
    """

    # require that we had the chance to register the urls we need with the sitemap
    self.core.requireUniqueService('registerWithSidebar')

    # register the GHOP menu entries
    self.core.registerSidebarEntry(mentor.view.getSidebarMenus)
    self.core.registerSidebarEntry(org_admin.view.getSidebarMenus)
    self.core.registerSidebarEntry(organization.view.getSidebarMenus)
    self.core.registerSidebarEntry(program.view.getSidebarMenus)
    self.core.registerSidebarEntry(student.view.getSidebarMenus)
    self.core.registerSidebarEntry(timeline.view.getSidebarMenus)

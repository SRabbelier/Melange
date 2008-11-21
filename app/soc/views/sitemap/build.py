#!/usr/bin/python2.5
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

"""Module that constructs the sitemap.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.conf.urls import defaults

from soc.views.models import document
from soc.views.models import presence
from soc.views.models import host
from soc.views.models import request
from soc.views.models import user
from soc.views.models import site
from soc.views.models import sponsor

from soc.views.sitemap import sidebar
from soc.views.sitemap import sitemap


sidebar.SIDEBAR.append(user.view.getUserSidebar())

sidebar.SIDEBAR.append(presence.view.getSidebarLinks())
sitemap.addPages(presence.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(site.view.getSidebarLinks())
sitemap.addPages(site.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(user.view.getSidebarLinks())
sitemap.addPages(user.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(document.view.getSidebarLinks())
sitemap.addPages(document.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(sponsor.view.getSidebarLinks())
sitemap.addPages(sponsor.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(host.view.getSidebarLinks())
sitemap.addPages(host.view.getDjangoURLPatterns())

sidebar.SIDEBAR.append(request.view.getSidebarLinks())
sitemap.addPages(request.view.getDjangoURLPatterns())


def getPatterns():
  return defaults.patterns(None, *sitemap.SITEMAP)

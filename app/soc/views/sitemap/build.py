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

from soc.views.models import club
from soc.views.models import club_app
from soc.views.models import club_admin
from soc.views.models import document
from soc.views.models import host
from soc.views.models import notification
from soc.views.models import organization
from soc.views.models import program
from soc.views.models import request
from soc.views.models import site
from soc.views.models import sponsor
from soc.views.models import timeline
from soc.views.models import user
from soc.views.models import user_self

from soc.views.sitemap import sidebar
from soc.views.sitemap import sitemap


sidebar.addMenu(user_self.view.getSidebarMenus)
sidebar.addMenu(club.view.getSidebarMenus)
sidebar.addMenu(club_admin.view.getSidebarMenus)
sidebar.addMenu(club_app.view.getSidebarMenus)
sidebar.addMenu(site.view.getSidebarMenus)
sidebar.addMenu(user.view.getSidebarMenus)
sidebar.addMenu(document.view.getSidebarMenus)
sidebar.addMenu(sponsor.view.getSidebarMenus)
sidebar.addMenu(host.view.getSidebarMenus)
sidebar.addMenu(request.view.getSidebarMenus)
sidebar.addMenu(program.view.getSidebarMenus)
sidebar.addMenu(program.view.getExtraMenus)
sidebar.addMenu(organization.view.getSidebarMenus)

sitemap.addPages(club.view.getDjangoURLPatterns())
sitemap.addPages(club_admin.view.getDjangoURLPatterns())
sitemap.addPages(club_app.view.getDjangoURLPatterns())
sitemap.addPages(document.view.getDjangoURLPatterns())
sitemap.addPages(host.view.getDjangoURLPatterns())
sitemap.addPages(notification.view.getDjangoURLPatterns())
sitemap.addPages(organization.view.getDjangoURLPatterns())
sitemap.addPages(program.view.getDjangoURLPatterns())
sitemap.addPages(request.view.getDjangoURLPatterns())
sitemap.addPages(site.view.getDjangoURLPatterns())
sitemap.addPages(sponsor.view.getDjangoURLPatterns())
sitemap.addPages(timeline.view.getDjangoURLPatterns())
sitemap.addPages(user_self.view.getDjangoURLPatterns())
sitemap.addPages(user.view.getDjangoURLPatterns())


def getPatterns():
  return defaults.patterns(None, *sitemap.SITEMAP)

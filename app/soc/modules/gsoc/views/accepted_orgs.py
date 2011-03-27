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

"""Module containing the views for GSoC accepted orgs.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.conf.urls.defaults import url

from soc.logic.exceptions import AccessViolation
from soc.views.template import Template

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import lists
from soc.modules.gsoc.views.helper import url_patterns

from soc.modules.gsoc.logic.models.organization import logic as org_logic


class AcceptedOrgsList(Template):
  """Template for list of accepted organizations.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data
    r = data.redirect

    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('name', 'Name')
    list_config.addSimpleColumn('link_id', 'Link ID', hidden=True)
    list_config.setRowAction(
        lambda e, *args: r.organization(e).urlOf('gsoc_org_home'))
    list_config.addColumn('tags', 'Tags',
                          lambda e, *args: e.tags_string(e.org_tag))
    list_config.addColumn(
        'ideas', 'Ideas',
        (lambda e, *args: lists.urlize(e.ideas, name="[ideas page]")),
        hidden=True)
    list_config.setDefaultSort('name')

    self._list_config = list_config

  def context(self):
    description = 'List of organizations accepted into %s' % (
            self.data.program.name)

    list = lists.ListConfigurationResponse(self._list_config, 0, description)

    return {
        'lists': [list],
    }

  def getListData(self):
    idx = lists.getListIndex(self.request)
    if idx == 0:
      fields = {'scope': self.data.program,
                'status': ['active', 'inactive']}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, org_logic, fields)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gsoc/accepted_orgs/_project_list.html"


class AcceptedOrgsPage(RequestHandler):
  """View for the accepted organizations page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/accepted_orgs/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/accepted_orgs/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_accepted_orgs'),
        url(r'gsoc/program/accepted_orgs/%s$' % url_patterns.PROGRAM, self),
        url(r'program/accepted_orgs/%s$' % url_patterns.PROGRAM, self),
    ]

  def checkAccess(self):
    self.check.acceptedOrgsAnnounced()

  def jsonContext(self):
    list_content = AcceptedOrgsList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    return {
        'page_name': "Accepted organizations for %s" % self.data.program.name,
        'accepted_orgs_list': AcceptedOrgsList(self.request, self.data),
    }

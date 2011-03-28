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

"""Module for the GSoC search page.
"""

__authors__ = [
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


import os

from django.conf.urls.defaults import url

from soc.logic.models.site import logic as site_logic

from soc.modules.gsoc.views.base import RequestHandler


class SearchGsocPage(RequestHandler):
  """View for the search gsoc page.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/search$', self, name='search_gsoc'),
    ]

  def context(self):
    site = site_logic.getSingleton()
    return {
        'app_version': os.environ.get('CURRENT_VERSION_ID', '').split('.')[0],
        'page_name': 'Search GSoC',
        'cse_key':  site.cse_key
    }

  def templatePath(self):
    return 'v2/modules/gsoc/search.html'

  def checkAccess(self):
    pass

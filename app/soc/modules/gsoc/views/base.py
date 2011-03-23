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

"""Module containing the boiler plate required to construct GSoC views.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Mario Ferraro" <fadinlight@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]

import os

from soc.logic import system

from soc.views.base import RequestHandler

from soc.modules.gsoc.views import base_templates
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper.request_data import RequestData


class RequestHandler(RequestHandler):
  """Customization required by GSoC to handle HTTP requests.
  """

  def render(self, context):
    """Renders the page using the specified context.

    See soc.views.base.RequestHandler.

    The context object is extended with the following values:
      header: a rendered header.Header template for the current self.data
      mainmenu: a rendered site_menu.MainMenu template for the current self.data
      footer: a rendered site_menu.Footer template for the current self.data
      app_version: the current version of the application, used e.g. in URL
                   patterns to avoid JS caching issues.
    """
    context['header'] = base_templates.Header(self.data)
    context['mainmenu'] = base_templates.MainMenu(self.data)
    context['footer'] = base_templates.Footer(self.data)
    context['app_version'] = os.environ.get('CURRENT_VERSION_ID', '').split('.')[0]
    context['is_local'] = system.isLocal()
    super(RequestHandler, self).render(context)

  def init(self, request, args, kwargs):
    self.data = RequestData()
    self.data.populate(request, args, kwargs)
    self.check = access_checker.AccessChecker(self.data)

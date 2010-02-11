#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Middleware to handle maintenance mode.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import os

from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from django.utils.translation import ugettext

from soc.views.helper import responses


DEF_DOWN_FOR_MAINTENANCE_MSG = ugettext("Down for maintenance")
DEF_IN_UNEXPECTED_MAINTENANCE_MSG = ugettext(
      "Down for unexpected maintenance.")


class MaintenanceMiddleware(object):
  """Middleware to handle maintenance mode.
  """

  def maintenance(self, request):
    """Returns a 'down for maintenance' view.
    """

    context = responses.getUniversalContext(request)
    context['page_name'] = ugettext('Maintenance')

    notice = context.pop('site_notice')

    if not notice:
      context['body_content'] = DEF_IN_UNEXPECTED_MAINTENANCE_MSG
    else:
      context['body_content'] = notice

    context['header_title'] = DEF_DOWN_FOR_MAINTENANCE_MSG
    context['sidebar_menu_items'] = [
        {'heading': DEF_DOWN_FOR_MAINTENANCE_MSG,
         'group': ''},
        ]

    template = 'soc/base.html'

    return responses.respond(request, template, context=context)

  def process_request(self, request):
    """Called when a request is made.

    See the Django middleware documentation for an explanation of
    the method signature.
    """

    context = responses.getUniversalContext(request)
    allowed = (context['is_admin']
        or ('HTTP_X_APPENGINE_CRON' in os.environ)
        or ('HTTP_X_APPENGINE_QUEUENAME' in os.environ))

    if not allowed and context['in_maintenance']:
      return self.maintenance(request)

  def process_exception(self, request, exception):
    """Called when an uncaught exception is raised.

    See the Django middleware documentation for an explanation of
    the method signature.
    """

    if isinstance(exception, CapabilityDisabledError):
      # assume the site is in maintenance if we get CDE
      return self.maintenance(request)

    # let the exception handling middleware handle it
    return None

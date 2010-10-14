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

"""Views for GCI Task Subscription.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from django import http

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views.helper import decorators
from soc.views.models import base

from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.views.helper import access as gci_access

import soc.modules.gci.logic.models.task_subscription


class View(base.View):
  """View methods for the Task Subscriptions.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the task_subscription.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['subscribe'] = ['checkIsUser']

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.task_subscription.logic
    new_params['rights'] = rights

    new_params['name'] = "Task Subscription"
    new_params['module_name'] = "task_subscription"

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/task_subscription'

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>subscribe)$',
        '%(module_package)s.%(module_name)s.subscribe',
        'Subscribe to the %(name)s'),
        ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def subscribe(self, request, access_type, page_name=None,
                params=None, **kwargs):
    """View that subscribes/unsubscribes an user.

    This view is accessed by an AJAX call from task public page.

    Args:
      request: the standard Django HTTP request object
    """

    data = None
    get_params = request.GET

    task_entity = gci_task_logic.logic.getFromKeyNameOr404(
        get_params['key_name'])
    user_entity = user_logic.logic.getForCurrentAccount()

    # this method gets called everytime the task public page gets loaded
    # caused by jQuery. So this conditional is necessary to make sure
    # toggling won't happen every time task public page is loaded but
    # only when subscription star is clicked
    if not get_params.get('no_toggle'):
      data = params['logic'].subscribeUser(
          task_entity, user_entity, toggle=True)
    else:
      data = params['logic'].subscribeUser(
          task_entity, user_entity, toggle=False)

    return http.HttpResponse(data if data else '')


view = View()

subscribe = decorators.view(view.subscribe)

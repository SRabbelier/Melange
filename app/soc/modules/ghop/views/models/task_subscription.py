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

"""Views for GHOP Task Subscription.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from google.appengine.ext import db

from django import http

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views.helper import decorators
from soc.views.models import base

from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.logic.models import task_subscription as \
    ghop_task_subscription_logic
from soc.modules.ghop.views.helper import access as ghop_access

import soc.modules.ghop.logic.models.task_subscription


class View(base.View):
  """View methods for the Task Subscriptions.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the task_subscription.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['subscribe'] = ['checkIsUser']

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.task_subscription.logic
    new_params['rights'] = rights

    new_params['name'] = "Task Subscription"
    new_params['module_name'] = "task_subscription"

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/task_subscription'

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

    get_params = request.GET

    task_entity = ghop_task_logic.logic.getFromKeyNameOr404(
        get_params['key_name'])

    user_account = user_logic.logic.getForCurrentAccount()

    entity = params['logic'].getOrCreateTaskSubscriptionForTask(task_entity)

    subscribers = db.get(entity.subscribers)

    # TODO: this should not loop over all subscribers but use GET argument
    remove = False

    for subscriber in subscribers:
      # pylint: disable-msg=E1103
      if subscriber.key() == user_account.key():
        remove = True
        break

    if remove:
      subscribers.remove(subscriber)
      data = 'remove'
    else:
      subscribers.append(user_account)
      data = 'add'

    # TODO: missing description for this argument, is it even necessary?
    if not get_params.get('no_toggle'):
      sub_keys = []
      for subscriber in subscribers:
        sub_keys.append(subscriber.key())

      properties = {
          'subscribers': sub_keys,
          }

      ghop_task_subscription_logic.logic.updateEntityProperties(
          entity, properties)

    return http.HttpResponse(data)


view = View()

subscribe = decorators.view(view.subscribe)

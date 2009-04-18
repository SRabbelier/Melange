#!/usr/bin/python2.5
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

"""Views for Cron.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import http

from soc.logic import dicts
from soc.logic.models.priority_group import logic as priority_group_logic
from soc.logic.models.job import logic as job_logic
from soc.views.helper import access
from soc.views.models import base

import soc.cron.job


class View(base.View):
  """View methods for the Cron model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = priority_group_logic

    new_params['name'] = "Cron"

    new_params['django_patterns_defaults'] = [
        (r'^%(url_name)s/(?P<access_type>add)$',
          'soc.views.models.%(module_name)s.add', 'Add %(name_short)s'),
        (r'^%(url_name)s/(?P<access_type>poke)$',
          'soc.views.models.%(module_name)s.poke', 'Poke %(name_short)s'),
        ]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def add(self, request, access_type, page_name):
    group = priority_group_logic.getGroup(priority_group_logic.EMAIL)

    fields = {
        'priority_group': group,
        'task_name': 'sendAcceptanceEmail',
        'text_data': "O HI THAR",
        }

    job_logic.updateOrCreateFromFields(fields)

    return http.HttpResponse("Done")

  def poke(self, request, access_type, page_name):
    """
    """

    order = ['-priority']
    query = priority_group_logic.getQueryForFields(order=order)
    groups = priority_group_logic.getAll(query)
    handler = soc.cron.job.handler

    groups_completed = 0
    jobs_completed = 0

    for group in groups:
      filter = {
          'priority_group': group,
          'status': 'waiting',
          }

      query = job_logic.getQueryForFields(filter=filter)
      jobs = job_logic.getAll(query)

      for job in jobs:
        job_key = job.key().id()
        good = handler.handle(job_key)

        if not good:
          break

        jobs_completed += 1

      groups_completed += 1

    response = 'Completed %d jobs and %d groups completed.' % (
        jobs_completed, groups_completed)

    return http.HttpResponse(response)


view = View()

add = view.add
poke = view.poke

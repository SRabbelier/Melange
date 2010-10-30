#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Views for Student Ranking.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from soc.views.models import base

from soc.logic import dicts
from soc.views import helper

from soc.views.helper import decorators

from soc.modules.gci.logic.models.task import logic as task_logic
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import program as gci_program_view

import soc.modules.gci.logic.models.student_ranking

class View(base.View):
  """View methods for the Tasks.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the task View class
    to provide the user with the necessary views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['any_access'] = ['allow']

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.student_ranking.logic
    new_params['rights'] = rights

    new_params['name'] = "Student Ranking"
    new_params['module_name'] = "student_ranking"
    new_params['sidebar_grouping'] = 'Student Rankings'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/student_ranking'

    new_params['scope_view'] = gci_program_view

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>show_details)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.show_details',
          'Show ranking details.'),
        ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  def showDetails(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows ranking details for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    logic = params['logic']
    ranking = logic.getFromKeyFields(kwargs)
    student = ranking.student
    program = ranking.scope

    filter = {
        'student': student,
        'program': program,
        'status': 'Closed'
        }
    tasks = task_logic.getForFields(filter)

    total = 0
    for task in tasks:
      points = task.difficulty.value
      total += points
      task.points = points

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = 'Ranking details for %s.' % student.name()
    context['tasks'] = tasks
    context['total'] = total

    template = 'modules/gci/student_ranking/details.html'

    return helper.responses.respond(request, template, context=context)
    
view = View()

show_details = decorators.view(view.showDetails)

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
from soc.views.helper import lists
from soc.views.helper import redirects

from soc.modules.gci.logic.models.task import logic as gci_task_logic
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import program as gci_program_view

import soc.modules.gci.logic.models.student_ranking

class View(base.View):
  """View methods for the Tasks.
  """

  DETAILS_MSG_FMT = 'Ranking details for %s.'

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

    list_params = params.copy()
    list_params['list_description'] = self.DETAILS_MSG_FMT % student.user.name
    list_params['public_field_extra'] = lambda entity: {
        'task': entity.title,
        'org': entity.scope.name,
        'points_difficulty': entity.taskDifficulty().value
        }
    list_params['public_field_keys'] = [
        'task', 'org', 'points_difficulty', 'closed_on']
    list_params['public_field_names'] = [
        'Task', 'Organization', 'Points (Difficulty)', 'Completed on']
    list_params['public_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, {'url_name': 'gci/task'}),
    }

    if lists.isDataRequest(request):
      return self.getListRankingDetailsData(request, list_params, student)

    contents = []
    order = ['closed_on']
    list = lists.getListGenerator(request, list_params, order=order, idx=0)
    contents.append(list)

    return self._list(request, list_params, contents, page_name)


  def getListRankingDetailsData(self, request, params, student):
    """Returns the list data for Ranking Details list.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      org_entity: GCIOrganization entity for which the lists are generated
    """

    filter = {
        'student': student,
        'status': 'Closed',
        }

    visibility = 'public'
    args = []

    params['logic'] = gci_task_logic

    contents = lists.getListData(request, params, filter,
        visibility=visibility, args=args)
    return lists.getResponse(request, contents)

view = View()

show_details = decorators.view(view.showDetails)

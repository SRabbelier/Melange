#!/usr/bin/python2.5
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

"""Views for an admin to manage statistics.
"""

__authors__ = [
    '"Daniel Hans" <Daniel.M.Hans@gmail.com>',
  ]


import csv
import logging
import StringIO

from google.appengine.api import memcache
from google.appengine.ext import db

from gviz import gviz_api

from django import http
from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.models import linkable

from soc.logic import accounts
from soc.logic import dicts

from soc.views import helper
from soc.views import out_of_band

from soc.logic.models.user import logic as user_logic

from soc.tasks import responses as task_responses
from soc.tasks.helper import decorators as task_decorators

from soc.views.models import base
from soc.views.models import program as program_view
from soc.views.helper import access
from soc.views.helper import decorators as view_decorators
from soc.views.helper import responses

from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.statistic.logic.models.statistic import logic as \
    statistic_logic

from soc.modules.statistic.models import statistic

from soc.modules.statistic.views.helper import access
from soc.modules.statistic.views.helper import redirects

import soc.cache.logic


class View(base.View):
  """View methods for the Statistic model.
  """

  DEF_EACH_GSOC_STAT_MSG = ugettext("These statistics have been"
      " defined for all Google Summer of Code programs.")

  DEF_ONE_GSOC_STAT_MSG = ugettext("These statistics have been"
      " defined for this particular Google Summer of Code program.")

  DEF_EACH_GSOC_LIST_IDX = 0
  DEF_ONE_GSOC_LIST_IDX = 1

  DEF_NO_VISUALIZATION_MSG_FMT = ugettext("There is no available"
      " visualization for %s statistic. Please try again later.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Args:
      params: a dict with params for this View

    """

    rights = access.StatisticChecker(params)

    rights['csv_export'] = [('checkCanManageStatistic', program_logic)]
    rights['get_json_response'] =  [('checkCanManageStatistic', program_logic)]
    rights['show'] = [('checkCanManageStatistic', program_logic)]
    rights['visualize'] = [('checkCanManageStatistic', program_logic)]
    rights['update_stats'] = [('checkCanManageStatistic', program_logic)]
    rights['manage_statistics'] = [
        ('checkIsHostForProgramInScope', program_logic)]
    rights['set_collect_task'] = [('checkCanManageStatistic', program_logic)]

    new_params = {}

    new_params['logic'] = statistic_logic
    new_params['rights'] = rights
    new_params['scope_view'] = program_view
    new_params['name'] = 'statistic'
    new_params['sidebar_grouping'] = 'Statistics'
    new_params['module_package'] = 'soc.modules.statistic.views.models'

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>manage_statistics)/%(scope)s$',
         '%(module_package)s.%(module_name)s.manage_statistics',
         'Manage Statistics'),
        (r'^%(url_name)s/(?P<access_type>update_stats)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.update_stats',
         'Update Statistics'),
        (r'^%(url_name)s/(?P<access_type>clear_stats)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.update_stats',
         'Clear Statistics'),
        (r'^%(url_name)s/(?P<access_type>set_collect_task)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.set_collect_task',
         'Set collect task'),
        (r'^%(url_name)s/(?P<access_type>visualize)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.visualize',
         'Visualize Statistic'),
        (r'^%(url_name)s/(?P<access_type>csv_export)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.csv_export',
         'Export Statistic'),
        (r'^%(url_name)s/(?P<access_type>get_json_response)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.get_json_response',
         'Get Json Response'),
        (r'^%(url_name)s/(?P<access_type>get_json_response)/%(scope)s$',
         '%(module_package)s.%(module_name)s.get_json_response',
         'Get Json Response'),
        (r'^%(url_name)s/(?P<access_type>collect_task)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.collect_task',
         'Collect task'),
        (r'^%(url_name)s/(?P<access_type>get_available_statistics)$',
         '%(module_package)s.%(module_name)s.get_available_statistics',
         'Get Available Statistics'),
        (r'^%(url_name)s/(?P<access_type>get_virtual_statistics)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.get_virtual_statistics',
         'Get virtual statistics'),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['working_json', 'calculated_on',
        'next_entity', 'choices_json', 'final_json',]

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),
        }

    new_params['public_field_keys'] = new_params['select_field_keys'] = [
        "name", "calculated_on"]

    new_params['public_field_names'] = new_params['select_field_names'] = [
        "Name", "Calculated on"]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @view_decorators.merge_params
  @view_decorators.check_access
  def manageStatistics(self, request, access_type, page_name=None,
                       params=None, **kwargs):
    """Represents view that allows a program admin to manage stats.
    """

    if request.method == 'POST':
      return self._manageStatisticsPost(request, access_type, page_name,
                                       params, **kwargs)
    else: # request.method == 'GET'
      return self._manageStatisticsGet(request, access_type, page_name,
                                      params, **kwargs)

  def _manageStatisticsGet(self, request, access_type, page_name=None,
                          params=None, **kwargs):
    """GET method for manage statistics request.
    """

    program = self._getProgramInScopeEntity(kwargs['scope_path'])

    context = {}

    list_params = self.getParams().copy()
    list_params['public_field_props'] = {
        "unread": {
            "stype": "select",
            "editoptions": {"value": ":All;^Read$:Read;^Not Read$:Not Read"}
        }
    }
    list_params['public_conf_extra'] = {
        "multiselect": True,
    }

    list_params['public_button_global'] = [
        {
          'bounds': [1,'all'],
          'id': 'collect_stats',
          'caption': 'Collect',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'table',
              }
        },
        {
          'bounds': [1,'all'],
          'id': 'clear_stats',
          'caption': 'Clear',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'table',
              }
        }]

    # statistic entities which are defined for all GSoC programs
    ep_params = list_params.copy()

    ep_params['list_description'] = self.DEF_EACH_GSOC_STAT_MSG
    ep_params['public_row_extra'] = lambda entity: {
        'link': redirects.getVisualizeRedirect(entity, ep_params),
    }

    # statistic entities which are defined for the specific GSoC program
    op_params = list_params.copy()

    op_params['list_description'] = self.DEF_ONE_GSOC_STAT_MSG
    op_params['public_row_extra'] = lambda entity: {
        'link': redirects.getVisualizeRedirect(entity, op_params),
    }

    if request.GET.get('fmt') == 'json':
      # retrieving data for a list
      return self.getManageStatisticsData(request, [ep_params, op_params], program)

    # fill contents for all the needed lists
    contents = []

    ep_list = helper.lists.getListGenerator(request, ep_params,
        idx=self.DEF_EACH_GSOC_LIST_IDX)
    contents.append(ep_list)

    op_list = helper.lists.getListGenerator(request, op_params,
        idx=self.DEF_ONE_GSOC_LIST_IDX)
    contents.append(op_list)

    return self._list(request, list_params, contents, page_name, context)

  def getManageStatisticsData(self, request, params_collection, program):
    """Returns the list data for manageStats.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      program: program entity for which the lists are generated
    """

    idx = request.GET.get('idx', '')
    idx = int(idx) if idx.isdigit() else -1

    args = order = []
    visibility = 'public'

    if idx == self.DEF_EACH_GSOC_LIST_IDX:
      fields = {
          'access_for_other_programs': ['visible', 'collectable']
          }
    elif idx == self.DEF_ONE_GSOC_LIST_IDX:
      fields = {
          'scope': program,
          'access_for_other_programs' : 'invisible'
          }
    else:
      return responses.jsonErrorResponse(request, "idx not valid")

    params = params_collection[idx]
    contents = helper.lists.getListData(request, params, fields)

    json = simplejson.dumps(contents)

    return responses.jsonResponse(request, json)

  def _manageStatisticsPost(self, request, access_type, page_name=None,
                           params=None, **kwargs):
    """POST method for manage statistics request.
    """

    logic = params['logic']
    post_dict = request.POST

    selections = simplejson.loads(post_dict.get('data', '[]'))
    button_id = post_dict.get('button_id', '')

    modified_entities = []
    for selection in selections:
      entity = logic.getFromKeyName(selection['key'])

      if not entity:
        logging.error('No notification found for %(key)s' % selection)
        continue

      # check if the current user can modify the statistic

      if button_id == 'collect_stats':
        fields = {
            'url_name': params['url_name'],
            'key_name': entity.key().name()
            }

        task_url = '/%(url_name)s/collect_task/%(key_name)s' % fields
        task = task_responses.startTask(task_url)

        if not task:
          logging.error('There was an error. The task is not started')

      elif button_id == 'clear_stats':
        modified_entities.append(logic.clearStatistic(entity))

    db.put(modified_entities)

    return http.HttpResponseRedirect('')

  @view_decorators.merge_params
  @view_decorators.check_access
  def updateOrClearStats(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """Collects one batch of statistic or clears a statistic.
    """

    get_dict = request.GET

    logic = params['logic']
    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']

    statistic = None

    if 'update' in get_dict:
      statistic, _ = logic.collectDispatcher(
          self._getStatisticEntity(link_id, scope_path, logic))

    elif 'clear' in get_dict:
      statistic = logic.clearStatistic(
          self._getStatisticEntity(link_id, scope_path, logic))

    if statistic is not None:
      self._updateCacheList(statistic, scope_path, logic)
      self._updateCache(statistic, link_id, scope_path, logic)

    fields = {
        'url_name': params['url_name'],
        'scope_path': scope_path,
        'link_id': link_id
        }

    if 'show_after_operation' in get_dict:
      return http.HttpResponseRedirect(
             '/%(url_name)s/show/%(scope_path)s/%(link_id)s' % fields)

    return http.HttpResponseRedirect(
           '/%(url_name)s/manage_stats/%(scope_path)s' % fields)

  @view_decorators.merge_params
  @view_decorators.check_access
  def setCollectTask(self, request, access_type, page_name=None,
                     params=None, **kwargs):
    """Starts a statistic collecting task.
    """

    logic = params['logic']
    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']

    fields = {
        'url_name': params['url_name'],
        'scope_path': scope_path,
        'link_id': link_id
        }

    task_url = '/%(url_name)s/collect_task/%(scope_path)s/%(link_id)s' % fields
    task = task_responses.startTask(task_url)#, queue_name='statistic-queue')

    if task is not None:
      return self.json(request, {'response': 'success'})
    else:
      return self.json(request, {'response': 'failure'})

  @view_decorators.merge_params
  @view_decorators.check_access
  def visualize(self, request, access_type, page_name=None, params=None,
                **kwargs):
    """Visualization view for a statistic specified in request params.
    """

    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']
    logic = params['logic']

    statistic = self._getStatisticEntity(link_id, scope_path, logic)

    context = responses.getUniversalContext(request)

    if not logic.checkIfStatisticReady(statistic):
      template = 'soc/error.html'
      context['message'] = self.DEF_NO_VISUALIZATION_MSG_FMT % (statistic.name)
    else:
      responses.useJavaScript(context, params['js_uses_all'])
      context['entity'] = statistic
      context['page_name'] = "Statistic visualization"
      context['link_id'] = statistic.link_id
      context['scope_path'] = statistic.scope_path
      context['visualization_types'] = logic.getVisualizationTypesJson(statistic)

      template = 'soc/statistic/show.html'

      fields = {
          'url_name': params['url_name'],
          'scope_path': kwargs['scope_path'],
          'link_id': 'students_per_degree'
          }

    return responses.respond(request, template, context)

  @view_decorators.merge_params
  @view_decorators.check_access
  def getJsonResponse(self, request, access_type, page_name=None,
                      params=None, filter=None, **kwargs):
    """Returns a JSON response for AJAX calls from client.
    """

    scope_path = kwargs['scope_path']
    if 'link_id' in kwargs:
      link_id = kwargs['link_id']
      post_dict = request.GET
      statistic_name = post_dict['statistic_name']
      data = self._getJsonResponseForStat(link_id, scope_path, statistic_name)
      is_json = False
    else:
      data = self._getJsonResponseForAllStats(scope_path)
      is_json = True

    return self.json(request, data, is_json)

  @view_decorators.merge_params
  def collectTask(self, request, access_type, page_name=None,
                      params=None, **kwargs):
    """Task for collecting statistics that will be executed by Task Queue API.
    """

    logic = params['logic']
    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']

    statistic = self._getStatisticEntity(link_id, scope_path, logic)
    if statistic is None:
      raise task_responses.FatalTaskError

    statistic, completed = logic.collectDispatcher(statistic)

    self._updateCache(statistic, link_id, scope_path, logic)

    if completed:
      self._updateCacheList(statistic, scope_path, logic)
      statistic.put()
    else:
      task_responses.startTask(url=request.path)

    return task_responses.terminateTask()

  @view_decorators.merge_params
  def getVirtualStatistics(self, request, access_type, page_name=None,
                           params=None, **kwargs):
    """For a given statistic a list of possible virtual statistics and
     visualizations is returned.
    """

    logic = params['logic']
    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']

    statistic = self._getStatisticEntity(link_id, scope_path, logic)
    if not statistic:
      return None

    data = logic.getVisualizationTypesJson(statistic)
    return self.json(request, data, False)

  @view_decorators.merge_params
  def getAvailableStatistics(self, request, access_type, page_name=None,
                             params=None, **kwargs):
    """Returns a list of all statistics that the user has access to.
    """

    logic = params['logic']

    data = {}

    programs = program_logic.getForFields()
    key_names = []
    for program in programs:
      fields = {
          'link_id': program.link_id,
          'scope_path': program.scope_path
          }
      key_name = program_logic.getKeyNameFromFields(fields)
      data[key_name] = {
          'name': program.name,
          'statistics': []
          }

    statistics = logic.getForFields()
    for statistic in statistics:
      has_access = self._checkHasStatisticAccess(statistic)
      if has_access:
        data[statistic.scope_path]['statistics'].append({
            'link_id': statistic.link_id,
            'name': statistic.name
            })

    return self.json(request, data)

  @view_decorators.merge_params
  @view_decorators.check_access
  def csvExport(self, request, access_type, page_name=None, params=None, **kwargs):
    """CSV export of a statistic specified in request params.
    """

    link_id = kwargs['link_id']
    scope_path = kwargs['scope_path']
    logic = params['logic']
    data = []

    statistic = self._getStatisticEntity(link_id, scope_path, logic)    
    if statistic:
      data = logic.getCSV(statistic)

    params['export_extension'] = '.csv'
    params['export_content_type'] = 'text/csv'

    file_handler = StringIO.StringIO()
    writer = csv.writer(file_handler, dialect='excel')

    # encode the data to UTF-8 to ensure compatibiliy
    for row in data:
      writer.writerow(row)

    data = file_handler.getvalue()

    return self.download(request, data, "plik", params)

  @view_decorators.merge_params
  def _getJsonResponseForAllStats(self, scope_path, params=None):
    """Returns json response with all statistics for a program.
    """

    logic = params['logic']
    entities = self._getAllStatisticEntitiesForProgram(scope_path, logic)

    data = []
    for entity in entities:
      data.append({'link_id': entity.link_id,
                   'scope_path': entity.scope_path,
                   'name': entity.name})

    return data

  @view_decorators.merge_params
  def _getJsonResponseForStat(self, link_id, scope_path, statistic_name,
                              params=None):
    """Returns json string with data for one statistic.
    """

    logic = params['logic']
    statistic = self._getStatisticEntity(link_id, scope_path, logic)

    if statistic is None:
      return {}

    data_table = logic.getDataTableObject(statistic, statistic_name)
    json_response = data_table.ToJSon()

    return json_response

  def _getProgramInScopeEntity(self, scope_path):
    """Extracts program link_id from scope_path for a statistic.
    """

    path_link_name_match = linkable.PATH_LINK_ID_REGEX.match(scope_path)
    fields = path_link_name_match.groupdict()
    return program_logic.getFromKeyFields(fields)

  def _getStatisticEntity(self, link_id, scope_path, logic):
    """Returns a statistic entity for given fields.
    """

    filter = {
      'link_id': link_id,
      'scope_path': scope_path
    }

    fun =  soc.cache.logic.cache(self._getData)
    entities = fun(logic.getModel(), filter, order=None, logic=logic)

    if entities is not None and len(entities) != 0:
      return entities[0]
    else:
      return None

  def _getAllStatisticEntitiesForProgram(self, scope_path, logic):
    """Returns a list of statistics that can be accessed by a program.
    """

    # There are two types of stats that can be accessed by a program:
    # - stats that are assigned to the particular program
    # - stats that are defined for another program but can be seen by others
    filter = {
        'scope_path': scope_path,
        'access_for_other_programs' : 'invisible'
        }
    fun =  soc.cache.logic.cache(self._getData)
    entities = fun(logic.getModel(), filter, order=None, logic=logic)

    filter = {
        'access_for_other_programs': ['visible', 'collectable']
        }
    entities += fun(logic.getModel(), filter, order=None, logic=logic)

    return entities

  def _updateCache(self, statistic, link_id, scope_path, logic):
    """It updates cache value for a key associated with a specific statistic.
    """

    filter = {
        'link_id': link_id,
        'scope_path': scope_path
        }

    soc.cache.logic.force_cache(logic.getModel(), filter, order=None,
        data=[statistic])

  def _updateCacheList(self, statistic, scope_path, logic):
    """Update list of all statistics in memcache.
    """

    if statistic.access_for_other_programs == 'invisible':
      filter = {
          'scope_path': scope_path,
          'access_for_other_programs': 'invisible'
          }
    else:
      filter = {
          'access_for_other_programs': ['visible', 'collectable']
          }

    entities, _ = soc.cache.logic.get(logic.getModel(), filter,
        order=None)

    if entities is not None:

      for i in range(len(entities)):
        if entities[i].link_id == statistic.link_id:
          entities[i] = statistic
          break

      soc.cache.logic.force_cache(logic.getModel(), filter,
          order=None, data=entities)

  @view_decorators.merge_params
  def _checkHasStatisticAccess(self, statistic, params=None):
    """Checks that the user has access to the specified statistic.
    """

    logic = params['logic']

    id = accounts.getCurrentAccount()
    user = None
    if id:
      user = user_logic.getForAccount(id)

    checker = access.Checker(None)
    checker.setCurrentUser(id, user)

    access_type = statistic.read_access
    has_access = False

    minimal_rights = logic.ACCESS_TYPES.index(access_type)
    for item in logic.ACCESS_TYPES[minimal_rights:]:
      ref_logic = logic.helper.LOGICS_DICT[item]
      try:
        checker.checkHasActiveRole({}, ref_logic.logic)
        has_access = True
        break
      except Exception:
        pass

    return has_access


view = View()

csv_export = view_decorators.view(view.csvExport)
manage_statistics = view_decorators.view(view.manageStatistics)
update_stats = view_decorators.view(view.updateOrClearStats)
visualize = view_decorators.view(view.visualize)
get_json_response = view_decorators.view(view.getJsonResponse)
get_virtual_statistics = view_decorators.view(view.getVirtualStatistics)
get_available_statistics = view_decorators.view(view.getAvailableStatistics)
set_collect_task = view_decorators.view(view.setCollectTask)
public = view_decorators.view(view.public)
create = view_decorators.view(view.create)
delete = view_decorators.view(view.delete)
edit = view_decorators.view(view.edit)
list = view_decorators.view(view.list)
collect_task = task_decorators.task(view.collectTask)

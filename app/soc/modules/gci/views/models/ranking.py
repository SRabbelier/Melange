#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""GSIRanking query functions.
"""

__authors__ = [
  '"Daniel Hans" <dhans@google.com>',
]


from django import forms
from django import http
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts

from soc.tasks import responses as task_responses

from soc.views import out_of_band
from soc.views import helper

from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
from soc.views.models import base

from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.models.task import TaskDifficultyTag
from soc.modules.gci.views.helper import access as gci_access

import soc.modules.gci.logic.models.ranking


class View(base.View):
  """View methods for the Ranking.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the task View class
    to provide the user with the necessary views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)

    rights['any_access'] = ['allow']
    rights['create'] = [('checkIsHostForProgram', [gci_program_logic.logic])]
    rights['edit'] = [('checkIsHostForProgram', [gci_program_logic.logic])]
    rights['show'] = ['any_access']
    rights['force_update'] = ['any_access']#[('checkIsHostForProgram',
        #[gci_program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.ranking.logic

    new_params['name'] = "Ranking"
    new_params['module_name'] = "ranking"
    new_params['sidebar_grouping'] = 'Rankings'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/ranking'

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>force_update)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.force_update',
          'Update ranking'),
        ]

    new_params['extra_dynaexclude'] = [
        'link_id', 'last_data_from', 'raw_data', 'schema']

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Replaces the create Form with the dynamic one.

    For args see base.View.create().
    """

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    # get program entity
    program = gci_program_logic.logic.getFromKeyFields(kwargs)

    dynafields = self.createDynamicDynafields(program, params['logic'])
    dynaproperties = params_helper.getDynaFields(dynafields)

    create_form = dynaform.extendDynaForm(
        dynaform=self._params['create_form'],
        dynaproperties=dynaproperties)

    params['create_form'] = create_form

    if request.method == 'POST':
      return self.createPost(request, context, params)
    else:
      return self.createGet(request, context, params, kwargs)

  def createDynamicDynafields(self, program, logic):
    """Creates dynamic dynafields for based difficulties and bonus.
    """

    dynafields = []
    difficulties = TaskDifficultyTag.get_by_scope(program)
    for difficulty in difficulties:
      dynafields.append({
          'name': difficulty.tag,
          'base': forms.IntegerField,
          'min_value': 0,
          'initial': 0,
          'required': False,
          'group': ugettext('Difficulty'),
          'help_text': ugettext('Number of points for this difficulty level.'),
          })

    bonuses = logic.DEFAULT_BONUSES
    for bonus in bonuses:
      dynafields.append({
          'name': bonus['name'],
          'base': forms.IntegerField,
          'min_value': 0,
          'initial': 0,
          'required': False,
          'label': bonus['pretty_name'],
          'group': ugettext('Bunus'),
          'help_text': ugettext('Number of points for this bonus.'),
          })

    dynafields.append({
        'name': 'link_id',
         'base': forms.fields.CharField,
         'widget': forms.HiddenInput,
         'required': True,
         'initial': program.link_id
        })

    dynafields.append({
        'name': 'scope_path',
         'base': forms.fields.CharField,
         'widget': forms.HiddenInput,
         'required': True,
         'initial': program.scope_path
        })

    return dynafields

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit().
    """

    logic = params['logic']

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    # get ranking entity
    try:
      entity = logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      msg = self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']
          }
      error.message_fmt = error.message_fmt + msg
      return helper.responses.errorResponse(
          error, request, context=context)

    # get program entity
    program = gci_program_logic.logic.getFromKeyFields(kwargs)

    dynafields = self.createDynamicDynafields(program, logic)
    dynaproperties = params_helper.getDynaFields(dynafields)

    create_form = dynaform.extendDynaForm(
        dynaform=self._params['edit_form'],
        dynaproperties=dynaproperties)

    params['edit_form'] = create_form

    if request.method == 'POST':
      return self.editPost(request, entity, context, params=params)
    else:
      return self.editGet(request, entity, context, params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    if entity:
      schema = simplejson.loads(entity.schema)
      for field, value in schema.iteritems():
        if field in form.fields:
          form.fields[field].initial = value

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # set schema dict based on the values of dynamic fields
    schema = {}
    for field, value in fields.items():
      if field not in ['link_id', 'scope_path']:
        schema[field] = value

        # the dynamic fields are not needed in the real model
        del fields[field]


    fields['schema'] = simplejson.dumps(schema)

    program = gci_program_logic.logic.getFromKeyFields(fields)
    if not program.ranking:
      import logging
      logging.error(entity)
      properties = {
          'ranking': entity
          }
      gci_program_logic.logic.updateEntityProperties(program, properties)
    
    # set the scope field
    super(View, self)._editPost(request, entity, fields)

  @decorators.merge_params
  def forceUpdate(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """Creates a new task which updates ranking for the GCI program.
    """

    url = '/tasks/gci/ranking/update'
    context = {
        'link_id': kwargs['link_id'],
        'scope_path': kwargs['scope_path']
        }

    task_responses.startTask(url, 'gci-update', context)

    fields = {
        'url_name': params['url_name'],
        'scope_path': kwargs['scope_path'],
        'link_id': kwargs['link_id'],
        }

    return http.HttpResponseRedirect(
        '/%(url_name)s/edit/%(scope_path)s/%(link_id)s' % fields)    
    
view = View()

create = decorators.view(view.create)
edit = decorators.view(view.edit)
force_update = decorators.view(view.forceUpdate)

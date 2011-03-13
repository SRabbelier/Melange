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
"""Views for an admin to manage data seeding operations.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from django.utils import simplejson
from django.http import HttpResponseForbidden, HttpResponse

from soc.modules.seeder.views.helper import access
from soc.modules.seeder.logic.models import logic as seeder_models_logic
from soc.modules.seeder.logic.providers import logic as seeder_providers_logic
from soc.modules.seeder.logic.seeder import logic as seeder_logic
from soc.modules.seeder.logic.seeder import Error

from soc.views.models import base
from soc.views.helper import responses
from soc.views.helper import decorators as view_decorators
from soc.views.sitemap import sidebar

from soc.logic import dicts

# pylint: disable=R0201
class View(base.View):
  """View methods for the Data Seeder.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Args:
      params: a dict with params for this View

    """

    rights = access.DataSeederChecker(params)

    rights['home'] = ['checkIsDeveloper']

    new_params = {}

    new_params['logic'] = seeder_logic
    new_params['rights'] = rights
    new_params['scope_view'] = None
    new_params['name'] = 'seeder'
    new_params['sidebar_grouping'] = 'Data Seeder'
    new_params['module_package'] = 'soc.modules.seeder.views'
    new_params['module_name'] = 'seeder'

    new_params['url_name'] = 'seeder'
    new_params['link_id_arg_pattern'] = ''
    new_params['link_id_pattern_core'] = ''
    new_params['key_fields_pattern'] = ''
    new_params['scope_path_pattern'] = ''
    new_params['sans_link_id_pattern'] = ''

    patterns = []
    patterns += [(r'^%(url_name)s/get_data$',
         '%(module_package)s.%(module_name)s.get_data',
         'Get Data'),
         (r'^%(url_name)s/home$',
         '%(module_package)s.%(module_name)s.home',
         'Manage Data Seeder'),
         (r'^%(url_name)s/seed$',
         '%(module_package)s.%(module_name)s.seed',
         'Start seeding'),
         (r'^%(url_name)s/echo$',
         '%(module_package)s.%(module_name)s.echo',
         'Echo'),
         (r'^%(url_name)s/test_provider$',
         '%(module_package)s.%(module_name)s.test_provider',
         'Test data provider'),
         (r'^%(url_name)s/validate_configuration_sheet$',
         '%(module_package)s.%(module_name)s.validate_configuration_sheet',
         'Validate configuration sheet'),
         ]


    new_params['django_patterns'] = None
    new_params['django_patterns_defaults'] = []
    new_params['extra_django_patterns'] = patterns

    new_params['sidebar'] = None
    new_params['sidebar_defaults'] = patterns
    new_params['sidebar_additional'] = patterns
    new_params['sidebar_developer'] = patterns

    params = dicts.merge(params, new_params)
    
    # FIXME : temporarily added due to errors 
    self._params = params
    # FIXME : temporarily commented due to errors 
    #super(View, self).__init__(params=params)

  @view_decorators.merge_params
  def getData(self, request, page_name=None, params=None):
    """Returns a JSON object containing information regarding models,
    properties and supported data providers.
    """
    contents = {}

    contents['models'] = seeder_models_logic.getModelsData()
    contents['providers'] = seeder_providers_logic.getProvidersData()

    # TODO(sttwister): Remove the indent on deployment
    json = simplejson.dumps(contents, indent=2)

    return responses.jsonResponse(request, json)

  @view_decorators.merge_params
  def home(self, request, page_name=None, params=None, **kwargs):
    """Renders the home page for seeding operations.
    """
    template = 'modules/seeder/home.html'
    configuration_sheet = request.FILES.get('configuration_sheet', None);
    if configuration_sheet:
      configuration_sheet = configuration_sheet.read()
    else:
      configuration_sheet = ''

    context = responses.getUniversalContext(request)
    context['configuration_sheet'] = simplejson.dumps(configuration_sheet)

    # FIXME : temporarily comment due to errors 
    #responses.useJavaScript(context, params['js_uses_all'])

    return responses.respond(request, template, context)

  @view_decorators.merge_params
  def getSidebarMenus(self, id, user, params=None):
    """Returns the extra menu's for this view.

    A menu item is generated for each program that is currently
    running. The public page for each program is added as menu item,
    as well as all public documents for that program.

    Args:
      params: a dict with params for this View.
    """

    rights = params['rights']

    menus = []

    rights.setCurrentUser(id, user)

    items = [('/seeder/home', 'Manage Data Seeder', '')]
    items = sidebar.getSidebarMenu(id, user, items, params=params)

    menu = {}
    menu['heading'] = 'Data Seeder'
    menu['items'] = items
    menu['group'] = 'Developer'
    menu['collapse'] = 'collapse'
    menus.append(menu)

    return menus

  @view_decorators.merge_params
  def seed(self, request, page_name=None, params=None, **kwargs):
    """Starts a seeding operation using the supplied JSON data.
    """
    if request.is_ajax():
      data = request.POST.get('data', None)
      if data:
        try:
          id = seeder_logic.seedFromJSON(data)
        except Error, ex:
          return responses.jsonErrorResponse(request, ex.args[0])
      else:
        return responses.jsonErrorResponse(request, 'No data supplied!')
    else:
      return HttpResponseForbidden()

    response = simplejson.dumps({'result': 'success', 'id': id})
    return responses.jsonResponse(request, response)

  @view_decorators.merge_params
  def echo(self, request, page_name=None, params=None, **kwargs):
    """Echoes the JSON configuration sheet back to the browser.
    """
    json = request.POST.get('data', None)
    if json:
      try:
        data = simplejson.loads(json)
      except ValueError:
        return HttpResponse('Invalid JSON!')

      response = HttpResponse(json, mimetype='application/json')
      response['Content-Disposition'] = 'attachment; filename=configuration.json'
      return response
    else:
      return HttpResponse('No data supplied!')

  @view_decorators.merge_params
  def testProvider(self, request, page_name=None, params=None, **kwargs):
    """Tests a parameter configuration for a data provider and return a sample
    value or an error message as JSON data.
    """
    if request.is_ajax():
      json = request.POST.get('data', None)
      if json:
        try:
          data = simplejson.loads(json)
        except ValueError:
          return responses.jsonErrorResponse(request, 'Invalid JSON!')

        try:
          value = seeder_logic.testProvider(data)
        except Error, e:
          return responses.jsonErrorResponse(request, e.args[0])
      else:
        return responses.jsonErrorResponse(request, 'No data supplied!')
    else:
      return HttpResponseForbidden()

    response = simplejson.dumps({
      'result': 'success',
      'value': value
    })
    return responses.jsonResponse(request, response)

  @view_decorators.merge_params
  def validateConfigurationSheet(self, request, page_name=None, params=None,
                             **kwargs):
    """Tests a configuration sheet for validity and report any errors as JSON
    data.
    """
    if request.is_ajax():
      json = request.POST.get('data', None)
      if json:
        try:
          data = simplejson.loads(json)
        except ValueError:
          return responses.jsonErrorResponse(request, 'Invalid JSON!')

        try:
          seeder_logic.validateConfiguration(data)
        except Error, e:
          return responses.jsonErrorResponse(request, e.args[0])
      else:
        return responses.jsonErrorResponse(request, 'No data supplied!')
    else:
      return HttpResponseForbidden()

    response = simplejson.dumps({
      'result': 'success'
    })
    return responses.jsonResponse(request, response)


view = View()

get_data = view_decorators.view(view.getData)
home = view_decorators.view(view.home)
seed = view_decorators.view(view.seed)
echo = view_decorators.view(view.echo)
test_provider = view_decorators.view(view.testProvider)
validate_configuration_sheet = view_decorators.view(
    view.validateConfigurationSheet)

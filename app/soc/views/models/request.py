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

"""Views for Requests.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import http
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.logic.models.request import logic as request_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base


class View(base.View):
  """View methods for the Request model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['listSelf'] = ['checkIsUser']
    rights['create'] = ['deny']
    rights['edit'] = ['checkIsDeveloper']
    rights['process_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']])]
    rights['list'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    rights['roles'] = ['checkIsUser']

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = request_logic

    new_params['name'] = "Request"

    new_params['sidebar_developer'] = [('/%s/list', 'List %(name_plural)s',
        'list')]

    new_params['create_template'] = ['soc/request/create.html']

    new_params['extra_dynaexclude'] = ['user', 'role', 'group', 'status']

    patterns = [
        (r'^%(url_name)s/(?P<access_type>process_invite)/(?P<id>[0-9]*)$',
          'soc.views.models.%(module_name)s.process_invite',
          'Process Invite to become')]

    new_params['extra_django_patterns'] = patterns

    new_params['invite_processing_template'] = 'soc/request/process_invite.html'
    new_params['request_processing_template'] = \
        'soc/request/process_request.html'

    new_params['public_field_extra'] = lambda entity: {
        "user": "%s (%s)" % (entity.user.name, entity.user.link_id),
        "for": entity.group.name,
    }
    new_params['public_field_keys'] = ["role", "user", "for",
                                       "status", "created_on"]
    new_params['public_field_names'] = ["Role", "User", "For",
                                        "Status", "Created On"]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special forms for invite and requests
    self._params['request_form'] = self._params['create_form']

    updated_fields = {
        'user_id': widgets.ReferenceField(reference_url='user'),
        'clean_user_id': cleaning.clean_existing_user('user_id'),
        }

    invite_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynaproperties = updated_fields)
    # reverse the fields so that user_id field comes first
    invite_form.base_fields.keyOrder.reverse()

    self._params['invite_form'] = invite_form

  def _edit(self, request, entity, context, params):
    """Hook for edit View.

    Changes the page name to contain request information.

    For args see base.View._edit().
    """

    # TODO: editing request, so you can also edit message
    context['page_name'] = '%s to become a %s for %s' % (context['page_name'],
                                                         entity.role_verbose,
                                                         entity.scope.name)

  @decorators.merge_params
  @decorators.check_access
  def processInvite(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Creates the page upon which an invite can be processed.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    from soc.views.models.role import ROLE_VIEWS

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])

    # get the request entity using the information from kwargs
    request_entity = request_logic.getFromIDOr404(int(kwargs['id']))

    role_params = ROLE_VIEWS[request_entity.role].getParams()

    # set the page name using the request_entity
    context['page_name'] = '%s %s for %s' % (page_name, 
        role_params['name'], request_entity.group.name)

    get_dict = request.GET

    if 'status' in get_dict.keys():
      if get_dict['status'] == 'rejected':
        # this invite has been rejected mark as rejected
        request_logic.updateEntityProperties(request_entity, {
            'status': 'rejected'})

        # redirect to user request overview
        return http.HttpResponseRedirect('/user/requests')

    # put the entity in the context
    context['entity'] = request_entity
    context['module_name'] = params['module_name']
    context['role_name'] = role_params['name']
    context['invite_accepted_redirect'] = (
        redirects.getInviteAcceptedRedirect(request_entity, self._params))

    #display the invite processing page using the appropriate template
    template = params['invite_processing_template']

    return responses.respond(request, template, context=context)

  def getListSelfData(self, request, uh_params, ar_params):
    """Returns the list data for getListSelf.
    """

    idx = request.GET.get('idx', '')
    idx = int(idx) if idx.isdigit() else -1

    # get the current user
    user_entity = user_logic.logic.getForCurrentAccount()

    # only select the Invites for this user that haven't been handled yet
    # pylint: disable-msg=E1103
    filter = {'user': user_entity}

    if idx == 0:
      filter['status'] = 'group_accepted'
      params = uh_params
    elif idx == 1:
      filter['status'] = 'new'
      params = ar_params
    else:
      return responses.jsonErrorResponse(request, "idx not valid")

    contents = helper.lists.getListData(request, params, filter, 'public')
    json = simplejson.dumps(contents)

    return responses.jsonResponse(request, json)

  @decorators.merge_params
  @decorators.check_access
  def listSelf(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Displays the unhandled requests for this user.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used
    """

    # construct the Unhandled Invites list

    uh_params = params.copy()
    uh_params['public_row_extra'] = lambda entity: {
        "link": redirects.getInviteProcessRedirect(entity, None),
    }
    uh_params['list_description'] = ugettext(
        "An overview of your unhandled invites.")

    # construct the Open Requests list

    ar_params = params.copy()
    ar_params['public_row_action'] = {}
    ar_params['public_row_extra'] = lambda x: {}
    ar_params['list_description'] = ugettext(
        "List of your pending requests.")

    if request.GET.get('fmt') == 'json':
      return self.getListSelfData(request, uh_params, ar_params)

    uh_list = helper.lists.getListGenerator(request, uh_params, idx=0)
    ar_list = helper.lists.getListGenerator(request, ar_params, idx=1)

    # fill contents with all the needed lists
    contents = [uh_list, ar_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
list_self = decorators.view(view.listSelf)
process_invite = decorators.view(view.processInvite)
public = decorators.view(view.public)
export = decorators.view(view.export)


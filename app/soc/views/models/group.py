#!/usr/bin/python2.5
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

"""Views for Groups.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views.helper import decorators
from soc.views.helper import lists as list_helper
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models.request import view as request_view


class View(base.View):
  """View methods for the Group model.
  """

  # TODO(ljvderijk) add sidebar entry for listRequests to each group

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}

    new_params['extra_dynaexclude'] = ['founder',
      # TODO(tlarsen): these need to be enabled once a button to a list
      #   selection "interstitial" page is implemented, see:
      #     http://code.google.com/p/soc/issues/detail?id=151
      'home', 'tos', 'member_template']
    new_params['edit_extra_dynafields'] = {
        'founded_by': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=False),
        }

    #set the extra_django_patterns and include the one from params
    patterns = params.get('extra_django_patterns')

    if not patterns:
      patterns = []

    patterns += [
        (r'^%(url_name)s/(?P<access_type>list_requests)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.list_requests',
        'List of requests for %(name)s')]

    new_params['extra_django_patterns'] = patterns

    # TODO(tlarsen): Add support for Django style template lookup
    new_params['public_template'] = 'soc/group/public.html'

    new_params['list_row'] = 'soc/group/list/row.html'
    new_params['list_heading'] = 'soc/group/list/heading.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the founded_by with data from the entity
    form.fields['founded_by'].initial = entity.founder.name
    super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # only if we are creating a new entity we should fill in founder
      account = users.get_current_user()
      user = user_logic.logic.getForFields({'account': account}, unique=True)
      fields['founder'] = user

    super(View, self)._editPost(request, entity, fields)

  @decorators.merge_params
  @decorators.check_access
  def listRequests(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Gives an overview of all the requests for a specific group.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # set the pagename to include the link_id
    page_name = '%s %s' %(page_name, kwargs['link_id'])

    role_names = params['roles_logic'].keys()

    # list all incoming requests
    filter = {
        'role': role_names,
        'state': 'new'
        }

    # create the list parameters
    inc_req_params = request_view.getParams()

    # define the list redirect action to the request processing page
    inc_req_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    inc_req_params['list_description'] = ugettext(
        "An overview of the %(name)s's incoming requests." % params)
    
    inc_req_content = list_helper.getListContent(
        request, inc_req_params, filter, 0)

    # list all outstanding invites
    filter = {
        'role': role_names,
        'state': 'group_accepted'
        }

    # create the list parameters
    out_inv_params = request_view.getParams()

    # define the list redirect action to the request processing page
    out_inv_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    out_inv_params['list_description'] = ugettext(
        "An overview of the %(name)s's outstanding invites." % params)

    out_inv_content = list_helper.getListContent(
        request, out_inv_params, filter, 1)

    # list all ignored requests
    filter = {
        'role': role_names,
        'state': 'ignored'
        }

    # create the list parameters
    ignored_params = request_view.getParams()

    # define the list redirect action to the request processing page
    ignored_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    ignored_params['list_description'] = ugettext(
        "An overview of the %(name)s's ignored requests." % params)
    
    ignored_content = list_helper.getListContent(
        request, ignored_params, filter, 2)

    contents = [inc_req_content, out_inv_content, ignored_content]

    return self._list(request, params, contents, page_name)

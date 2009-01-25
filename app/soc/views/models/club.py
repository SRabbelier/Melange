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

"""Views for Clubs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api import users

from django import http
from django import forms
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.logic.models import club_app as club_app_logic
from soc.logic.models import club as club_logic
from soc.logic.models import request as request_logic
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists as list_helper
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models.request import view as request_view

import soc.logic.models.club
import soc.views.helper


class View(base.View):
  """View methods for the Club model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['create'] = [access.checkIsDeveloper]
    rights['edit'] = [access.checkIsClubAdminForClub]
    rights['delete'] = [access.checkIsDeveloper]
    rights['list'] = [access.checkIsDeveloper]
    rights['list_requests'] = [access.checkIsClubAdminForClub]
    rights['applicant'] = [access.checkIsApplicationAccepted(club_app_logic)]

    new_params = {}
    new_params['logic'] = soc.logic.models.club.logic
    new_params['rights'] = rights
    new_params['name'] = "Club"

    patterns = []

    patterns += [(r'^%(url_name)s/(?P<access_type>applicant)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.applicant', 
        "%(name)s Creation via Accepted Application"),
        (r'^%(url_name)s/(?P<access_type>list_requests)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.list_requests',
        'List of requests for %(name)s')]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['founder', 'home']
    new_params['edit_extra_dynafields'] = {
        'founded_by': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=False),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for applicants
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False)}

    applicant_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynafields = updated_fields)

    params['applicant_create_form'] = applicant_create_form

  @decorators.merge_params
  @decorators.check_access
  def applicant(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Handles the creation of a club via an approved club application.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.applicantPost(request, context, params, **kwargs)
    else:
      # request.method == 'GET'
      return self.applicantGet(request, context, params, **kwargs)

  def applicantGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the creation of a club via an
    approved club application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # find the application
    key_fields = club_app_logic.logic.getKeyFieldsFromDict(kwargs)
    application = club_app_logic.logic.getFromFields(**key_fields)

    # extract the application fields
    field_names = application.properties().keys()
    fields = dict( [(i, getattr(application, i)) for i in field_names] )

    # create the form using the fields from the application as the initial value
    form = params['applicant_create_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def applicantPost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the creation of a club via an
    approved club application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # populate the form using the POST data
    form = params['applicant_create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, fields = soc.views.helper.forms.collectCleanedFields(form)

    # fill in the founder of the club
    account = users.get_current_user()
    user = user_logic.logic.getForFields({'account': account}, unique=True)
    fields['founder'] = user

    if not key_name:
      key_fields =  self._logic.getKeyFieldsFromDict(fields)
      key_name = self._logic.getKeyNameForFields(key_fields)

    # create the club entity
    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # redirect to notifications list to see the admin invite
    return http.HttpResponseRedirect('/notification/list')


  @decorators.merge_params
  @decorators.check_access
  def listRequests(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Gives an overview of all the requests for a specific club.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # set the pagename to include the link_id
    page_name = '%s %s' %(page_name, kwargs['link_id'])

    club_roles = ['club_admin', 'club_member']

    # list all incoming requests
    filter = {
        'role': club_roles,
        'state': 'new'
        }

    # create the list parameters
    inc_req_params = request_view.getParams()

    # define the list redirect action to the request processing page
    inc_req_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    inc_req_params['list_description'] = ugettext(
        "An overview of the club's incoming requests.")
    
    inc_req_content = list_helper.getListContent(
        request, inc_req_params, filter, 0)

    # list all outstanding invites
    filter = {
        'role': club_roles,
        'state': 'group_accepted'
        }

    # create the list parameters
    out_inv_params = request_view.getParams()

    # define the list redirect action to the request processing page
    out_inv_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    out_inv_params['list_description'] = ugettext(
        "An overview of the club's outstanding invites.")

    out_inv_content = list_helper.getListContent(
        request, out_inv_params, filter, 1)

    # list all ignored requests
    filter = {
        'role': club_roles,
        'state': 'ignored'
        }

    # create the list parameters
    ignored_params = request_view.getParams()

    # define the list redirect action to the request processing page
    ignored_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    ignored_params['list_description'] = ugettext(
        "An overview of the club's ignored requests.")
    
    ignored_content = list_helper.getListContent(
        request, ignored_params, filter, 2)


    contents = [inc_req_content, out_inv_content, ignored_content]

    return self._list(request, params, contents, page_name)


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


view = View()

applicant = view.applicant
create = view.create
delete = view.delete
edit = view.edit
list = view.list
list_requests = view.listRequests
public = view.public
export = view.export
pick = view.pick

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

"""Views for Organizations.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Augie Fackler" <durin42@gmail.com>',
    '"Mario Ferraro" <fadinlight@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django import http
from django.utils import simplejson
from django.utils import html
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import accounts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import organization as org_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import group

import soc.models.organization
import soc.logic.models.organization

class View(group.View):
  """View methods for the Organization model.
  """

  DEF_ACCEPTED_PROJECTS_MSG_FMT = ugettext("These projects have"
      " been accepted into %s. You can learn more about"
      " each project by visiting the links below.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    from soc.views.models import program as program_view

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasRoleForKeyFieldsAsScope',
                           org_admin_logic.logic,),
                      ('checkGroupIsActiveForLinkId', org_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasRoleForKeyFieldsAsScope',
                                org_admin_logic.logic)]
    rights['list_roles'] = [('checkHasRoleForKeyFieldsAsScope',
                             org_admin_logic.logic)]

    new_params = {}
    new_params['logic'] = soc.logic.models.organization.logic
    new_params['rights'] = rights

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Organization"
    new_params['url_name'] = "org"
    new_params['document_prefix'] = "org"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['public_template'] = 'soc/organization/public.html'
    new_params['home_template'] = 'soc/organization/home.html'

    new_params['sans_link_id_public_list'] = True

    patterns = []

    patterns += [
        (r'^%(url_name)s/(?P<access_type>apply_mentor)/%(scope)s$',
        '%(module_package)s.%(module_name)s.apply_mentor',
        "List of all %(name_plural)s you can apply to"),
        (r'^%(url_name)s/(?P<access_type>list_proposals)/%(key_fields)s$',
        '%(module_package)s.%(module_name)s.list_proposals',
        "List of all Student Proposals for "),
        (r'^%(url_name)s/(?P<access_type>applicant)/%(scope)s$',
        '%(module_package)s.%(module_name)s.applicant', 
        "%(name)s Creation via Accepted Application"),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Organization Link ID',
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
                                   required=True),
        'description': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'clean_description': cleaning.clean_html_content('description'),
        'clean_ideas': cleaning.clean_url('ideas'),
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            soc.logic.models.organization),
        }

    new_params['edit_extra_dynaproperties'] = {
        'clean': cleaning.clean_refs(params if params else new_params,
                                     ['home_link_id'])
        }

    new_params['public_field_extra'] = lambda entity: {
        'ideas': lists.urlize(entity.ideas, 'Click Here'),
    }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    self._params['public_field_keys'] = self._params['select_field_keys'] = [
        "name", "link_id", "short_name", "ideas"
    ]
    self._params['public_field_names'] = self._params['select_field_names'] = [
        "Name", "Link ID", "Short Name", "Ideas Page"
    ]
    self._params['select_field_extra'] = self._params['public_field_extra']
    self._params['select_row_action'] = {
        "type": "redirect_custom",
        "parameters": dict(new_window=True),
    }
    self._params['select_row_extra'] = lambda entity: {
        "link": redirects.getRequestRedirectForRole(
            entity, params['mentor_url_name'])
    }

  def _postCreate(self, request, entity):
    """See base.View._postCreate.
    """

    from soc.logic.models.document import logic as document_logic

    bold = lambda x: "<b>%s</b>: " % x

    parts = [
        bold("Name") + entity.name,
        bold("Registered by") + entity.founder.name,
        bold("Home page url") + str(entity.home_page),
        bold("Email") + entity.email,
        bold("Public mailing list") + entity.pub_mailing_list,
        bold("Public irc channel") + entity.irc_channel ,
        bold("Description") + entity.description ,
        bold("Development mailing list") + entity.dev_mailing_list,
        bold("Ideas list") + str(entity.ideas),
        bold("Application template") + entity.contrib_template,
        ]
    content = '<br/>'.join(parts)

    home_document = document_logic.updateOrCreateFromFields({
        'link_id': 'home',
        'scope_path': entity.key().id_or_name(),
        'scope': entity,
        'author': entity.founder,
        'title': 'Home Page for %s' % entity.name,
        'short_name': 'Home',
        'content': content,
        'prefix': self._params['document_prefix'],
        'read_access': 'public',
        'write_access': 'admin',
        'home_for': entity,
        'modified_by': entity.founder,
        })

    self._logic.updateEntityProperties(entity, {'home': home_document})

    super(View, self)._postCreate(request, entity)

  @decorators.merge_params
  @decorators.check_access
  def applicant(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Handles the creation of an Organization via an approved application.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    get_dict = request.GET
    record_id = get_dict.get('id', None)

    org_app_logic = params['org_app_logic']
    record_logic = org_app_logic.getRecordLogic()

    if not record_id or not record_id.isdigit():
      raise out_of_band.Error('No valid OrgAppRecord ID specified.')
    else:
      record_entity =  record_logic.getFromIDOr404(int(record_id))

    if request.method == 'POST':
      return self.applicantPost(request, context, params,
                                record_entity, **kwargs)
    else:
      # request.method == 'GET'
      return self.applicantGet(request, context, params,
                               record_entity, **kwargs)

  def applicantGet(self, request, context, params, record_entity, **kwargs):
    """Handles the GET request concerning the creation of an Organization via
    an approved Organization application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      record_entity: OrgAppRecord entity
      kwargs: the Key Fields for the specified entity
    """

    # extract the application fields
    fields = {'name': record_entity.name,
              'description': record_entity.description,
              'home_page': record_entity.home_page,
              'scope_path': record_entity.survey.scope.key().id_or_name(),
              }
    # use the extracted fields to initialize the form
    form = params['create_form'](initial=fields)

    context['scope_path'] = kwargs['scope_path']

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def applicantPost(self, request, context, params, record_entity, **kwargs):
    """Handles the POST request concerning the creation of an Organization via
    an approved Organization application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      record_entity: OrgAppRecord entity
      kwargs: the Key Fields for the specified entity
    """

    from soc.logic.helper import org_app_survey as org_app_helper

    # populate the form using the POST data
    form = params['create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, fields = soc.views.helper.forms.collectCleanedFields(form)

    # do post processing
    self._applicantPost(request, context, fields)

    if not key_name:
      key_name = self._logic.getKeyNameFromFields(fields)

    # create the Organization entity
    org_entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # complete the application and sent out the OrgAdmin invites
    record_logic = params['org_app_logic'].getRecordLogic()
    org_app_helper.completeApplication(record_entity, record_logic, org_entity,
                                       params['org_admin_role_name'])

    # redirect to notifications list to see the admin invite
    return http.HttpResponseRedirect('/notification/list')

  def _applicantPost(self, request, context, fields):
    """Performs any required processing on the entity to post its edit page.

    Args:
      request: the django request object
      context: the context for the webpage
      fields: the new field values
    """
    self._editPost(request, None, fields)

  @decorators.merge_params
  @decorators.check_access
  def applyMentor(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows a list of all organizations and you can choose one to
       apply to become a mentor.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    list_params = params.copy()
    list_params['list_description'] = ugettext('Choose an Organization which '
        'you want to become a Mentor for.')

    filter = {'scope_path': kwargs['scope_path'],
              'status' : 'active'}

    return self.list(request, 'allow',
        page_name, params=list_params, filter=filter, visibility='select')


  @decorators.merge_params
  @decorators.check_access
  def listPublic(self, request, access_type, page_name=None,
                 params=None, filter=None, **kwargs):
    """See base.View.list.
    """

    account = accounts.getCurrentAccount()
    user = user_logic.logic.getForAccount(account) if account else None

    try:
      rights = self._params['rights']
      rights.setCurrentUser(account, user)
      rights.checkIsHost()
      is_host = True
    except out_of_band.Error:
      is_host = False

    params = params.copy()

    if is_host:
      params['public_row_extra'] = lambda entity: {
          'link': redirects.getAdminRedirect(entity, params)
      }
    else:
      params['public_row_extra'] = lambda entity: {
          'link': redirects.getPublicRedirect(entity, params)
      }

    new_filter = {}

    new_filter['scope_path'] = kwargs['scope_path']
    new_filter['status'] = 'active'
    filter = dicts.merge(filter, new_filter)

    return self.list(request, 'allow', page_name=page_name,
                      params=params, filter=filter)


view = View()

admin = responses.redirectLegacyRequest
apply_mentor = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
home = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
list_proposals = responses.redirectLegacyRequest
list_public = responses.redirectLegacyRequest
list_requests = responses.redirectLegacyRequest
list_roles = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest
pick = responses.redirectLegacyRequest

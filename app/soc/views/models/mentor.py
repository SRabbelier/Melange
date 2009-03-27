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

"""Views for Organization Mentors.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.models import organization as org_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import params as params_helper
from soc.views.helper import widgets
from soc.views.models import organization as org_view
from soc.views.models import role

import soc.logic.models.mentor
import soc.logic.models.org_admin


class View(role.View):
  """View methods for the Organization Mentors model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasActiveRoleForScope', 
                       soc.logic.models.mentor.logic),
        ('checkIsMyEntity', soc.logic.models.mentor.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasActiveRoleForScope',
                         soc.logic.models.org_admin.logic)]
    rights['accept_invite'] = [('checkCanCreateFromRequest', 'mentor'),
        'checkIsNotStudentForProgramOfOrg']
    rights['request'] = ['checkIsNotStudentForProgramOfOrg',
        ('checkCanMakeRequestToGroup', org_logic)]
    rights['process_request'] = [
        ('checkHasActiveRoleForScope', soc.logic.models.org_admin.logic),
        ('checkCanProcessRequest', 'mentor')]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [soc.logic.models.mentor.logic,
             soc.logic.models.org_admin.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.mentor.logic
    new_params['group_logic'] = org_logic.logic
    new_params['group_view'] = org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = org_view

    new_params['name'] = "Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['extra_dynaexclude'] = ['agreed_to_tos', 'program']

    new_params['create_dynafields'] = [
        {'name': 'scope_path',
         'base': forms.fields.CharField,
         'widget': forms.HiddenInput,
         'required': True,
         },
        {'name': 'mentor_agreement',
         'base': forms.fields.CharField,
         'required': False,
         'widget': widgets.AgreementField,
         'group': ugettext("5. Terms of Service"),
         },
        {'name': 'agreed_to_mentor_agreement',
         'base': forms.fields.BooleanField,
         'initial': False,
         'required':True,
         'label': ugettext('I agree to the Mentor Agreement'),
         'group': ugettext("5. Terms of Service"),
         },
        ]

    new_params['allow_requests_and_invites'] = True
    new_params['show_in_roles_overview'] = True

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # register the role with the group_view
    params['group_view'].registerRole(params['module_name'], self)

    # create and store the special form for invited users
    dynafields = [
        {'name': 'link_id',
         'base': forms.CharField,
         'widget': widgets.ReadOnlyInput(),
         'required': False,
         },
        {'name': 'mentor_agreement',
         'base': forms.fields.Field,
         'required': False,
         'widget': widgets.AgreementField,
         'group': ugettext("5. Terms of Service"),
        },
        ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    invited_create_form = dynaform.extendDynaForm(
        dynaform=self._params['create_form'],
        dynaproperties=dynaproperties)

    params['invited_create_form'] = invited_create_form

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['user'].link_id

      group_logic = self._params['group_logic']
      group_entity = group_logic.getFromKeyName(fields['scope_path'])
      fields['program'] = group_entity.scope

    fields['agreed_to_tos'] = fields['agreed_to_mentor_agreement']

    super(View, self)._editPost(request, entity, fields)

  def _acceptInvitePost(self, fields, request, context, params, **kwargs):
    """Fills in the fields that were missing in the invited_created_form.
    
    For params see base.View._acceptInvitePost()
    """

    # fill in the appropriate fields that were missing in the form
    fields['user'] = fields['link_id']
    fields['link_id'] = fields['user'].link_id
    fields['agreed_to_tos'] = fields['agreed_to_mentor_agreement']

    group_logic = params['group_logic']
    group_entity = group_logic.getFromKeyName(fields['scope_path'])
    fields['program'] = group_entity.scope

  def _editGet(self, request, entity, form):
    """Sets the content of the agreed_to_tos_on field and replaces.

    Also replaces the agreed_to_tos field with a hidden field when the ToS has been signed.
    For params see base.View._editGet().
    """

    if entity.agreed_to_tos:
      form.fields['agreed_to_mentor_agreement'] = forms.fields.BooleanField(
          widget=forms.HiddenInput, initial=entity.agreed_to_tos,
          required=True)

    super(View, self)._editGet(request, entity, form)

  def _editContext(self, request, context):
    """See base.View._editContext.
    """

    entity = context['entity']
    form = context['form']

    if 'scope_path' in form.initial:
      scope_path = form.initial['scope_path']
    elif 'scope_path' in request.POST:
      scope_path = request.POST['scope_path']
    else:
      form.fields['mentor_agreement'] = None
      return

    entity = org_logic.logic.getFromKeyName(scope_path)

    if not (entity and entity.scope and entity.scope.mentor_agreement):
      return

    agreement = entity.scope.mentor_agreement

    content = agreement.content
    params = {'url_name': 'document'}

    widget = form.fields['mentor_agreement'].widget
    widget.text = content
    widget.url = redirects.getPublicRedirect(agreement, params)


view = View()

accept_invite = decorators.view(view.acceptInvite)
admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
invite = decorators.view(view.invite)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
process_request = decorators.view(view.processRequest)
request = decorators.view(view.request)
public = decorators.view(view.public)
export = decorators.view(view.export)


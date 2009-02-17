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

"""Views for Student.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import program as program_logic
from soc.logic.models import student as student_logic
from soc.logic.models import user as user_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import program as program_view
from soc.views.models import role

import soc.logic.models.student


class View(role.View):
  """View methods for the Student model.
  """


  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasActiveRoleForScope', student_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod', ['student_signup', 'scope_path']),
        'checkIsNotParticipatingInProgramInScope',
        ]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [soc.logic.models.host.logic,
             soc.logic.models.org_admin.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.student.logic
    new_params['group_logic'] = program_logic.logic
    new_params['group_view'] = program_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect
    new_params['manage_redirect'] = redirects.getUserRolesRedirect

    new_params['name'] = "Student"
    new_params['module_name'] = "student"
    new_params['sidebar_grouping'] = 'Students'

    # add apply pattern
    patterns = [(r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.apply',
        'Become a %(name)s'),]
    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['agreed_to_tos', 'school']

    new_params['create_extra_dynafields'] = {
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'student_agreement': forms.fields.CharField(required=False,
            widget=widgets.AgreementField),
        'agreed_to_student_agreement': forms.fields.BooleanField(
            initial=False, required=True,
            label=ugettext('I agree to the Student Agreement')),
        }

    new_params['show_in_roles_overview'] = True

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for users
    updated_fields = {
        'link_id': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'clean_link_id': cleaning.clean_user_is_current('link_id')
        }

    user_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynafields = updated_fields)

    self._params['user_create_form'] = user_create_form


  @decorators.merge_params
  @decorators.check_access
  def apply(self, request, access_type,
           page_name=None, params=None, **kwargs):
    """Handles student role creation for the current user.
    """

    user_entity = user_logic.logic.getForCurrentAccount()
    params['create_form'] = params['user_create_form']

    return self.create(request, access_type='unspecified', page_name=page_name,
        params=params, link_id=user_entity.link_id, **kwargs)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['user'].link_id

    fields['agreed_to_tos'] = fields['agreed_to_student_agreement']

    super(View, self)._editPost(request, entity, fields)

  def _editGet(self, request, entity, form):
    """Sets the content of the agreed_to_tos_on field and replaces.

    Also replaces the agreed_to_tos field with a hidden field when the ToS has been signed.
    For params see base.View._editGet().
    """

    if entity.agreed_to_tos:
      form.fields['agreed_to_student_agreement'] = forms.fields.BooleanField(
          widget=forms.HiddenInput, initial=entity.agreed_to_tos,
          required=True)

    super(View, self)._editGet(request, entity, form)

  def _editContext(self, request, context):
    """See base.View._editContext().
    """

    entity = context['entity']
    form = context['form']

    if 'scope_path' in form.initial:
      scope_path = form.initial['scope_path']
    elif 'scope_path' in request.POST:
      # TODO do this nicely
      scope_path = request.POST['scope_path']
    else:
      # TODO is this always sufficient?
      form.fields['student_agreement'] = None
      return

    program = program_logic.logic.getFromKeyName(scope_path)

    if not (program and program.student_agreement):
      return

    content = entity.scope.student_agreement.content
    form.fields['student_agreement'].widget.text = content


view = View()

apply = view.apply
create = view.create
delete = view.delete
edit = view.edit
list = view.list
manage = view.manage
public = view.public
export = view.export

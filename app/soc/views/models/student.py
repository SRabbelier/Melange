#!/usr/bin/env python2.5
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
    '"Madhusudan.C.S." <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


import time

from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import program as program_logic
from soc.logic.models import student as student_logic
from soc.logic.models import user as user_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import responses
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
    rights['edit'] = [('checkIsMyActiveRole', student_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod', 
         ['student_signup', 'scope_path', program_logic.logic]),
        ('checkIsNotParticipatingInProgramInScope', [program_logic.logic,
        student_logic.logic, org_admin_logic.logic, mentor_logic.logic]),
        ]
    rights['manage'] = [('checkIsMyActiveRole', student_logic.logic)]

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

    new_params['create_template'] = 'soc/student/edit.html'
    new_params['edit_template'] = 'soc/student/edit.html'

    new_params['public_field_keys'] = ["name", "link_id", "scope_path"]
    new_params['public_field_names'] = ["Student Name", "Student ID", "Program ID"]

    # add apply pattern
    patterns = [(r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        '%(module_package)s.%(module_name)s.apply',
        'Become a %(name)s'),]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['agreed_to_tos', 'school']

    current_year = time.gmtime().tm_year
    # the current year is not the minimum because a program could span
    # more than one year
    allowed_years = range(current_year-1, current_year+20)

    view_logic = params['logic'] if params else new_params['logic']

    new_params['create_extra_dynaproperties'] = {
        'expected_graduation': forms.TypedChoiceField(
            choices=[(x,x) for x in allowed_years],
            coerce=lambda val: int(val)
            ),
        'clean': cleaning.validate_student(view_logic.getScopeLogic().logic),
        'school_home_page': forms.fields.URLField(required=True),
        'clean_school_home_page': cleaning.clean_url('school_home_page'),
        }

    new_params['create_dynafields'] = [
        {'name': 'scope_path',
         'base': forms.fields.CharField,
         'widget': forms.HiddenInput,
         'required': True,
         },
        {'name': 'student_agreement',
         'base': forms.fields.CharField,
         'required': False,
         'widget': widgets.AgreementField,
         'group': ugettext("5. Terms of Service"),
         },
        {'name': 'agreed_to_student_agreement',
         'base': forms.fields.BooleanField,
         'initial': False,
         'required':True,
         'label': ugettext('I agree to the Student Agreement'),
         'group': ugettext("5. Terms of Service"),
         },
        ]

    # only if subclassed, so params is not empty
    new_params['show_in_roles_overview'] = bool(params)

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    params = self.getParams()

    # create and store the special form for users
    updated_fields = {
        'link_id': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'clean_link_id': cleaning.clean_user_is_current('link_id'),
        }

    user_create_form = dynaform.extendDynaForm(
        dynaform = params['create_form'],
        dynaproperties = updated_fields)

    params['user_create_form'] = user_create_form

    params['admin_field_keys'].extend([
        'school_name', 'school_country', 'school_home_page', 'school_type',
        'major', 'degree', 'grade', 'expected_graduation', 'program_knowledge',
        'can_we_contact_you'])
    params['admin_field_names'].extend([
        'School Name', 'School Country', 'School Homepage', 'School Type',
        'Major', 'Degree', 'Grade', 'Expected Graduation Year',
        'How did you hear about us?', 'Allowed to Contact?'])
    params['admin_field_hidden'].extend([
        'school_name', 'school_country', 'school_home_page', 'school_type',
        'major', 'degree', 'grade', 'expected_graduation', 'program_knowledge',
        'can_we_contact_you'])

  @decorators.merge_params
  @decorators.check_access
  def apply(self, request, access_type,
           page_name=None, params=None, **kwargs):
    """Handles student role creation for the current user.
    """

    user_entity = user_logic.logic.getCurrentUser()

    logic = params['logic']
    fields = logic.getSuggestedInitialProperties(user_entity)
    fields['link_id'] = user_entity.link_id

    params['create_form'] = params['user_create_form']

    kwargs.update(fields)
    # pylint: disable=E1103
    return self.create(request, access_type='allow', page_name=page_name,
        params=params, **kwargs)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['user'].link_id
      fields['status'] = 'active'

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

    # entity = context['entity']
    form = context['form']

    if 'scope_path' in form.initial:
      scope_path = form.initial['scope_path']
    elif 'scope_path' in request.POST:
      scope_path = request.POST['scope_path']
    else:
      form.fields['student_agreement'] = None
      return

    program = self._params['group_logic'].getFromKeyName(scope_path)

    if not (program and program.student_agreement):
      return

    agreement = program.student_agreement

    content = agreement.content
    params = {'url_name': 'document'}

    widget = form.fields['student_agreement'].widget
    widget.text = content
    widget.url = redirects.getPublicRedirect(agreement, params)


view = View()

apply = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
manage = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest

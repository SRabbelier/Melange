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

"""Views for Student Project.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import time

from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import student as student_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import organization as org_view

import soc.logic.models.student_project


class View(base.View):
  """View methods for the Student Project model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    # TODO who should be able to edit this?
    rights['edit'] = ['checkIsDeveloper']
    
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = ['allow']
    rights['list'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.student_project.logic
    new_params['rights'] = rights
    new_params['name'] = "Student Project"
    new_params['url_name'] = "student_project"
    new_params['sidebar_grouping'] = 'Students'

    new_params['scope_view'] = org_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['no_create_with_key_fields'] = True

    new_params['extra_dynaexclude'] = ['program', 'status', 'link_id',
                                       'mentor', 'student']

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'student_id': forms.CharField(label='Student Link ID',
            required=True),
        'mentor_id': forms.CharField(label='Mentor Link ID',
            required=True),
        'clean_student': cleaning.clean_link_id('student'),
        'clean_mentor': cleaning.clean_link_id('mentor'),
        'clean_additional_info': cleaning.clean_url('additional_info'),
        'clean': cleaning.validate_new_student_project('scope_path',
            'mentor_id', 'student_id')
        }

    new_params['edit_extra_dynaproperties'] = {
        'student_id': forms.CharField(label='Student Link ID',
            widget=widgets.ReadOnlyInput),
        'mentor_id': forms.CharField(label='Mentor Link ID',
            widget=widgets.ReadOnlyInput),
        'link_id': forms.CharField(widget=forms.HiddenInput),
        'clean': (lambda x: x.cleaned_data)
        }

    # TODO(ljvderijk) OrgAdmins should be able to assign another Mentor

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['link_id'].initial = entity.link_id
    form.fields['student_id'].initial = entity.student.link_id
    form.fields['mentor_id'].initial = entity.mentor.link_id

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      fields['link_id'] = 't%i' % (int(time.time()*100))
    else:
      fields['link_id'] = entity.link_id

    # fill in the scope via call to super
    super(View, self)._editPost(request, entity, fields)

    if not entity:
      # creating a new project so set the program, student and mentor field
      fields['program'] = fields['scope'].scope

      filter = {'scope': fields['program'],
                'link_id': fields['student_id']}
      fields['student'] = student_logic.logic.getForFields(filter, unique=True)

      filter = {'scope': fields['scope'],
                'link_id': fields['mentor_id'],
                'status': 'active'}
      fields['mentor'] = mentor_logic.logic.getForFields(filter, unique=True)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)

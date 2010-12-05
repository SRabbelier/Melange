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

"""GCI specific views for Student.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>'
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging

from google.appengine.ext import blobstore

from django import forms
from django import http
from django.forms import fields as django_fields
from django.utils.translation import ugettext
from django.utils.datetime_safe import new_datetime

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import student

from soc.modules.gci.logic.models import mentor as gci_mentor_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.logic.models.student  import logic as gci_student_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.models import task as gci_task_model
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.helper import redirects as gci_redirects
from soc.modules.gci.views.models import program as gci_program_view
from soc.modules.gci.views.models import task as gci_task_view

import soc.modules.gci.logic.models.student


class View(student.View):
  """View methods for the GCI Student model.
  """

  DEF_NO_TASKS_MSG = ugettext(
      'There are no tasks affiliated to you.')

  DEF_STUDENT_TASKS_MSG_FMT = ugettext('My tasks for %s.')

  DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'     # '2006-10-25 14:30:59'

  def __init__(self, params=None):
    """Defines the fields and methods required for the student View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>submit_forms)/%(key_fields)s$',
        '%(module_package)s.%(module_name)s.submit_forms',
        'Submit forms'),
        (r'^%(url_name)s/(?P<access_type>list_student_tasks)/%(scope)s$',
        '%(module_package)s.%(module_name)s.list_student_tasks',
        'List Student tasks')
    ]

    rights = gci_access.GCIChecker(params)
    rights['edit'] = [('checkIsMyActiveRole', gci_student_logic)]
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod', ['student_signup', 'scope_path',
            gci_program_logic.logic]),
        ('checkIsNotParticipatingInProgramInScope',
            [gci_program_logic.logic, gci_student_logic,
            gci_org_admin_logic.logic, gci_mentor_logic.logic]),
        'checkCanApply']
    rights['manage'] = [('checkIsMyActiveRole', gci_student_logic)]
    rights['list_student_tasks'] = [
        ('checkCanOpenTaskList', [gci_student_logic, 'gci/student']),
        ('checkIsAfterEvent', ['student_signup_start',
                               'scope_path', gci_program_logic.logic])]
    rights['submit_forms'] = [('checkIsMyActiveRole', gci_student_logic)]

    new_params = {}
    new_params['logic'] = gci_student_logic
    new_params['rights'] = rights

    new_params['group_logic'] = gci_program_logic.logic
    new_params['group_view'] = gci_program_view.view

    new_params['scope_view'] = gci_program_view

    new_params['name'] = "GCI Student"
    new_params['module_name'] = "student"
    new_params['sidebar_grouping'] = 'Students'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/student'

    new_params['extra_dynaexclude'] = [
        'agreed_to_tos', 'school', 'parental_form_mail',
        'consent_form', 'student_id_form',
    ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    base_form = self._params['dynabase']
    gci_student_model = gci_student_logic.getModel()

    def getUploadForms(name, label, help_text):
      dynafields = [
          {'name': name,
           'base': forms.FileField,
           'label': label,
           'required': False,
           'help_text': help_text,
          }
      ]

      dynaproperties = params_helper.getDynaFields(dynafields)

      add_form = dynaform.newDynaForm(dynabase=base_form,
                                      dynaproperties=dynaproperties)

      dynaproperties = {
          'name': django_fields.CharField(
              label='Name', required=False,
              widget=widgets.PlainTextWidget),
          'uploaded': django_fields.CharField(
              label='Uploaded on', required=False,
              widget=widgets.PlainTextWidget),
          'size': django_fields.CharField(
              label='Size', required=False,
              widget=widgets.PlainTextWidget),
      }
      edit_form = dynaform.extendDynaForm(
          add_form, dynaproperties=dynaproperties,
          dynainclude=['name', 'size', 'uploaded', name])

      return add_form, edit_form

    self._params['consent_form_upload_form'] = getUploadForms(
        'consent_form_upload', 'Consent Form',
        gci_student_model.consent_form.help_text)

    self._params['student_id_form_upload_form'] = getUploadForms(
        'student_id_form_upload', 'Student ID Form',
         gci_student_model.student_id_form.help_text)

  def getListStudentTasksData(self, request, params, filter):
    """Returns the list data for Organization Tasks list.

    Args:
      request: HTTPRequest object
      params: params of the task entity for the list
      filter: properties on which the tasks must be listed
    """

    idx = lists.getListIndex(request)

    # default list settings
    visibility = 'public'

    if idx == 0:
      all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)
      all_t = gci_task_model.TaskTypeTag.all().fetch(100)
      args = [all_d, all_t]

      contents = lists.getListData(request, params, filter,
                                   visibility=visibility, args=args)
    else:
      return lists.getErrorResponse(request, "idx not valid")


    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listStudentTasks(self, request, access_type, page_name=None,
                       params=None, **kwargs):
    """Displays a list of all tasks for a given student.

    See base.View.list() for more details.
    """

    # obtain program entity based on request params
    program = gci_program_logic.logic.getFromKeyNameOr404(
        kwargs['scope_path'])

    user_account = user_logic.logic.getForCurrentAccount()

    list_params = gci_task_view.view.getParams().copy()

    list_params['list_description'] = self.DEF_STUDENT_TASKS_MSG_FMT % (
          program.name)

    filter = {
        'program': program,
        'user': user_account,
        'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                   'Closed', 'AwaitingRegistration', 'NeedsWork',
                   'NeedsReview']
        }
    if lists.isDataRequest(request):
        return self.getListStudentTasksData(request, list_params,
                                             filter)

    tasks = gci_task_logic.logic.getForFields(filter=filter, unique=True)

    contents = []
    order = ['modified_on']

    if tasks:
      tasks_list = lists.getListGenerator(request, list_params,
                                          order=order, idx=0)
      contents.append(tasks_list)

    if contents:
      return self._list(request, list_params, contents, page_name)
    else:
      raise out_of_band.Error(self.DEF_NO_TASKS_MSG)

  @decorators.merge_params
  @decorators.check_access
  def submitForms(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """Form upload page for a given student.

    See base.View.public() for more details.
    """

    template = 'modules/gci/student/submit_forms.html'
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    logic = params['logic']

    entity = logic.getFromKeyFieldsOr404(kwargs)

    if request.method == 'POST':
      return self.submitFormsPost(request, params, context, entity)
    else:
      return self.submitFormsGet(request, params, template, context, entity)

  def submitFormsGet(self, request, params, template, context, entity):
    if lists.isJsonRequest(request):
      url = blobstore.create_upload_url(
          gci_redirects.getSubmitFormsRedirect(entity, params))
      return responses.jsonResponse(request, url)

    def setForm(param_name, blob_info):
      add_form, edit_form = params[param_name]

      if blob_info:
        form = edit_form(initial={
            'name': blob_info.filename,
            'size': blob_info.size,
            'uploaded': blob_info.creation.strftime(self.DATETIME_FORMAT),
            })
      else:
        form = add_form()

      context[param_name] = form

    setForm('consent_form_upload_form', entity.consent_form)
    setForm('student_id_form_upload_form', entity.student_id_form)

    return responses.respond(request, template, context)

  def submitFormsPost(self, request, params, context, entity):
    form = request.POST.get('form')

    if not (request.file_uploads and form):
      # no file uploaded
      logging.error("No file_uploads valid form value")
      return http.HttpResponseRedirect(
          gci_redirects.getSubmitFormsRedirect(entity, params))

    # TODO(SRabbelier): handle multiple file uploads
    upload = request.file_uploads[0]

    if form == 'consent':
      entity.consent_form = upload
    elif form=='student_id':
      entity.student_id_form = upload
    else:
      logging.warning("Invalid value for form '%s'" % form)

    entity.put()

    return http.HttpResponseRedirect(
        gci_redirects.getSubmitFormsRedirect(entity, params))

view = View()

apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_student_tasks = decorators.view(view.listStudentTasks)
public = decorators.view(view.public)
export = decorators.view(view.export)
submit_forms = decorators.view(view.submitForms)

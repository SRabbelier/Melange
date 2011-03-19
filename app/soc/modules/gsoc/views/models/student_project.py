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

"""Views for Student Project.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging
import time

from google.appengine.ext import db

from django import forms
from django import http
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import forms as forms_helper
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base

from soc.modules.gsoc.logic.models import student as student_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student_project import logic as \
    project_logic
from soc.modules.gsoc.views.helper import access
from soc.modules.gsoc.views.models import organization as org_view


class View(base.View):
  """View methods for the Student Project model.
  """

  DEF_NO_RECORD_AVAILABLE_MSG = ugettext('No Record Available')
  DEF_VIEW_RECORD_MSG = ugettext('View Record')
  DEF_TAKE_SURVEY_MSG = ugettext('Take Survey')

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = ['allow']
    rights['list'] = ['checkIsDeveloper']
    rights['manage'] = [('checkHasRoleForScope',
                         [org_admin_logic, ['active', 'inactive']]),
        ('checkStudentProjectHasStatus', [['accepted', 'failed', 'completed',
                                           'withdrawn']])]
    rights['manage_overview'] = [
        ('checkHasAny', [
            [('checkHasRoleForScope', [org_admin_logic,
                                       ['active', 'inactive']]),
             ('checkHasRoleForScope', [mentor_logic,
                                       ['active', 'inactive']])
        ]])]
    # TODO: lack of better name here!
    rights['st_edit'] = [
        'checkCanEditStudentProjectAsStudent',
        ('checkStudentProjectHasStatus',
            [['accepted', 'completed']])
        ]
    rights['overview'] = [('checkIsHostForProgram', [program_logic])]

    new_params = {}
    new_params['logic'] = project_logic
    new_params['rights'] = rights
    new_params['name'] = 'Student Project'
    new_params['url_name'] = 'gsoc/student_project'
    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['sidebar_grouping'] = 'Students'

    new_params['scope_view'] = org_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['no_create_with_key_fields'] = True

    new_params['extra_dynaexclude'] = ['program', 'status', 'link_id',
                                       'mentor', 'additional_mentors',
                                       'student', 'passed_evaluations',
                                       'failed_evaluations']

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'public_info': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'student_id': forms.CharField(label='Student Link ID',
            required=True),
        'mentor_id': forms.CharField(label='Mentor Link ID',
            required=True),
        'clean_abstract': cleaning.clean_content_length('abstract'),
        'clean_public_info': cleaning.clean_html_content('public_info'),
        'clean_student': cleaning.clean_link_id('student'),
        'clean_mentor': cleaning.clean_link_id('mentor'),
        'clean_additional_info': cleaning.clean_url('additional_info'),
        'clean_feed_url': cleaning.clean_feed_url('feed_url'),
        'clean': cleaning.validate_student_project('scope_path',
            'mentor_id', 'student_id')
        }

    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput),
        }

    patterns = [
        (r'^%(url_name)s/(?P<access_type>manage_overview)/%(scope)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.manage_overview',
        'Overview of %(name_plural)s to Manage for'),
        (r'^%(url_name)s/(?P<access_type>manage)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.manage',
        'Manage %(name)s'),
        (r'^%(url_name)s/(?P<access_type>st_edit)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.st_edit',
        'Edit my %(name)s'),
        (r'^%(url_name)s/(?P<access_type>overview)/(?P<scope_path>%(ulnp)s)/%(lnp)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.overview',
        'Overview of all %(name_plural)s for'),
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['edit_template'] = 'soc/student_project/edit.html'
    new_params['manage_template'] = 'soc/student_project/manage.html'

    new_params['public_field_prefetch'] = ['mentor', 'student', 'scope']
    new_params['public_field_extra'] = lambda entity: {
        'student': entity.student.name(),
        'mentor': entity.mentor.name(),
        'org': entity.scope.name,
    }
    new_params['public_field_keys'] = ['student', 'title', 'mentor',
                                       'org', 'status']
    new_params['public_field_names'] = ['Student', 'Title', 'Mentor',
                                        'Organization', 'Status']

    new_params['org_home_field_prefetch'] = ['mentor', 'student']
    new_params['org_home_field_extra'] = lambda entity: {
        'student': entity.student.name(),
        'mentor': ', '.join(
            mentor.name() for mentor in
            [entity.mentor] + db.get(entity.additional_mentors))
    }
    new_params['org_home_field_keys'] = ['student', 'title', 'mentor',
                                         'status']
    new_params['org_home_field_names'] = ['Student', 'Title',
                                          'Mentor', 'Status']

    # define the list redirect action to show the notification
    new_params['public_row_extra'] = new_params[
        'org_home_row_extra'] = lambda entity: {
            'link': redirects.getPublicRedirect(entity, new_params)
        }
    new_params['org_home_row_action'] = {
        'type': 'redirect_custom',
        'parameters': dict(new_window=False),
    }

    new_params['admin_field_prefetch'] = ['mentor', 'student', 'scope']
    new_params['admin_field_extra'] = lambda entity: {
        'student': entity.student.name(),
        'mentor': entity.mentor.name(),
        'student_id': entity.student.link_id
    }
    new_params['admin_field_keys'] = ['student', 'title', 'mentor', 'status',
                                      'student_id']
    new_params['admin_field_names'] = ['Student', 'Title', 'Mentor', 'Status',
                                       'Student Link ID']
    new_params['admin_field_hidden'] = ['student_id']

    new_params['admin_conf_extra'] = {
        'multiselect': True,
    }
    new_params['admin_button_global'] = [
        {
          'bounds': [1,'all'],
          'id': 'withdraw',
          'caption': 'Withdraw Project',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
        },
        {
          'bounds': [1,'all'],
          'id': 'accept',
          'caption': 'Accept Project',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
        }]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create the form that students will use to edit their projects
    dynaproperties = {
        'public_info': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'clean_abstract': cleaning.clean_content_length('abstract'),
        'clean_public_info': cleaning.clean_html_content('public_info'),
        'clean_additional_info': cleaning.clean_url('additional_info'),
        'clean_feed_url': cleaning.clean_feed_url('feed_url'),
        }

    student_edit_form = dynaform.newDynaForm(
        dynabase = self._params['dynabase'],
        dynamodel = self._params['logic'].getModel(),
        dynaexclude = self._params['create_dynaexclude'],
        dynaproperties = dynaproperties,
    )

    self._params['student_edit_form'] = student_edit_form

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

    # editing a project so set the program, student and mentor field
    if entity:
      organization = entity.scope
    else:
      organization = fields['scope']

    fields['program'] = organization.scope

    filter = {'scope': fields['program'],
              'link_id': fields['student_id']}
    fields['student'] = student_logic.logic.getForFields(filter, unique=True)

    filter = {'scope': organization,
              'link_id': fields['mentor_id'],
              'status': 'active'}
    fields['mentor'] = mentor_logic.getForFields(filter, unique=True)

  def _public(self, request, entity, context):
    """Adds the names of all additional mentors to the context.

    For params see base.View._public()
    """

    additional_mentors = entity.additional_mentors

    if not additional_mentors:
      context['additional_mentors'] = []
    else:
      mentor_names = []

      for mentor_key in additional_mentors:
        additional_mentor = mentor_logic.getFromKeyName(
            mentor_key.id_or_name())
        mentor_names.append(additional_mentor.name())

      context['additional_mentors'] = ', '.join(mentor_names)

  def getOverviewData(self, request, params, program):
    """Return data for withdraw.
    """

    fields = {
        'program': program,
        }

    idx = lists.getListIndex(request)

    if idx != 0:
      return lists.getErrorResponse(request, "idx not valid")

    contents = lists.getListData(request, params, fields, visibility='admin')

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def overview(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """View that allows Program Admins to see/control all StudentProjects.

    For args see base.View().public()
    """

    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)

    if request.POST:
      return self.overviewPost(request, params, program_entity)
    else: #request.GET
      return self.overviewGet(request, page_name, params, program_entity,
                              **kwargs)

  def overviewPost(self, request, params, program):
    """Handles the POST request for the Program Admins overview page.

    Args:
      request: Django HTTPRequest object
      params: Params for this view
      program: GSoCProgram entity
    """

    project_logic = params['logic']

    post_dict = request.POST

    data = simplejson.loads(post_dict.get('data', '[]'))
    button_id = post_dict.get('button_id', '')

    if button_id not in ['withdraw', 'accept']:
      logging.warning('Invalid button ID found %s' %(button_id))
      return http.HttpResponse()

    project_keys = []

    for selected in data:
      project_keys.append(selected['key'])

    # get all projects and prefetch the program field
    projects = project_logic.getFromKeyName(project_keys)
    project_logic.prefetchField('program', projects)

    # filter out all projects not belonging to the current program
    projects = [p for p in projects if p.program.key() == program.key()]

    for p in projects:
      fields = {}
      if button_id == 'withdraw':
        fields['status'] = 'withdrawn'
      elif button_id == 'accept':
        fields['status'] = 'accepted'

      # update the project with the new status
      project_logic.updateEntityProperties(p, fields)

    # return a 200 response
    return http.HttpResponse()

  def overviewGet(self, request, page_name, params, program_entity, **kwargs):
    """Handles the GET request for the Program Admins overview page.

    Args:
      request: Django HTTPRequest object
      page_name: Name for this page
      params: Params for this view
      program_entity: GSocProgram entity
    """

    page_name = '%s %s' %(page_name, program_entity.name)

    list_params = params.copy()
    list_params['admin_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, list_params)
    }

    list_params['list_description'] = ugettext(
        'An overview of all StudentProjects for %s. Click on an item to view '
        'the project, use the buttons on the list for withdrawing a project.'%
        (program_entity.name))

    if lists.isDataRequest(request):
      return self.getOverviewData(request, list_params, program_entity)

    project_list = lists.getListGenerator(request, list_params, idx=0, visibility='admin')

    # fill contents with the list
    contents = [project_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)

  def _getManageData(self, request, gps_params, ps_params, entity):
    """Returns the JSONResponse for the Manage page.

    Args:
      request: HTTPRequest object
      gps_params: GradingProjectSurvey list params
      ps_params: ProjectSurvey list params
      entity: StudentProject entity
    """

    idx = lists.getListIndex(request)

    if idx == 0:
      params = gps_params
    elif idx == 1:
      params = ps_params
    else:
      return lists.getErrorResponse(request, "idx not valid")

    fields = {'project': entity}
    record_logic = params['logic'].getRecordLogic()
    record_entities = record_logic.getForFields(fields)
    record_dict = dict((i.survey.key(), i) for i in record_entities if i.survey)
    record_getter = lambda entity: record_dict.get(entity.key())
    args = [record_getter]

    fields = {'scope': entity.program,
              'prefix': 'gsoc_program'}
    contents = lists.getListData(request, params, fields, args=args)

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def manage(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows Organization Admins to manage their Student Projects.

    For params see base.View().public()
    """

    import soc.logic.lists

    from soc.modules.gsoc.views.models.grading_project_survey import view as \
        grading_survey_view
    from soc.modules.gsoc.views.models.project_survey import view as \
        project_survey_view

    entity = self._logic.getFromKeyFieldsOr404(kwargs)

    template = params['manage_template']

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = "%s '%s' from %s" % (page_name, entity.title,
                                                entity.student.name())
    context['entity'] = entity

    if project_logic.canChangeMentors(entity):
      # only accepted project can have their mentors managed
      self._enableMentorManagement(entity, params, context)

    # list all surveys for this Project's Program
    gps_params = grading_survey_view.getParams().copy()
    gps_params['list_description'] = \
        'List of all Mentor Evaluations for this Project'
    gps_params['public_row_extra'] = lambda entity, *args: {}
    gps_params['public_row_action'] = {}
    gps_params['public_field_keys'] = [
        "title", "taken_by", "taken_on", "record_url", "take_url"
    ]
    gps_params['public_field_names'] = [
        "Title", "Taken by", "Taken on", "View", "(Re) Take",
    ]
    no_record = self.DEF_NO_RECORD_AVAILABLE_MSG

    # TODO(SRabbelier): use buttons instead
    project_entity = entity
    getExtra = lambda params: lambda entity, re: {
        "taken_by": no_record if not re(entity) else re(entity).user.name,
        "taken_on": no_record if not re(entity) else str(re(entity).modified),
        "record_url": no_record if not re(entity) else lists.urlize(
            redirects.getViewSurveyRecordRedirect(re(entity), params),
            name=self.DEF_VIEW_RECORD_MSG),
        "take_url": lists.urlize(redirects.getTakeProjectSurveyRedirect(
            project_entity, {'survey': entity, 'params': params}),
            name=self.DEF_TAKE_SURVEY_MSG),
    }

    gps_params['public_field_extra'] = getExtra(gps_params)

    # get the ProjectSurvey list
    ps_params = project_survey_view.getParams().copy()
    ps_params['list_description'] = \
        'List of all Student Evaluations for this Project'
    ps_params['public_row_extra'] = lambda entity, *args: {}
    ps_params['public_row_action'] = {}
    ps_params['public_field_keys'] = gps_params['public_field_keys']
    ps_params['public_field_names'] = gps_params['public_field_names']
    ps_params['public_field_ignore'] = ["take_url"]
    ps_params['public_field_extra'] = getExtra(ps_params)

    if lists.isDataRequest(request):
      return self._getManageData(request, gps_params, ps_params, entity)

    gps_list = lists.getListGenerator(request, gps_params, idx=0)
    ps_list = lists.getListGenerator(request, ps_params, idx=1)

    # store both lists in the content
    content = [gps_list, ps_list]

    context['evaluation_list'] = soc.logic.lists.Lists(content)

    if request.POST:
      return self.managePost(request, template, context, params, entity,
                             **kwargs)
    else: #request.GET
      return self.manageGet(request, template, context, params, entity,
                            **kwargs)

  def _enableMentorManagement(self, entity, params, context):
    """Sets the data required to manage mentors for a StudentProject.

    Args:
      entity: StudentProject entity to manage
      params: params dict for the manage view
      context: context for the manage view
    """

    context['can_manage_mentors'] = True

    # get all mentors for this organization
    fields = {'scope': entity.scope,
              'status': 'active'}
    mentors = mentor_logic.getForFields(fields)

    choices = [(mentor.link_id,'%s (%s)' %(mentor.name(), mentor.link_id))
                  for mentor in mentors]

    # create the form that org admins will use to reassign a mentor
    dynafields = [
        {'name': 'mentor_id',
         'base': forms.ChoiceField,
         'label': 'Primary Mentor',
         'required': True,
         'passthrough': ['required', 'choices', 'label'],
         'choices': choices,
        },]

    dynaproperties = params_helper.getDynaFields(dynafields)

    mentor_edit_form = dynaform.newDynaForm(
        dynabase = params['dynabase'],
        dynaproperties = dynaproperties,
    )

    params['mentor_edit_form'] = mentor_edit_form

    additional_mentors = entity.additional_mentors

    # we want to show the names of the additional mentors in the context
    # therefore they need to be resolved to entities first
    additional_mentors_context = []

    for mentor_key in additional_mentors:
      mentor_entity = mentor_logic.getFromKeyName(
          mentor_key.id_or_name())
      additional_mentors_context.append(mentor_entity)

    context['additional_mentors'] = additional_mentors_context

    # all mentors who are not already an additional mentor or
    # the primary mentor are allowed to become an additional mentor
    possible_additional_mentors = [m for m in mentors if 
        (m.key() not in additional_mentors) 
        and (m.key() != entity.mentor.key())]

    # create the information to be shown on the additional mentor form
    additional_mentor_choices = [
        (mentor.link_id,'%s (%s)' %(mentor.name(), mentor.link_id))
        for mentor in possible_additional_mentors]

    dynafields = [
        {'name': 'mentor_id',
         'base': forms.ChoiceField,
         'label': 'Co-Mentor',
         'required': True,
         'passthrough': ['required', 'choices', 'label'],
         'choices': additional_mentor_choices,
        },]

    dynaproperties = params_helper.getDynaFields(dynafields)

    additional_mentor_form = dynaform.newDynaForm(
        dynabase = params['dynabase'],
        dynaproperties = dynaproperties,
    )

    params['additional_mentor_form'] = additional_mentor_form

  def manageGet(self, request, template, context, params, entity, **kwargs):
    """Handles the GET request for the project's manage page.

    Args:
        template: the template used for this view
        entity: the student project entity
        rest: see base.View.public()
    """

    get_dict = request.GET

    if 'remove' in get_dict and entity.status == 'accepted':
      # get the mentor to remove
      fields = {'link_id': get_dict['remove'],
                'scope': entity.scope}
      mentor = mentor_logic.getForFields(fields, unique=True)

      additional_mentors = entity.additional_mentors
      # pylint: disable=E1103
      if additional_mentors and mentor.key() in additional_mentors:
        # remove the mentor from the additional mentors list
        additional_mentors.remove(mentor.key())
        fields = {'additional_mentors': additional_mentors}
        project_logic.updateEntityProperties(entity, fields)

      # redirect to the same page without GET arguments
      redirect = request.path
      return http.HttpResponseRedirect(redirect)

    if project_logic.canChangeMentors(entity):
      # populate forms with the current mentors set
      initial = {'mentor_id': entity.mentor.link_id}
      context['mentor_edit_form'] = params['mentor_edit_form'](initial=initial)
      context['additional_mentor_form'] = params['additional_mentor_form']()

    return responses.respond(request, template, context)

  def managePost(self, request, template, context, params, entity, **kwargs):
    """Handles the POST request for the project's manage page.

    Args:
        template: the template used for this view
        entity: the student project entity
        rest: see base.View.public()
    """

    post_dict = request.POST

    if 'set_mentor' in post_dict and project_logic.canChangeMentors(entity):
      form = params['mentor_edit_form'](post_dict)
      return self._manageSetMentor(request, template, context, params, entity,
                                   form)
    elif 'add_additional_mentor' in post_dict and \
        project_logic.canChangeMentors(entity):
      form = params['additional_mentor_form'](post_dict)
      return self._manageAddAdditionalMentor(request, template, context,
                                             params, entity, form)
    else:
      # unexpected error return the normal page
      logging.warning('Unexpected POST data found')
      return self.manageGet(request, template, context, params, entity)

  def _manageSetMentor(self, request, template, context, params, entity, form):
    """Handles the POST request for changing a Projects's mentor.

    Args:
        template: the template used for this view
        entity: the student project entity
        form: instance of the form used to set the mentor
        rest: see base.View.public()
    """

    if not form.is_valid():
      context['mentor_edit_form'] = form

      # add an a fresh additional mentors form
      context['additional_mentor_form'] = params['additional_mentor_form']()

      return responses.respond(request, template, context)

    _, fields = forms_helper.collectCleanedFields(form)

    # get the mentor from the form
    fields = {'link_id': fields['mentor_id'],
              'scope': entity.scope,
              'status': 'active'}
    mentor = mentor_logic.getForFields(fields, unique=True)

    # update the project with the assigned mentor
    fields = {'mentor': mentor}

    additional_mentors = entity.additional_mentors

    # pylint: disable=E1103
    if additional_mentors and mentor.key() in additional_mentors:
      # remove the mentor that is now becoming the primary mentor
      additional_mentors.remove(mentor.key())
      fields['additional_mentors'] = additional_mentors

    # update the project with the new mentor and possible 
    # new set of additional mentors
    project_logic.updateEntityProperties(entity, fields)

    # redirect to the same page
    redirect = request.path
    return http.HttpResponseRedirect(redirect)

  def _manageAddAdditionalMentor(self, request, template, 
                                 context, params, entity, form):
    """Handles the POST request for changing a Projects's additional mentors.

    Args:
        template: the template used for this view
        entity: the student project entity
        form: instance of the form used to add an additional mentor
        rest: see base.View.public()
    """

    if not form.is_valid():
      context['additional_mentor_form'] = form

      # add a fresh edit mentor form
      initial = {'mentor_id': entity.mentor.link_id}
      context['mentor_edit_form'] = params['mentor_edit_form'](initial=initial)

      return responses.respond(request, template, context)

    _, fields = forms_helper.collectCleanedFields(form)

    # get the mentor from the form
    fields = {'link_id': fields['mentor_id'],
              'scope': entity.scope,
              'status': 'active'}
    mentor = mentor_logic.getForFields(fields, unique=True)

    # add this mentor to the additional mentors
    if not entity.additional_mentors:
      additional_mentors = [mentor.key()]
    else:
      additional_mentors = entity.additional_mentors
      additional_mentors.append(mentor.key())

    fields = {'additional_mentors': additional_mentors}
    project_logic.updateEntityProperties(entity, fields)

    # redirect to the same page
    redirect = request.path
    return http.HttpResponseRedirect(redirect)

  def getManageOverviewData(self, request, mo_params, org_entity):
    """Returns the manageOverview data.
    """

    args = []
    fields = {}

    idx = lists.getListIndex(request)

    if idx == 0:
      from soc.modules.gsoc.logic.models.survey import grading_logic as \
          grading_survey_logic
      from soc.modules.gsoc.logic.models.survey import project_logic as \
          project_survey_logic
      from soc.modules.gsoc.logic.models.survey_record import grading_logic
      from soc.modules.gsoc.logic.models.survey_record import project_logic

      program_entity = org_entity.scope

      fields = {'scope_path': program_entity.key().id_or_name()}

      # count the number of have been active ProjectSurveys
      project_surveys = project_survey_logic.getForFields(fields)
      project_survey_count = len(project_surveys)

      for project_survey in project_surveys:
        if not project_survey_logic.hasRecord(project_survey):
          project_survey_count = project_survey_count - 1

      # count the number of have been active GradingProjectSurveys
      grading_surveys = grading_survey_logic.getForFields(fields)
      grading_survey_count = len(grading_surveys)

      for grading_survey in grading_surveys:
        if not grading_survey_logic.hasRecord(grading_survey):
          grading_survey_count = grading_survey_count - 1

      fields = {'scope': org_entity}
      params = mo_params
      args = [project_surveys, project_survey_count,
              grading_surveys, grading_survey_count]
    else:
      return lists.getErrorResponse(request, 'idx not valid')

    contents = lists.getListData(request, params, fields, args=args)

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def manageOverview(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows Organization Admins to see an overview of 
       their Organization's Student Projects.

    For params see base.View().public()
    """

    from soc.modules.gsoc.logic.models.survey import grading_logic as \
        grading_survey_logic
    from soc.modules.gsoc.logic.models.survey import project_logic as \
        project_survey_logic
    from soc.modules.gsoc.logic.models.survey_record import grading_logic
    from soc.modules.gsoc.logic.models.survey_record import project_logic

    # make sure the organization exists
    org_entity = org_logic.getFromKeyNameOr404(kwargs['scope_path'])
    page_name = '%s %s' % (page_name, org_entity.name)

    mo_params = params.copy()

    #list all active projects
    mo_params['list_description'] = ugettext(
        'List of all %s for %s, if you are an Org Admin you can click '
        'a project for more actions. Such as reassigning mentors or viewing '
        'results of the evaluations.' %(params['name_plural'], org_entity.name)
        )
    mo_params['public_field_names'] = params['public_field_names'] + [
        'Mentor evaluation', 'Student Evaluation']
    mo_params['public_field_keys'] = params['public_field_keys'] + [
        'mentor_evaluation', 'student_evaluation']

    fields = {'scope': org_entity,
              'status': ['active', 'inactive']}
    org_admin = org_admin_logic.getForFields(fields, unique=True)

    # Org Admins get a link to manage the project, others go to public page
    if org_admin:
      mo_params['public_row_extra'] = lambda entity, *args: {
          'link': redirects.getManageRedirect(entity, mo_params)
      }
    else:
      mo_params['public_row_extra'] = lambda entity, *args: {
          'link': redirects.getPublicRedirect(entity, mo_params)
      }

    mo_params['public_field_prefetch'] = ['student', 'mentor', 'scope']
    mo_params['public_field_extra'] = lambda entity, ps, psc, gs, gsc: {
        'org': entity.scope.name,
        'student': '%s (%s)' % (entity.student.name(), entity.student.email),
        'mentor': entity.mentor.name(),
        'mentor_evaluation': '%d/%d' % (
                grading_logic.getQueryForFields({'project': entity}).count(),
                gsc),
        'student_evaluation': '%d/%d' % (
                project_logic.getQueryForFields({'project': entity}).count(),
                psc),
    }

    if lists.isDataRequest(request):
      return self.getManageOverviewData(request, mo_params, org_entity)

    mo_list = lists.getListGenerator(request, mo_params, idx=0)
    contents = [mo_list]

    # call the _list method from base to display the list
    return self._list(request, mo_params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def stEdit(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows students to edit information about their project.

    For params see base.View().public()
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name
    # cancel should go to the public view
    params['cancel_redirect'] = redirects.getPublicRedirect(entity, params)

    if request.POST:
      return self.stEditPost(request, context, params, entity, **kwargs)
    else: #request.GET
      return self.stEditGet(request, context, params, entity, **kwargs)

  def stEditGet(self, request, context, params, entity, **kwargs):
    """Handles the GET request for the student's edit page.

    Args:
        entity: the student project entity
        rest: see base.View.public()
    """

    # populate form with the existing entity
    form = params['student_edit_form'](instance=entity)

    return self._constructResponse(request, entity, context, form, params)

  def stEditPost(self, request, context, params, entity, **kwargs):
    """Handles the POST request for the student's edit page.

    Args:
        entity: the student project entity
        rest: see base.View.public()
    """

    form = params['student_edit_form'](request.POST)

    if not form.is_valid():
      return self._constructResponse(request, entity, context, form, params)

    _, fields = forms_helper.collectCleanedFields(form)

    project_logic.updateEntityProperties(entity, fields)

    return self.stEditGet(request, context, params, entity, **kwargs)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
manage_overview = decorators.view(view.manageOverview)
overview = decorators.view(view.overview)
public = decorators.view(view.public)
st_edit = decorators.view(view.stEdit)
export = decorators.view(view.export)
pick = decorators.view(view.pick)

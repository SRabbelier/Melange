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


import logging
import time

from django import forms
from django import http
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
from soc.views.models import organization as org_view

from soc.modules.gsoc.logic.models import student as student_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student_project import logic as project_logic
from soc.modules.gsoc.views.helper import access


class View(base.View):
  """View methods for the Student Project model.
  """

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
    rights['manage'] = [('checkHasActiveRoleForScope',
                         org_admin_logic),
        ('checkStudentProjectHasStatus', [['accepted', 'failed', 'completed',
                                           'withdrawn']])]
    rights['manage_overview'] = [('checkHasActiveRoleForScope',
                         org_admin_logic)]
    # TODO: lack of better name here!
    rights['st_edit'] = [
        'checkCanEditStudentProjectAsStudent',
        ('checkStudentProjectHasStatus',
            [['accepted', 'completed']])
        ]
    rights['withdraw'] = ['checkIsHostForProgram']
    rights['withdraw_project'] = ['checkIsHostForStudentProject',
        ('checkStudentProjectHasStatus',
            [['accepted', 'completed']])
        ]
    rights['accept_project'] = ['checkIsHostForStudentProject',
        ('checkStudentProjectHasStatus',
            [['withdrawn']])
        ]

    new_params = {}
    new_params['logic'] = project_logic
    new_params['rights'] = rights
    new_params['name'] = "Student Project"
    new_params['url_name'] = "gsoc/student_project"
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
        'clean_feed_url': cleaning.clean_feed_url,
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
        (r'^%(url_name)s/(?P<access_type>withdraw)/(?P<scope_path>%(ulnp)s)/%(lnp)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.withdraw',
        'Withdraw %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>withdraw_project)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.withdraw_project',
        'Withdraw a %(name)s'),
        (r'^%(url_name)s/(?P<access_type>accept_project)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.accept_project',
        'Accept a %(name)s'),
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['edit_template'] = 'soc/student_project/edit.html'
    new_params['manage_template'] = 'soc/student_project/manage.html'
    new_params['manage_overview_heading'] = \
        'soc/student_project/list/heading_manage.html'
    new_params['manage_overview_row'] = \
        'soc/student_project/list/row_manage.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create the form that students will use to edit their projects
    dynaproperties = {
        'public_info': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'clean_abstract': cleaning.clean_content_length('abstract'),
        'clean_public_info': cleaning.clean_html_content('public_info'),
        'clean_additional_info': cleaning.clean_url('additional_info'),
        'clean_feed_url': cleaning.clean_feed_url,
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

  @decorators.merge_params
  @decorators.check_access
  def withdraw(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """View that allows Program Admins to accept or withdraw Student Projects.

    For params see base.View().public()
    """

    program = program_logic.getFromKeyFieldsOr404(kwargs)

    fields = {
        'program': program,
        'status': ['accepted', 'completed'],
        }

    ap_params = params.copy() # accepted projects

    ap_params['list_action'] = (redirects.getWithdrawProjectRedirect,
                                ap_params)
    ap_params['list_description'] = ugettext(
        "An overview of accepted and completed Projects. "
        "Click on a project to withdraw it.")

    ap_list = lists.getListContent(
        request, ap_params, fields, idx=0)

    fields['status'] = ['withdrawn']

    wp_params = params.copy() # withdrawn projects

    wp_params['list_action'] = (redirects.getAcceptProjectRedirect, wp_params)
    wp_params['list_description'] = ugettext(
        "An overview of withdrawn Projects. "
        "Click on a project to undo the withdrawal.")

    wp_list = lists.getListContent(
        request, wp_params, fields, idx=1)

    # fill contents with all the needed lists
    contents = [ap_list, wp_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def withdrawProject(self, request, access_type,
                      page_name=None, params=None, **kwargs):
    """View that allows Program Admins to withdraw Student Projects.

    For params see base.View().public()

    """

    logic = params['logic']
    entity = logic.getFromKeyFieldsOr404(kwargs)

    fields = {
        'status': 'withdrawn',
        }

    logic.updateEntityProperties(entity, fields)

    url = redirects.getWithdrawRedirect(entity.program, params)

    return http.HttpResponseRedirect(url)

  @decorators.merge_params
  @decorators.check_access
  def acceptProject(self, request, access_type,
                    page_name=None, params=None, **kwargs):
    """View that allows Program Admins to accept Student Projects.

    For params see base.View().public()

    """

    logic = params['logic']
    entity = logic.getFromKeyFieldsOr404(kwargs)

    fields = {
        'status': 'accepted',
        }

    logic.updateEntityProperties(entity, fields)

    url = redirects.getWithdrawRedirect(entity.program, params)

    return http.HttpResponseRedirect(url)

  @decorators.merge_params
  @decorators.check_access
  def manage(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows Organization Admins to manage their Student Projects.

    For params see base.View().public()
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    template = params['manage_template']

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = "%s '%s' from %s" % (page_name, entity.title,
                                                entity.student.name())
    context['entity'] = entity


    if entity.status == 'accepted':
      # only accepted project can have their mentors managed
      self._enableMentorManagement(entity, params, context)

    context['evaluation_list'] = self._getEvaluationLists(request, params,
                                                          entity)

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

  def _getEvaluationLists(self, request, params, entity):
    """Returns List Object containing the list to be shown on the Student 
    Project's manage page.

    This list contains all Surveys that have at least one record and will also 
    contain information about the presence (or absence) of a accompanying 
    record for the given Student Project.

    Args:
      request: Django HTTP Request Object
      params: the params dict for this View
      entity: a StudentProject entity for which the Surveys(Records) should be
              retrieved

    Returns:
      A List Object as specified by this method.
    """

    from soc.modules.gsoc.views.helper import list_info
    from soc.views.models.grading_project_survey import view as \
        grading_survey_view
    from soc.views.models.project_survey import view as project_survey_view

    fields = {'scope_path': entity.program.key().id_or_name()}

    # get the GradingProjectSurvey list
    gps_params = grading_survey_view.getParams().copy()
    gps_params['list_key_order'] = None
    gps_params['list_heading'] = gps_params['manage_student_project_heading']
    gps_params['list_row'] = gps_params['manage_student_project_row']

    # list all surveys for this Project's Program
    fields['scope_path'] = entity.program.key().id_or_name()
    gps_params['list_description'] = \
        'List of all Mentor Evaluations for this Project'
    gps_params['list_action'] = None

    gps_list = lists.getListContent(
        request, gps_params, fields, idx=0)
    list_info.setProjectSurveyInfoForProject(gps_list, entity, gps_params)

    # get the ProjectSurvey list
    ps_params = project_survey_view.getParams().copy()
    ps_params['list_key_order'] = None
    ps_params['list_heading'] = ps_params['manage_student_project_heading']
    ps_params['list_row'] = ps_params['manage_student_project_row']

    ps_params['list_description'] = \
        'List of all Student Evaluations for this Project'
    ps_params['list_action'] = None

    # list all surveys for this Project's Program
    fields['scope_path'] = entity.program.key().id_or_name()
    ps_list = lists.getListContent(
        request, ps_params, fields, idx=1)
    list_info.setProjectSurveyInfoForProject(ps_list, entity, ps_params)

    # store both lists in the content
    content = [gps_list, ps_list]

    for list in content:
      # remove all the surveys that have no records attached
      list['data'] = [i for i in list['data'] if
                      list['logic'].hasRecord(i)]

    # return the List Object with the filtered list content
    return soc.logic.lists.Lists(content)

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
      # pylint: disable-msg=E1103
      if additional_mentors and mentor.key() in additional_mentors:
        # remove the mentor from the additional mentors list
        additional_mentors.remove(mentor.key())
        fields = {'additional_mentors': additional_mentors}
        project_logic.updateEntityProperties(entity, fields)

      # redirect to the same page without GET arguments
      redirect = request.path
      return http.HttpResponseRedirect(redirect)

    if entity.status == 'accepted':
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

    if 'set_mentor' in post_dict and entity.status == 'accepted':
      form = params['mentor_edit_form'](post_dict)
      return self._manageSetMentor(request, template, context, params, entity,
                                   form)
    elif 'add_additional_mentor' in post_dict and entity.status == 'accepted':
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

    # pylint: disable-msg=E1103
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

  @decorators.merge_params
  @decorators.check_access
  def manageOverview(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows Organization Admins to see an overview of 
       their Organization's Student Projects.

    For params see base.View().public()
    """

    from soc.modules.gsoc.views.helper import list_info

    # make sure the organization exists
    org_entity = org_logic.getFromKeyNameOr404(kwargs['scope_path'])
    fields = {'scope': org_entity}

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = '%s %s' % (page_name, org_entity.name)

    prefetch = ['student', 'mentor']

    list_params = params.copy()
    list_params['list_heading'] = params['manage_overview_heading']
    list_params['list_row'] = params['manage_overview_row']

    #list all active projects
    fields['status'] = 'accepted'
    active_params = list_params.copy()
    active_params['list_description'] = \
        'List of all active %(name_plural)s' % list_params
    active_params['list_action'] = (redirects.getManageRedirect, list_params)

    active_list = lists.getListContent(request, active_params, fields, idx=0,
                                       prefetch=prefetch)
    # set the needed info
    active_list = list_info.setStudentProjectSurveyInfo(active_list,
                                                        org_entity.scope)

    # list all failed projects
    fields['status'] = 'failed'
    failed_params = list_params.copy()
    failed_params['list_description'] = ('List of all %(name_plural)s who ' 
                                         'failed the program.') % list_params
    failed_params['list_action'] = (redirects.getManageRedirect, list_params)

    failed_list = lists.getListContent(request, failed_params, fields, idx=1,
                                       need_content=True, prefetch=prefetch)
    # set the needed info
    failed_list = list_info.setStudentProjectSurveyInfo(failed_list,
                                                        org_entity.scope)

    # list all completed projects
    fields['status'] = 'completed'
    completed_params = list_params.copy()
    completed_params['list_description'] = (
        'List of %(name_plural)s that have successfully completed the '
        'program.' % list_params)
    completed_params['list_action'] = (redirects.getManageRedirect, list_params)

    completed_list = lists.getListContent(request, completed_params, fields,
                                          idx=2, need_content=True,
                                          prefetch=prefetch)
    # set the needed info
    completed_list = list_info.setStudentProjectSurveyInfo(completed_list,
                                                           org_entity.scope)

    # list all withdrawn projects
    fields['status'] = 'withdrawn'
    withdrawn_params = list_params.copy()
    withdrawn_params['list_description'] = (
        'List of %(name_plural)s that have withdrawn from the program.' %(
            list_params))
    withdrawn_params['list_action'] = (redirects.getManageRedirect, list_params)

    withdrawn_list = lists.getListContent(request, withdrawn_params, fields,
                                          idx=3, need_content=True,
                                          prefetch=prefetch)
    # set the needed info
    withdrawn_list = list_info.setStudentProjectSurveyInfo(withdrawn_list,
                                                           org_entity.scope)

    # always show the list with active projects
    content = [active_list]

    if failed_list != None:
      # do not show empty failed list
      content.append(failed_list)

    if completed_list != None:
      # do not show empty completed list
      content.append(completed_list)

    if withdrawn_list != None:
      # do not show empty withdrawn list
      content.append(withdrawn_list)

    # call the _list method from base to display the list
    return self._list(request, list_params, content,
                      context['page_name'], context)

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

accept_project = decorators.view(view.acceptProject)
admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
manage_overview = decorators.view(view.manageOverview)
public = decorators.view(view.public)
st_edit = decorators.view(view.stEdit)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
withdraw = decorators.view(view.withdraw)
withdraw_project = decorators.view(view.withdrawProject)

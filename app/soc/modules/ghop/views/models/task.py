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

"""Views for Tasks.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime
import time

from google.appengine.ext import db

from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import host as host_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base

from soc.modules.ghop.logic import cleaning as ghop_cleaning
from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import program as ghop_program_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.models import task as ghop_task_model
from soc.modules.ghop.views.helper import access
from soc.modules.ghop.views.helper import redirects as ghop_redirects
from soc.modules.ghop.views.models import organization as ghop_org_view
from soc.modules.ghop.tasks import task_update

import soc.modules.ghop.logic.models.task


class View(base.View):
  """View methods for the Tasks.
  """

  DEF_AWAITING_REG_MSG = ugettext(
      'The task is open but you cannot claim this task since you '
      'have not completed the student signup after finishing your '
      'first task.')

  DEF_CAN_EDIT_TASK_MSG = ugettext(
      'The task can be edited by clicking on the edit link '
      'next to the title above.')

  DEF_MAX_TASK_LIMIT_MSG_FMT = ugettext(
      'The task is open but you cannot claim this task since you '
      'have already claimed %d task(s).')

  DEF_SIGNIN_TO_COMMENT_MSG = ugettext(
      '<a href=%s>Sign in</a> to perform any action or comment on '
      'this task.')

  DEF_STUDENT_SIGNUP_MSG = ugettext(
      'You have successfully completed this task. Sign up as a student '
      'before you proceed further.')

  DEF_TASK_CLAIMED_BY_YOU_MSG = ugettext(
      'You have claimed this task!')

  DEF_TASK_CLAIMED_BY_STUDENT_MSG = ugettext(
      'This task has been claimed by a student!')

  DEF_TASK_CLAIMED_MSG = ugettext(
      'The task is already claimed and the work is in progress.')

  DEF_TASK_CLAIM_REQUESTED_MSG = ugettext(
      'A student has requested to claim this task. Accept or '
      'reject the request.')

  DEF_TASK_CLOSED_MSG = ugettext('This task is closed.')

  DEF_TASK_CMPLTD_BY_YOU_MSG = ugettext(
      'You have successfully completed this task!')

  DEF_TASK_NO_MORE_SUBMIT_MSG = ugettext(
      'You have submitted the work to this task, but deadline has passed '
      'You cannot submit any more work until your mentor extends the '
      'deadline.')

  DEF_TASK_MENTOR_REOPENED_MSG = ugettext(
      'The task has been reopened.')

  DEF_TASK_NEEDS_REVIEW_MSG = ugettext(
      'Student has submitted his work for this task! It needs review.')

  DEF_TASK_OPEN_MSG = ugettext(
      'This task is open. If you are a GHOP student, you can claim it!')

  DEF_TASK_REOPENED_MSG = ugettext(
      'This task has been reopened. If you are a GHOP student, '
      'you can claim it!')

  DEF_TASK_REQ_CLAIMED_BY_YOU_MSG = ugettext(
      'You have requested to claim this task!')

  DEF_TASK_UNPUBLISHED_MSG = ugettext(
      'The task is not yet published. It can be edited by clicking on '
      'the edit button below.')

  DEF_WS_MSG_FMT = ugettext(
      '(To see the work submitted <a href=#ws%d>click here</a>.)')

  def __init__(self, params=None):
    """Defines the fields and methods required for the task View class
    to provide the user with the necessary views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GHOPChecker(params)
    # TODO: create and suggest_task don't need access checks which use state
    # also feels like roles are being checked twice?
    rights['create'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin'], ['active'],
            []])]
    rights['edit'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open']])]
    rights['delete'] = [
        ('checkRoleAndStatusForTask', 
            [['ghop/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open']])]
    rights['show'] = ['checkStatusForTask']
    rights['list_org_tasks'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False])]
    rights['suggest_task'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['ghop/org_admin', 'ghop/mentor'], ['active'],
            ['Unapproved']])]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.task.logic
    new_params['rights'] = rights

    new_params['name'] = "Task"
    new_params['module_name'] = "task"
    new_params['sidebar_grouping'] = 'Tasks'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/task'

    new_params['scope_view'] = ghop_org_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['list_heading'] = 'modules/ghop/task/list/heading.html'
    new_params['list_row'] = 'modules/ghop/task/list/row.html'

    new_params['extra_dynaexclude'] = ['task_type', 'mentors', 'user',
                                       'student', 'program', 'status',
                                       'deadline', 'created_by',
                                       'created_on', 'modified_by',
                                       'modified_on', 'history',
                                       'link_id', 'difficulty']

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>suggest_task)/%(scope)s$',
        '%(module_package)s.%(module_name)s.suggest_task',
        'Mentors suggest %(name)s'),
        (r'^%(url_name)s/(?P<access_type>suggest_task)/%(key_fields)s$',
        '%(module_package)s.%(module_name)s.suggest_task',
        'Mentors edit a %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_org_tasks)/%(scope)s$',
        '%(module_package)s.%(module_name)s.list_org_tasks',
        'List Organization %(name)s'),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'arbit_tags',
         'base': forms.fields.CharField,
         'label': 'Arbitrary Tags',
         'required': False,
         'group': ugettext('Tags'),
         'help_text': ugettext(
             'Enter arbitrary Tags for this task separated by comma.\n'
             '<b>Note:</b> Tag names are case sensitive. If the tag is same '
             'as the program mandated tag, it will be considered as a '
             'mandatory tag.')
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'description': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'time_to_complete': forms.IntegerField(min_value=1,
                                               required=True),
        'clean_description': cleaning.clean_html_content('description'),
        'clean_arbit_tags': cleaning.str2set('arbit_tags'),
        }

    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }

    new_params['public_template'] = 'modules/ghop/task/public.html'

    def render(entities):
      two = [i.name for i in entities[:2]]
      result = ", ".join(two)
      size = len(entities) - 2
      return result if size > 0 else "%s + %d" % (result, size)

    new_params['public_field_extra'] = lambda entity: {
        "difficulty": entity.difficulty[0].tag,
        "task_type": ", ".join(entity.task_type),
        "mentors": render(db.get(entity.mentors)),
    }
    new_params['public_field_keys'] = [
        "title", "difficulty", "task_type",
        "time_to_complete", "status", "mentors",
    ]
    new_params['public_field_names'] = [
        "Title", "Difficulty", "Type",
        "Time To Complete", "Status", "Mentors",
    ]

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    # holds the base form for the task creation and editing
    self._params['base_create_form'] = self._params['create_form']
    self._params['base_edit_form'] = self._params['edit_form']

    # extend create and edit form for org admins
    dynafields = [
        {'name': 'mentors_list',
         'required': True,
         'base': forms.fields.CharField,
         'label': 'Assign mentors',
         'help_text': 'Assign mentors to this task by '
             'giving their link_ids separated by comma.',
         },
        {'name': 'published',
         'required': False,
         'initial': False,
         'base': forms.fields.BooleanField,
         'label': 'Publish the task',
         'help_text': ugettext('By ticking this box, the task will be'
                               'made public and can be claimed by students.'),
         }
        ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    dynaproperties['clean_mentors_list'] = ghop_cleaning.cleanMentorsList(
        'mentors_list')

    create_form = dynaform.extendDynaForm(
        dynaform=self._params['create_form'],
        dynaproperties=dynaproperties)

    self._params['create_form'] = create_form

    edit_form = dynaform.extendDynaForm(
        dynaform=self._params['edit_form'],
        dynaproperties=dynaproperties)

    self._params['edit_form'] = edit_form

    # create the comment form
    dynafields = [
        {'name': 'comment',
         'base': forms.CharField,
         'widget': widgets.FullTinyMCE(attrs={'rows': 10, 'cols': 40}),
         'label': 'Comment',
         'required': False,
         'example_text': 'Comment is optional.<br/>'
             'Choose an appropriate Action below and Save your '
             'changes.<br /><br />Caution, you will not be able '
             'to edit your comment!',
         },
         ]

    dynaproperties = params_helper.getDynaFields(dynafields)
    dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')
    dynaproperties['clean'] = ghop_cleaning.cleanTaskComment(
        'comment', 'action', 'work_submission')

    comment_form = dynaform.newDynaForm(dynamodel=None,
        dynabase=helper.forms.BaseForm, dynainclude=None,
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['comment_form'] = comment_form

  def _getTagsForProgram(self, form_name, params, **kwargs):
    """Extends form dynamically from difficulty levels in program entity.

    Args:
     form_name: the Form entry in params to extend
     params: the params for the view
    """

    # obtain program_entity using scope_path which holds
    # the org_entity key_name
    org_entity = ghop_org_logic.logic.getFromKeyName(kwargs['scope_path'])
    program_entity = ghop_program_logic.logic.getFromKeyName(
        org_entity.scope_path)

    # get a list difficulty levels stored for the program entity
    tds = ghop_task_model.TaskDifficultyTag.get_by_scope(
        program_entity)

    difficulties = []
    for td in tds:
      difficulties.append((td.tag, td.tag))

    # get a list of task type tags stored for the program entity
    tts = ghop_task_model.TaskTypeTag.get_by_scope(program_entity)

    type_tags = []
    for tt in tts:
      type_tags.append((tt.tag, tt.tag))

    # create the difficultly level field containing the choices
    # defined in the program entity
    dynafields = [
        {'name': 'difficulty',
         'base': forms.ChoiceField,
         'label': 'Difficulty level',
         'required': True,
         'passthrough': ['initial', 'required', 'choices',
                         'label', 'help_text'],
         'choices': difficulties,
         'group': ugettext('Tags'),
         'help_text': ugettext('Difficulty Level of this task.'),
         },
         {'name': 'type_tags',
         'base': forms.MultipleChoiceField,
         'label': 'Task Types',
         'required': True,
         'passthrough': ['initial', 'required', 'choices',
                         'label', 'help_text'],
         'choices': type_tags,
         'group': ugettext('Tags'),
         'help_text': ugettext('Task Type tags mandated by the program. You '
                               'must select one or more of them.'),
         },
       ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    extended_form = dynaform.extendDynaForm(
        dynaform=params[form_name],
        dynaproperties=dynaproperties)

    return extended_form

  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Replaces the create Form with the dynamic one.

    For args see base.View.create().
    """

    params = dicts.merge(params, self._params)

    # extend create_form to include difficulty levels
    params['create_form'] = self._getTagsForProgram(
        'create_form', params, **kwargs)

    return super(View, self).create(request, 'allow', page_name=page_name,
                                    params=params, **kwargs)

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit().
    """

    logic = params['logic']

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    try:
      entity = logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      msg = self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']
          }
      error.message_fmt = error.message_fmt + msg
      return helper.responses.errorResponse(
          error, request, context=context)

    # extend edit_form to include difficulty levels
    params['edit_form'] = self._getTagsForProgram(
        'edit_form', params, **kwargs)

    if entity.status == 'Unapproved':
      dynafields = [
          {'name': 'approved',
           'required': False,
           'initial': False,
           'base': forms.fields.BooleanField,
           'label': 'Approve the task',
           'help_text': 'By ticking this box, the task will be'
               'will be approved for publishing.',
          }
          ]

      dynaproperties = params_helper.getDynaFields(dynafields)

      edit_form = dynaform.extendDynaForm(
          dynaform=params['edit_form'],
          dynaproperties=dynaproperties)

      params['edit_form'] = edit_form

    if request.method == 'POST':
      return self.editPost(request, entity, context, params=params)
    else:
      return self.editGet(request, entity, context, params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    if entity.task_type:
      form.fields['type_tags'].initial = entity.tags_string(
          entity.task_type, ret_list=True)
    if entity.arbit_tag:
      form.fields['arbit_tags'].initial = entity.tags_string(
          entity.arbit_tag)

    if entity.difficulty:
      form.fields['difficulty'].initial = entity.tags_string(
          entity.difficulty)

    if entity.mentors and 'mentors_list' in form.fields:
      mentor_entities = db.get(entity.mentors)
      mentors_list = []
      for mentor in mentor_entities:
        mentors_list.append(mentor.link_id)
      form.fields['mentors_list'].initial = ', '.join(mentors_list)

    form.fields['link_id'].initial = entity.link_id

    # checks if the task is already approved or not and sets
    # the form approved field
    if 'approved' in form.fields:
      if entity.status == 'Unapproved':
        form.fields['approved'].initial = False
      else:
        form.fields['approved'].initial = True

    # checks if the task is already published or not and sets
    # the form published field
    if 'published' in form.fields:
      if entity.status == 'Unapproved' or entity.status == 'Unpublished':
        form.fields['published'].initial = False
      else:
        form.fields['published'].initial = True

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    # set the scope field
    super(View, self)._editPost(request, entity, fields)

    # TODO: this method can be made more clear, it seems a bit of a mess

    if not entity:
      program_entity = fields['scope'].scope
      fields['program'] = program_entity
    else:
      program_entity = entity.program

    user_account = user_logic.logic.getForCurrentAccount()

    filter = {
        'user': user_account,
        'status': 'active'
        }
    if not entity:
      filter['scope'] = fields['scope']
    else:
      filter['scope'] = entity.scope

    role_entity = ghop_org_admin_logic.logic.getForFields(
        filter, unique=True)

    if role_entity:
      # this user can publish/approve the task
      if fields.get('published'):
        fields['status'] = 'Open'
      elif fields.get('approved'):
        fields['status'] = 'Unpublished'

      fields['mentors'] = fields.get('mentors_list', [])
    else:
      role_entity = ghop_mentor_logic.logic.getForFields(
          filter, unique=True)
      if not entity:
        # creating a new task
        fields['status'] = 'Unapproved'

    # explicitly change the last_modified_on since the content has been edited
    fields['modified_on'] = datetime.datetime.now()

    if not entity:
      fields['link_id'] = 't%i' % (int(time.time()*100))
      fields['modified_by'] = role_entity
      fields['created_by'] = role_entity
      fields['created_on'] = datetime.datetime.now()
    else:
      fields['link_id'] = entity.link_id
      fields['modified_by'] = role_entity
      if 'status' not in fields:
        fields['status'] = entity.status

    fields['difficulty'] = {
        'tags': fields['difficulty'],
        'scope': program_entity
        }

    fields['task_type'] = {
        'tags': fields['type_tags'],
        'scope': program_entity
        }

    fields['arbit_tag'] = {
        'tags': fields['arbit_tags'],
        'scope': program_entity
        }

    return

  @decorators.merge_params
  @decorators.check_access
  def suggestTask(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """View used to allow mentors to create or edit a task.

    Tasks created by mentors must be approved by org admins
    before they are published.
    """

    params = dicts.merge(params, self._params)

    if 'link_id' in kwargs:
      # extend create_form to include difficulty levels
      params['mentor_form'] = self._getTagsForProgram(
          'base_edit_form', params, **kwargs)
      try:
        entity = self._logic.getFromKeyFieldsOr404(kwargs)
      except out_of_band.Error, error:
        return helper.responses.errorResponse(
            error, request, template=params['error_public'])
    else:
      # extend create_form to include difficulty levels
      params['mentor_form'] = self._getTagsForProgram(
          'base_create_form', params, **kwargs)
      entity = None

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.suggestTaskPost(request, context,
                                  params, entity)
    else:
      return self.suggestTaskGet(request, context,
                                 params, entity, kwargs)

  def suggestTaskPost(self, request, context, params, entity):
    """Handles the POST request for the suggest task view.
    """

    form = params['mentor_form'](request.POST)

    if not form.is_valid():
      return self._constructResponse(request, None, context, form, params)

    _, fields = helper.forms.collectCleanedFields(form)
    # TODO: this non-standard view shouldn't call _editPost but its own method
    self._editPost(request, entity, fields)

    logic = params['logic']
    if entity:
      entity = logic.updateEntityProperties(entity, fields)
    else:
      # TODO: Redirect to standard edit page which already has the ability to
      # hide certain fields.
      # get the mentor entity of the current user that is suggesting the task
      user_entity = user_logic.logic.getForCurrentAccount()

      filter = {'user': user_entity,
                'scope': fields['scope'],
                'status': 'active'}

      mentor_entity = ghop_mentor_logic.logic.getForFields(filter, unique=True)

      # pylint: disable-msg=E1103
      fields['mentors'] = [mentor_entity.key()]

      entity = logic.updateOrCreateFromFields(fields)

    redirect = ghop_redirects.getSuggestTaskRedirect(
        entity, params)

    return http.HttpResponseRedirect(redirect)

  def suggestTaskGet(self, request, context, params, entity, seed):
    """Handles the GET request for the suggest task view.
    """

    if entity:
      # populate form with the existing entity
      form = params['mentor_form'](instance=entity)

      self._editGet(request, entity, form)
    elif seed:
      form = params['mentor_form'](initial=seed)
    else:
      form = params['mentor_form']()

    return self._constructResponse(request, entity, context, form, params)

  @decorators.merge_params
  @decorators.check_access
  def listOrgTasks(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """See base.View.list()
    """
    if request.method == 'POST':
      return self.listOrgTasksPost(request, params, **kwargs)
    else: # request.method == 'GET'
      return self.listOrgTasksGet(request, page_name, params, **kwargs)

  def listOrgTasksPost(self, request, params, **kwargs):
    """Handles the POST request for the list tasks view.
    """

    # get the org entity for which we are listing these tasks
    org_entity = ghop_org_logic.logic.getFromKeyNameOr404(kwargs['scope_path'])

    # save the state to which the selected tasks must be changed
    # to based on the actions.
    if request.POST.get('Approve'):
      changed_status = 'Unpublished'
    elif request.POST.get('Publish'):
      changed_status = 'Open'

    # update the status of task entities that should be approved or published
    task_entities = []

    # get all the task keys to update, will return empty list if doesn't exist
    task_keys = request.POST.getlist('task_id')

    for key_name in task_keys:

      task_entity = ghop_task_logic.logic.getFromKeyName(key_name)

      # Of course only the tasks from this organization and those with a valid
      # state can be updated.
      if task_entity and task_entity.scope.key() == org_entity.key() and \
          task_entity.status in ['Unapproved', 'Unpublished']:
        task_entity.status = changed_status

        task_entities.append(task_entity)

    # bulk put the task_entities
    # TODO: replace with Task API call?
    db.put(task_entities)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def listOrgTasksGet(self, request, page_name, params, **kwargs):
    """Handles the GET request for the list tasks view.
    """

    from soc.modules.ghop.views.helper import list_info as list_info_helper

    org_entity =  ghop_org_logic.logic.getFromKeyNameOr404(
        kwargs['scope_path'])

    contents = []
    context = {}

    user_account = user_logic.logic.getForCurrentAccount()

    fields = {
        'user': user_account,
        'scope': org_entity,
        'status': 'active'
        }

    up_params = params.copy()
    # give the capability to approve tasks for the org_admins
    if ghop_org_admin_logic.logic.getForFields(fields, unique=True):
      up_params['list_template'] = 'modules/ghop/task/approve/approve.html'
      up_params['list_heading'] = 'modules/ghop/task/approve/heading.html'
      up_params['list_row'] = 'modules/ghop/task/approve/row.html'

    up_params['public_row_entity'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, up_params)
    }
# TODO(LIST)
    up_params['list_description'] = ugettext(
       'List of Unapproved tasks.')

    filter = {
        'scope': org_entity,
        'status': 'Unapproved',
        }

    up_list = lists.getListContent(request, up_params, filter, idx=0,
                                   need_content=True)

    if up_list:
      up_mentors_list = {}
      for task_entity in up_list['data']:
        up_mentors_list[task_entity.key()] = db.get(task_entity.mentors)

      up_list['info'] = (list_info_helper.getTasksInfo(up_mentors_list), None)

      contents.append(up_list)
      context['up_list'] = True

    aup_params = params.copy()
    aup_params['list_heading'] = 'modules/ghop/task/approve/heading.html'
    aup_params['list_row'] = 'modules/ghop/task/approve/row.html'

    aup_params['public_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, aup_params)
    }

    aup_params['list_description'] = ugettext(
       'List of Approved but Unpublished tasks.')

    filter = {
        'scope': org_entity,
        'status': 'Unpublished',
        }

    aup_list = lists.getListContent(request, aup_params, filter, idx=1,
                                    need_content=True)

    if aup_list:
      aup_mentors_list = {}
      for task_entity in aup_list['data']:
        aup_mentors_list[task_entity.key()] = db.get(task_entity.mentors)

      aup_list['info'] = (list_info_helper.getTasksInfo(aup_mentors_list), None)

      contents.append(aup_list)

    ap_params = up_params.copy()
    ap_params['list_template'] = 'soc/models/list.html'
    ap_params['list_heading'] = 'modules/ghop/task/list/heading.html'
    ap_params['list_row'] = 'modules/ghop/task/list/row.html'

    ap_params['public_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, ap_params)
    }

    ap_params['list_description'] = ugettext(
       'List of Published tasks.')

    filter = {
        'scope': org_entity,
        'status': ['Open', 'Reopened', 'ClaimRequested', 'Claimed',
            'ActionNeeded', 'Closed', 'AwaitingRegistration',
            'NeedsWork', 'NeedsReview'],
        }

    ap_list = lists.getListContent(request, ap_params, filter, idx=2,
                                   need_content=True)

    if ap_list:
      ap_mentors_list = {}
      for task_entity in ap_list['data']:
        ap_mentors_list[task_entity.key()] = db.get(task_entity.mentors)

      ap_list['info'] = (list_info_helper.getTasksInfo(ap_mentors_list), None)

      contents.append(ap_list)

    # call the _list method from base to display the list
    return self._list(request, up_params, contents, page_name, context)

  @decorators.merge_params
  @decorators.check_access
  def public(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """See base.View.public().
    """

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name
    entity = None
    logic = params['logic']

    try:
      entity, comment_entities, ws_entities = (
          logic.getFromKeyFieldsWithCWSOr404(kwargs))
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'], context=context)

    # because we are not sure if the Task API has called this for us we do it
    entity, comment_entity = ghop_task_logic.logic.updateTaskStatus(entity)
    if comment_entity:
      comment_entities.append(comment_entity)

    context['entity'] = entity
    context['entity_key_name'] = entity.key().id_or_name()
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']

    user_account = user_logic.logic.getForCurrentAccount()

    # get some entity specific context
    self.updatePublicContext(context, entity, comment_entities,
                             ws_entities, user_account, params)

    validation = self._constructActionsList(context, entity,
                                            user_account, params)

    context = dicts.merge(params['context'], context)

    if request.method == 'POST':
      return self.publicPost(request, context, params, entity,
                             user_account, validation, **kwargs)
    else: # request.method == 'GET'
      return self.publicGet(request, context, params, entity,
                            user_account, **kwargs)

  def publicPost(self, request, context, params, entity,
                 user_account=None, validation=None, **kwargs):
    """Handles the POST request for the entity's public page.

    Args:
        entity: the task entity
        rest: see base.View.public()
    """

    from soc.modules.ghop.logic.models import student as ghop_student_logic

    form = params['comment_form'](request.POST)

    if not form.is_valid():
      template = params['public_template']
      context['comment_form'] = form
      return self._constructResponse(request, entity, context,
                                     form, params, template=template)

    _, fields = helper.forms.collectCleanedFields(form)

    changes = []

    action = fields['action']

    properties = None
    ws_properties = None

    # TODO: this can be separated into several methods that handle the changes
    if validation == 'claim_request' and action == 'request':
      properties = {
          'status': 'ClaimRequested',
          'user': user_account,
          }

      st_filter = {
          'user': user_account,
          'scope': entity.program,
          'status': 'active'
          }
      student_entity = ghop_student_logic.logic.getForFields(
          st_filter, unique=True)

      if student_entity:
        properties['student'] = student_entity

      changes.extend([ugettext('User-Student'),
                      ugettext('Action-Claim Requested'),
                      ugettext('Status-%s' % (properties['status']))
                      ])
    elif (validation == 'claim_withdraw' or
        validation == 'needs_review') and action == 'withdraw':
      properties = {
          'user': None,
          'student': None,
          'status': 'Reopened',
          'deadline': None,
          }

      changes.extend([ugettext('User-Student'),
                      ugettext('Action-Withdrawn'),
                      ugettext('Status-%s' % (properties['status']))
                      ])
    elif validation == 'needs_review' and action == 'needs_review':
      properties = {
          'status': 'NeedsReview',
          }

      changes.extend([
          ugettext('User-Student'),
          ugettext('Action-Submitted work and Requested for review'),
          ugettext('Status-%s' % (properties['status']))])

      ws_properties = {
          'parent': entity,
          'program': entity.program,
          'org': entity.scope,
          'user': user_account,
          'information': fields['comment'],
          'url_to_work': fields['work_submission'],
          'submitted_on': datetime.datetime.now(),
          }
    elif validation == 'accept_claim':
      if action == 'accept':
        deadline = datetime.datetime.now() + datetime.timedelta(
            hours=entity.time_to_complete)

        properties = {
            'status': 'Claimed',
            'deadline': deadline,
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Claim Accepted'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

        task_update.spawnUpdateTask(entity)
      if action == 'reject':
        properties = {
            'user': None,
            'student': None,
            'status': 'Reopened',
            'deadline': None,
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Claim Rejected'),
                        ugettext('Status-%s' % (properties['status']))
                        ])
    elif validation == 'close':
      if action == 'needs_work':
        properties = {
            'status': 'NeedsWork',
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Requested more work'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

        if fields['extended_deadline'] > 0:
          deadline = entity.deadline + datetime.timedelta(
              hours=fields['extended_deadline'])

          properties['deadline'] = deadline

          changes.append(ugettext('DeadlineExtendedBy-%d hrs to %s' % (
              fields['extended_deadline'], deadline.strftime(
                  '%d %B %Y, %H :%M'))))

          task_update.spawnUpdateTask(entity)
        else:
          changes.append(ugettext('NoDeadlineExtensionGiven'))
      elif action == 'reopened':
        properties = {
          'user': None,
          'student': None,
          'status': 'Reopened',
          'deadline': None,
          }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Reopened'),
                        ugettext('Status-%s' % (properties['status']))
                        ])
      elif action == 'closed':
        properties = {
            'deadline': None,
            }

        if entity.student:
          properties['status'] = 'Closed'
        else:
          properties['status'] = 'AwaitingRegistration'

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Closed the task'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

    comment_properties = {
        'parent': entity,
        'scope_path': entity.key().name(),
        'created_by': user_account,
        'changes': changes,
        }

    if ws_properties:
      comment_properties['content'] = self.DEF_WS_MSG_FMT
    else:
      comment_properties['content'] = fields['comment']

    ghop_task_logic.logic.updateEntityPropertiesWithCWS(
        entity, properties, comment_properties, ws_properties)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def publicGet(self, request, context, params, entity,
                user_account, **kwargs):
    """Handles the GET request for the entity's public page.

    Args:
        entity: the task entity
        rest see base.View.public()
    """

    context['comment_form'] = params['comment_form']()

    template = params['public_template']

    return responses.respond(request, template, context=context)

  def updatePublicContext(self, context, entity, comment_entities,
                          ws_entities, user_account, params):
    """Updates the context for the public page with information.

    Args:
      context: the context that should be updated
      entity: a task used to set context
      user_account: user entity of the logged in user
      params: dict with params for the view using this context
    """

    mentor_entities = db.get(entity.mentors)
    mentors_str = ""
    for mentor in mentor_entities:
      mentors_str += mentor.name() + ", "

    if mentors_str:
      context['mentors_str'] = mentors_str[:-2]
    else:
      context['mentors_str'] = "Not Assigned"

    context['difficulty_str'] = entity.tags_string(entity.difficulty)

    context['task_type_str'] = entity.tags_string(entity.task_type)

    if entity.deadline:
      # TODO: it should be able to abuse Django functionality for this
      ttc = entity.deadline - datetime.datetime.now()
      (ttc_min, ttc_hour) = ((ttc.seconds / 60), (ttc.seconds / 3600))
      if ttc_min >= 60:
        ttc_min = ttc_min % 60
      if ttc_hour > 1:
        if ttc_min == 0:
          ttc_str = '%d hours' % (ttc_hour)
        else:
          ttc_str = '%d:%02d hours' % (ttc_hour, ttc_min)
        if ttc.days == 1:
          ttc_str = '%d day, %s' % (ttc.days, ttc_str)
        elif ttc.days > 1:
          ttc_str = '%d days, %s' % (ttc.days, ttc_str)
      else:
        ttc_str = '%d mins' % (ttc_min)
      context['time_to_complete'] = ttc_str
    else:
      if entity.status == 'NeedsReview':
        context['time_to_complete'] = 'No Time Left'
      else:
        context['time_to_complete'] = '%d hours' % (entity.time_to_complete)

    context['comments'] = comment_entities

    context['work_submissions'] = ws_entities

  def _constructActionsList(self, context, entity,
                            user_account, params):
    """Constructs a list of actions for the task page and extends
    the comment form with this list.

    This method also returns the validation used by POST method to
    validate the user input data.

    Args:
      context: the context that should be updated
      entity: a task used to set context
      user_account: user entity of the logged in user
      params: dict with params for the view using this context
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    # The following header messages are shown for non-logged in
    # general public, logged in public and the student.
    if entity.status is 'Closed':
      context['header_msg'] = self.DEF_TASK_CLOSED_MSG
      validation = 'closed'

    if entity.status == 'Open':
      context['header_msg'] = self.DEF_TASK_OPEN_MSG
    elif entity.status == 'Reopened':
      context['header_msg'] = self.DEF_TASK_REOPENED_MSG

    if user_account:
      actions = [('noaction', 'Comment without action')]

      # if the user is logged give him the permission to claim
      # the task only if he none of program host, org admin or mentor
      filter = {
          'user': user_account,
          }

      host_entity = host_logic.logic.getForFields(filter, unique=True)

      filter['scope_path'] = entity.scope_path
      org_admin_entity = ghop_org_admin_logic.logic.getForFields(
          filter, unique=True)
      mentor_entity = ghop_mentor_logic.logic.getForFields(
          filter, unique=True)

      if host_entity or org_admin_entity or mentor_entity:
        validation, mentor_actions = self._constructMentorActions(
            context, entity)
        actions += mentor_actions
        if entity.status in ['Unapproved', 'Unpublished', 'Open']:
          if host_entity or org_admin_entity:
            context['edit_link'] = redirects.getEditRedirect(entity, params)
          elif mentor_entity:
            context['suggest_link'] = ghop_redirects.getSuggestTaskRedirect(
                entity, params)
      else:
        validation, student_actions = self._constructStudentActions(
            context, entity, user_account)
        actions += student_actions

      # create the difficultly level field containing the choices
      # defined in the program entity
      dynafields = [
          {'name': 'action',
           'base': forms.ChoiceField,
           'label': 'Action',
           'required': False,
           'passthrough': ['initial', 'required', 'choices'],
           'choices': actions,
           },
         ]

      if validation == 'needs_review':
        dynafields.append(
            {'name': 'work_submission',
             'base': forms.URLField,
             'label': 'Submit Work',
             'required': False,
             'help_text': 'Provide a link to your work in this box. '
                 'Please use the comment box if you need to explain '
                 'of your work.',
             })

      if validation == 'close':
        dynafields.append(
            {'name': 'extended_deadline',
             'base': forms.IntegerField,
             'min_value': 1,
             'label': 'Extend deadline by',
             'required': False,
             'passthrough': ['min_value', 'required', 'help_text'],
             'help_text': 'Optional: Specify the number of hours by '
                 'which you want to extend the deadline for the task '
                 'for this student. ',
             })

      dynaproperties = params_helper.getDynaFields(dynafields)
      if validation == 'needs_review':
        dynaproperties['clean_work_submission'] = cleaning.clean_url(
            'work_submission')

      extended_comment_form = dynaform.extendDynaForm(
          dynaform=params['comment_form'],
          dynaproperties=dynaproperties)

      params['comment_form'] = extended_comment_form
    else:
      # list of statuses a task can be in after it is requested to be
      # claimed before closing or re-opening
      claim_status = ['ClaimRequested', 'Claimed', 'ActionNeeded',
                      'NeedsWork', 'NeedsReview']
      if entity.status in claim_status:
        context['header_msg'] = self.DEF_TASK_CLAIMED_MSG
      elif entity.status in ['AwaitingRegistration', 'Closed']:
        context['header_msg'] = self.DEF_TASK_CLOSED_MSG

      context['signin_comment_msg'] = self.DEF_SIGNIN_TO_COMMENT_MSG % (
          context['sign_in'])

    return validation

  def _constructMentorActions(self, context, entity):
    """Constructs the list of actions for mentors, org admins and
    hosts.
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    actions = []

    if entity.status in ['Unapproved', 'Unpublished']:
      context['header_msg'] = self.DEF_TASK_UNPUBLISHED_MSG
      context['comment_disabled'] = True
    elif entity.status == 'Open':
      context['header_msg'] = self.DEF_CAN_EDIT_TASK_MSG
    elif entity.status == 'Reopened':
      context['header_msg'] = self.DEF_TASK_MENTOR_REOPENED_MSG
    elif entity.status == 'ClaimRequested':
      actions.extend([('accept', 'Accept claim request'),
                      ('reject', 'Reject claim request')])
      context['header_msg'] = self.DEF_TASK_CLAIM_REQUESTED_MSG
      validation = 'accept_claim'
    elif entity.status == 'Claimed':
      context['header_msg'] = self.DEF_TASK_CLAIMED_BY_STUDENT_MSG
    elif entity.status == 'NeedsReview':
      context['header_msg'] = self.DEF_TASK_NEEDS_REVIEW_MSG
      actions.extend([('needs_work', 'Needs More Work'),
                      ('reopened', 'Reopen the task'),
                      ('closed', 'Close the task')])
      validation = 'close'
    elif entity.status in ['AwaitingRegistration', 'Closed']:
      context['header_msg'] = self.DEF_TASK_CLOSED_MSG

    return validation, actions

  def _constructStudentActions(self, context, entity, user_account):
    """Constructs the list of actions for students.
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    actions = []

    if entity.status in ['Open', 'Reopened']:
      task_filter = {
          'user': user_account,
          'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                     'NeedsWork', 'NeedsReview']
          }
      task_entities = ghop_task_logic.logic.getForFields(task_filter)

      if len(task_entities) >= entity.program.nr_simultaneous_tasks:
        context['header_msg'] = self.DEF_MAX_TASK_LIMIT_MSG_FMT % (
            entity.program.nr_simultaneous_tasks)
        validation = 'claim_ineligible'
        return validation, actions

      task_filter['status'] = 'AwaitingRegistration'
      task_entities = ghop_task_logic.logic.getForFields(task_filter)

      if task_entities:
        context['header_msg'] = self.DEF_AWAITING_REG_MSG
        validation = 'claim_ineligible'
      else:
        actions.append(('request', 'Request to claim the task'))
        validation = 'claim_request'

    # TODO: lot of double information here that can be simplified
    if entity.user and user_account.key() == entity.user.key():
      if entity.status  == 'ClaimRequested':
        context['header_msg'] = self.DEF_TASK_REQ_CLAIMED_BY_YOU_MSG
        actions.append(('withdraw', 'Withdraw from the task'))
        validation = 'claim_withdraw'
      elif entity.status in ['Claimed', 'NeedsWork',
                             'NeedsReview', 'ActionNeeded']:
        context['header_msg'] = self.DEF_TASK_CLAIMED_BY_YOU_MSG
        actions.extend([
            ('withdraw', 'Withdraw from the task'),
            ('needs_review', 'Submit work and Request for review')])
        validation = 'needs_review'
      elif entity.status == 'NeedsReview':
        context['header_msg'] = self.DEF_TASK_NO_MORE_SUBMIT_MSG
        actions.append(('withdraw', 'Withdraw from the task'))
        if datetime.datetime.now < entity.deadline:
          actions.append(
              ('needs_review', 'Submit work and Request for review'))
        validation = 'needs_review'
      elif entity.status == 'AwaitingRegistration':
        context['header_msg'] = self.DEF_STUDENT_SIGNUP_MSG
      elif entity.status == 'Closed':
        context['header_msg'] = self.DEF_TASK_CMPLTD_BY_YOU_MSG
    else:
      if entity.status in ['ClaimRequested', 'Claimed',
                           'ActionNeeded', 'NeedsWork',
                           'NeedsReview']:
        context['header_msg'] = self.DEF_TASK_CLAIMED_MSG
      if entity.status in ['AwaitingRegistration', 'Closed']:
        context['header_msg'] = self.DEF_TASK_CLOSED_MSG

    return validation, actions

  @decorators.merge_params
  @decorators.check_access
  def delete(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Shows the delete page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    params = params.copy()

    params['delete_redirect'] = '/%s/list_org_tasks/%s' % (
        params['url_name'], kwargs['scope_path'])

    return super(View, self).delete(request, access_type, page_name=page_name,
        params=params, **kwargs)


view = View()

create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_org_tasks = decorators.view(view.listOrgTasks)
suggest_task = decorators.view(view.suggestTask)
public = decorators.view(view.public)

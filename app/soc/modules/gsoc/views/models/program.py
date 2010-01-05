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

"""Views for GSoCProgram.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import allocations
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import system
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.models import program
from soc.views.sitemap import sidebar

from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import org_app as org_app_logic
from soc.logic.models import organization as org_logic
from soc.logic.models.host import logic as host_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.student_proposal import logic \
    as student_proposal_logic
from soc.modules.gsoc.views.helper import access
from soc.views.helper import redirects


class View(program.View):
  """View methods for the Program model.
  """

  DEF_ACCEPTED_ORGS_MSG_FMT = ugettext("These organizations have"
      " been accepted into %(name)s, but they have not yet completed"
      " their organization profile. You can still learn more about"
      " each organization by visiting the links below.")

  DEF_CREATED_ORGS_MSG_FMT = ugettext("These organizations have been"
      " accepted into %(name)s and have completed their organization"
      " profiles. You can learn more about each organization by"
      " visiting the links below.")

  DEF_ACCEPTED_PROJECTS_MSG_FMT = ugettext("These projects have been"
      " accepted into %(name)s. You can learn more about each project"
      " by visiting the links below.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
        host_logic])]
    rights['edit'] = [('checkIsHostForProgram', [program_logic])]
    rights['delete'] = ['checkIsDeveloper']
    rights['assign_slots'] = [('checkIsHostForProgram', [program_logic])]
    rights['slots'] = [('checkIsHostForProgram', [program_logic])]
    rights['show_duplicates'] = [('checkIsHostForProgram',
        [program_logic])]
    rights['assigned_proposals'] = [('checkIsHostForProgram',
        [program_logic])]
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', program_logic])]
    rights['list_projects'] = [('checkIsAfterEvent',
        ['accepted_students_announced_deadline',
         '__all__', program_logic])]

    new_params = {}
    new_params['logic'] = program_logic
    new_params['rights'] = rights

    new_params['name'] = "GSoC Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'gsoc_program'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/program'

    new_params['extra_dynaexclude'] = ['slots_allocation']

    new_params['create_dynafields'] = [
        {'name': 'org_tags',
         'base': forms.fields.Field,
         'widget': forms.widgets.Textarea,
         'label': 'Predefined organization tags',
         'required': False,
         'group': ugettext('Manage organization tags'),
         'help_text': ugettext('Enter predefined tags to be used by '
              'organization admins to tag their organizations. Each line '
              'should contain only one tag')},
        ]

    new_params['create_extra_dynaproperties'] = {
        'clean_org_tags': cleaning.str2set('org_tags', '\n')
        }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)

  @decorators.merge_params
  def _editPost(self, request, entity, fields, params=None):
    """See base._editPost().
    """

    super(View, self)._editPost(request, entity, fields)

    logic = params['logic']
    logic.updatePredefinedOrgTags(entity, fields.get('org_tags'))

  @decorators.merge_params
  def getExtraMenus(self, id, user, params=None):
    """Returns the extra menu's for this view.

    A menu item is generated for each program that is currently
    running. The public page for each program is added as menu item,
    as well as all public documents for that program.

    Args:
      params: a dict with params for this View.
    """

    # TODO: the largest part of this method can be moved to the core Program

    logic = params['logic']
    rights = params['rights']

    # only get all valid programs
    fields = {'status': ['invisible', 'visible', 'inactive']}
    entities = logic.getForFields(fields)

    menus = []

    rights.setCurrentUser(id, user)

    for entity in entities:
      items = []

      # some entries should be shown for all programs which are not hidden
      if entity.status in ['visible', 'inactive']:
        items += self._getStandardProgramEntries(entity, id, user, params)
        items += self._getSurveyEntries(entity, params, id, user)
      try:
        # check if the current user is a host for this program
        rights.doCachedCheck('checkIsHostForProgram',
                             {'scope_path': entity.scope_path,
                              'link_id': entity.link_id}, [logic])

        if entity.status == 'invisible':
          # still add the standard entries so hosts can see how it looks like
          items += self._getStandardProgramEntries(entity, id, user, params)
          items += self._getSurveyEntries(entity, params, id, user)

        items += self._getHostEntries(entity, params, 'gsoc')

        items += [(redirects.getReviewOverviewRedirect(
            entity, {'url_name': 'org_app'}),
            "Review Organization Applications", 'any_access')]

        # add link to Assign Slots
        items += [(redirects.getAssignSlotsRedirect(entity, params),
            'Assign Slots', 'any_access')]
        # add link to Show Duplicate project assignments
        items += [(redirects.getShowDuplicatesRedirect(entity, params),
            'Show Duplicate Project Assignments', 'any_access')]
        # add link to create a new Program Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'survey'),
            "Create a New Survey", 'any_access')]
        # add link to list all Program Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'survey'),
            "List Surveys", 'any_access')]
        # add link to create a new Project Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'gsoc/project_survey'),
            "Create a New Project Survey", 'any_access')]
        # add link to list all Project Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'gsoc/project_survey'),
            "List Project Surveys", 'any_access')]
        # add link to create a new Grading Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'gsoc/grading_project_survey'),
            "Create a New Grading Survey", 'any_access')]
        # add link to list all Grading Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'gsoc/grading_project_survey'),
            "List Grading Surveys", 'any_access')]
        # add link to withdraw Student Projects
        items += [(redirects.getWithdrawRedirect(
            entity, {'url_name': 'student_project'}),
            "Withdraw Student Projects", 'any_access')]

      except out_of_band.Error:
        pass

      items = sidebar.getSidebarMenu(id, user, items, params=params)
      if not items:
        continue

      menu = {}
      menu['heading'] = entity.short_name
      menu['items'] = items
      menu['group'] = 'Programs'
      menu['collapse'] = 'collapse' if entity.status == 'inactive' else ''
      menus.append(menu)

    return menus

  def _getTimeDependentEntries(self, program_entity, params, id, user):
    """Returns a list with time dependent menu items.
    """

    items = []

    #TODO(ljvderijk) Add more timeline dependent entries
    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(timeline_entity, 'org_signup'):
      # add the organization signup link
      items += [
          (redirects.getApplyRedirect(program_entity, {'url_name': 'org_app'}),
          "Apply to become an Organization", 'any_access')]

    if user and timeline_helper.isAfterEvent(timeline_entity,
        'org_signup_start'):
      filter = {
          'applicant': user,
          'scope': program_entity,
          }

      if org_app_logic.logic.getForFields(filter, unique=True):
        # add the 'List my Organization Applications' link
        items += [
            (redirects.getListSelfRedirect(program_entity,
                                           {'url_name' : 'org_app'}),
             "List My Organization Applications", 'any_access')]

    # get the student entity for this user and program
    filter = {
        'user': user,
        'scope': program_entity,
        'status': 'active'
        }
    student_entity = student_logic.getForFields(filter, unique=True)

    if student_entity:
      items += self._getStudentEntries(program_entity, student_entity,
                                       params, id, user, 'gsoc')

    # get mentor and org_admin entity for this user and program
    filter = {
        'user': user,
        'program': program_entity,
        'status': ['active', 'inactive']
        }
    mentor_entity = mentor_logic.getForFields(filter, unique=True)
    org_admin_entity = org_admin_logic.getForFields(filter, unique=True)

    if mentor_entity or org_admin_entity:
      items += self._getOrganizationEntries(program_entity, org_admin_entity,
                                            mentor_entity, params, id, user)

    if user and not (student_entity or mentor_entity or org_admin_entity):
      if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
        # this user does not have a role yet for this program
        items += [
            ('/gsoc/student/apply/%s' % (program_entity.key().id_or_name()),
            "Register as a Student", 'any_access')]

    deadline = 'accepted_organization_announced_deadline'

    if timeline_helper.isAfterEvent(timeline_entity, deadline):
      url = redirects.getAcceptedOrgsRedirect(program_entity, params)
      # add a link to list all the organizations
      items += [(url, "List participating Organizations", 'any_access')]

      if not student_entity and \
          timeline_helper.isBeforeEvent(timeline_entity, 'program_end'):
        # add apply to become a mentor link
        items += [
            ('/gsoc/org/apply_mentor/%s' % (program_entity.key().id_or_name()),
           "Apply to become a Mentor", 'any_access')]

    deadline = 'accepted_students_announced_deadline'

    if timeline_helper.isAfterEvent(timeline_entity, deadline):
      items += [(redirects.getListProjectsRedirect(program_entity,
          {'url_name':'gsoc/program'}),
          "List all Student Projects", 'any_access')]

    return items

  def _getSurveyEntries(self, entity, params, id, user):
    """Returns a list of entries specific for surveys which should be visible
    for users.
    """

    from soc.views.models import survey as survey_view
    from soc.modules.gsoc.views.models import project_survey \
        as project_survey_view
    from soc.modules.gsoc.views.models import grading_project_survey \
        as grading_survey_view

    items = []

    items += survey_view.view.getMenusForScope(entity, params, id, user)
    items += project_survey_view.view.getMenusForScope(entity, params, id, 
                                                       user)
    items += grading_survey_view.view.getMenusForScope(entity, params, id,
                                                       user)

    return items

  def _getStudentEntries(self, program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
      items += [('/gsoc/student_proposal/list_orgs/%s' % (
          student_entity.key().id_or_name()),
          "Submit your Student Proposal", 'any_access')]

    if timeline_helper.isAfterEvent(timeline_entity, 'student_signup_start'):
      items += [(redirects.getListSelfRedirect(student_entity,
          {'url_name': prefix + '/student_proposal'}),
          "List my Student Proposals", 'any_access')]

    if timeline_helper.isAfterEvent(timeline_entity,
                                   'accepted_students_announced_deadline'):
      # add a link to show all projects
      items += [(redirects.getListProjectsRedirect(program_entity,
          {'url_name': prefix + '/student'}),
          "List my Student Projects", 'any_access')]

    items += super(View, self)._getStudentEntries(program_entity,
        student_entity, params, id, user, prefix)

    return items

  @decorators.merge_params
  @decorators.check_access
  def acceptedOrgs(self, request, access_type,
                   page_name=None, params=None, filter=None, **kwargs):
    """See base.View.list.
    """

    from soc.modules.gsoc.views.models.organization import view as org_view

    contents = []
    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    aa_list = self._getOrgsWithAcceptedApps(request, program_entity, params)
    if aa_list:
      contents.append(aa_list)

    fmt = {'name': program_entity.name}
    description = self.DEF_CREATED_ORGS_MSG_FMT % fmt

    use_cache = not aa_list # only cache if there are no aa's left

    ap_list = self._getOrgsWithProfilesList(program_entity, org_view,
        description, use_cache)
    contents.append(ap_list)

    params = params.copy()
    params['list_msg'] = program_entity.accepted_orgs_msg

    return self._list(request, params, contents, page_name)

  def _getOrgsWithAcceptedApps(self, request, program_entity, params):
    """
    """

    fmt = {'name': program_entity.name}
    description = self.DEF_ACCEPTED_ORGS_MSG_FMT % fmt

    filter = {
        'status': 'accepted',
        'scope': program_entity,
        }

    from soc.views.models import org_app as org_app_view
    aa_params = org_app_view.view.getParams().copy() # accepted applications

    # define the list redirect action to show the notification
    del aa_params['list_key_order']
    aa_params['list_action'] = (redirects.getHomeRedirect, aa_params)
    aa_params['list_description'] = description

    aa_list = lists.getListContent(request, aa_params, filter, idx=0,
                                   need_content=True)

    return aa_list


  @decorators.merge_params
  @decorators.check_access
  def assignedProposals(self, request, access_type, page_name=None,
                        params=None, filter=None, **kwargs):
    """Returns a JSON dict containing all the proposals that would have
    a slot assigned for a specific set of orgs.

    The request.GET limit and offset determines how many and which
    organizations should be returned.

    For params see base.View.public().

    Returns: JSON object with a collection of orgs and proposals. Containing
             identification information and contact information.
    """

    get_dict = request.GET

    if not (get_dict.get('limit') and get_dict.get('offset')):
      return self.json(request, {})

    try:
      limit = max(0, int(get_dict['limit']))
      offset = max(0, int(get_dict['offset']))
    except ValueError:
      return self.json(request, {})

    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)

    fields = {'scope': program_entity,
              'slots >': 0,
              'status': 'active'}

    org_entities = org_logic.logic.getForFields(fields,
        limit=limit, offset=offset)

    orgs_data = {}
    proposals_data = []

    # for each org get the proposals who will be assigned a slot
    for org in org_entities:

      org_data = {'name': org.name}

      fields = {'scope': org,
                'status': 'active',
                'user': org.founder}

      org_admin = org_admin_logic.getForFields(fields, unique=True)

      if org_admin:
        # pylint: disable-msg=E1103
        org_data['admin_name'] = org_admin.name()
        org_data['admin_email'] = org_admin.email

      proposals = student_proposal_logic.getProposalsToBeAcceptedForOrg(
          org, step_size=program_entity.max_slots)

      if not proposals:
        # nothing to accept, next organization
        continue

      # store information about the org
      orgs_data[org.key().id_or_name()] = org_data

      # store each proposal in the dictionary
      for proposal in proposals:
        student_entity = proposal.scope

        proposals_data.append(
            {'key_name': proposal.key().id_or_name(),
            'proposal_title': proposal.title,
            'student_key': student_entity.key().id_or_name(),
            'student_name': student_entity.name(),
            'student_contact': student_entity.email,
            'org_key': org.key().id_or_name()
            })

    # return all the data in JSON format
    data = {'orgs': orgs_data,
            'proposals': proposals_data}

    return self.json(request, data)

  @decorators.merge_params
  @decorators.check_access
  def slots(self, request, acces_type, page_name=None, params=None, **kwargs):
    """Returns a JSON object with all orgs allocation.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View, not used
    """

    from django.utils import simplejson

    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)
    program_slots = program_entity.slots

    filter = {
          'scope': program_entity,
          'status': 'active',
          }

    query = org_logic.logic.getQueryForFields(filter=filter)
    organizations = org_logic.logic.getAll(query)

    locked_slots = adjusted_slots = {}

    if request.method == 'POST' and 'result' in request.POST:
      result = request.POST['result']
      submit = request.GET.get('submit')
      load = request.GET.get('load')
      stored = program_entity.slots_allocation

      if load and stored:
        result = stored

      from_json = simplejson.loads(result)

      locked_slots = dicts.groupDictBy(from_json, 'locked', 'slots')

      if submit:
        program_entity.slots_allocation = result
        program_entity.put()

    orgs = {}
    applications = {}
    max = {}

    for org in organizations:
      orgs[org.link_id] = org
      applications[org.link_id] = org.nr_applications
      max[org.link_id] = min(org.nr_mentors, org.slots_desired)

    max_slots_per_org = program_entity.max_slots
    min_slots_per_org = program_entity.min_slots
    algorithm = 2

    allocator = allocations.Allocator(orgs.keys(), applications, max,
                                      program_slots, max_slots_per_org,
                                      min_slots_per_org, algorithm)

    result = allocator.allocate(locked_slots)

    data = []

    # TODO: remove adjustment here and in the JS
    for link_id, count in result.iteritems():
      org = orgs[link_id]
      data.append({
          'link_id': link_id,
          'slots': count,
          'locked': locked_slots.get(link_id, 0),
          'adjustment': adjusted_slots.get(link_id, 0),
          })

    return self.json(request, data)

  @decorators.merge_params
  @decorators.check_access
  def assignSlots(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """View that allows to assign slots to orgs.
    """

    from soc.modules.gsoc.views.models.organization import view as org_view

    org_params = org_view.getParams().copy()
    org_params['list_template'] = 'soc/program/allocation/allocation.html'
    org_params['list_heading'] = 'soc/program/allocation/heading.html'
    org_params['list_row'] = 'soc/program/allocation/row.html'
    org_params['list_pagination'] = 'soc/list/no_pagination.html'

    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)

    description = self.DEF_SLOTS_ALLOCATION_MSG

    content = self._getOrgsWithProfilesList(program_entity, org_view,
        description, False)
    contents = [content]

    return_url =  "http://%(host)s%(index)s" % {
      'host' : system.getHostname(),
      'index': redirects.getSlotsRedirect(program_entity, params)
      }

    context = {
        'total_slots': program_entity.slots,
        'uses_json': True,
        'uses_slot_allocator': True,
        'return_url': return_url,
        }

    return self._list(request, org_params, contents, page_name, context)

  @decorators.merge_params
  @decorators.check_access
  def showDuplicates(self, request, access_type, page_name=None,
                     params=None, **kwargs):
    """View in which a host can see which students have been assigned
       multiple slots.

    For params see base.view.Public().
    """

    from django.utils import simplejson

    from soc.modules.gsoc.logic.models.proposal_duplicates import logic as duplicates_logic

    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)

    if request.POST and request.POST.get('result'):
      # store result in the datastore
      fields = {'link_id': program_entity.link_id,
                'scope': program_entity,
                'scope_path': program_entity.key().id_or_name(),
                'json_representation' : request.POST['result']
                }
      key_name = duplicates_logic.getKeyNameFromFields(fields)
      duplicates_logic.updateOrCreateFromKeyName(fields, key_name)

      response = simplejson.dumps({'status': 'done'})
      return http.HttpResponse(response)

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['uses_duplicates'] = True
    context['uses_json'] = True
    context['page_name'] = page_name

    # get all orgs for this program who are active and have slots assigned
    fields = {'scope': program_entity,
              'slots >': 0,
              'status': 'active'}

    query = org_logic.logic.getQueryForFields(fields)

    to_json = {
        'nr_of_orgs': query.count(),
        'program_key': program_entity.key().id_or_name()}
    json = simplejson.dumps(to_json)
    context['info'] = json
    context['offset_length'] = 10

    fields = {'link_id': program_entity.link_id,
              'scope': program_entity}
    duplicates = duplicates_logic.getForFields(fields, unique=True)

    if duplicates:
      # we have stored information
      # pylint: disable-msg=E1103
      context['duplicate_cache_content'] = duplicates.json_representation
      context['date_of_calculation'] = duplicates.calculated_on
    else:
      # no information stored
      context['duplicate_cache_content'] = simplejson.dumps({})

    template = 'soc/program/show_duplicates.html'

    return helper.responses.respond(request, template=template, context=context)
    
  @decorators.merge_params
  @decorators.check_access
  def acceptedProjects(self, request, access_type,
                       page_name=None, params=None, filter=None, **kwargs):
    """See base.View.list.
    """
    contents = []
    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    filter = {
        'status': 'accepted',
        'program': program_entity}

    fmt = {'name': program_entity.name}
    description = self.DEF_ACCEPTED_PROJECTS_MSG_FMT % fmt

    from soc.modules.gsoc.views.models import student_project as sp_view

    ap_params = sp_view.view.getParams().copy() # accepted projects
    ap_params['list_action'] = (redirects.getPublicRedirect, ap_params)
    ap_params['list_description'] = description
    ap_params['list_heading'] = 'soc/student_project/list/heading_all.html'
    ap_params['list_row'] = 'soc/student_project/list/row_all.html'

    prefetch = ['mentor', 'student', 'scope']

    return self.list(request, access_type, page_name=page_name,
                     params=ap_params, filter=filter, prefetch=prefetch)

view = View()

accepted_orgs = decorators.view(view.acceptedOrgs)
list_projects = decorators.view(view.acceptedProjects)
admin = decorators.view(view.admin)
assign_slots = decorators.view(view.assignSlots)
assigned_proposals = decorators.view(view.assignedProposals)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
show_duplicates = decorators.view(view.showDuplicates)
slots = decorators.view(view.slots)
home = decorators.view(view.home)
pick = decorators.view(view.pick)

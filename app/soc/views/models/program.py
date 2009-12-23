#!/usr/bin/python2.5
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

"""Views for Programs.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import allocations
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import system
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import organization as org_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import org_app as org_app_logic
from soc.logic.models import program as program_logic
from soc.logic.models import student as student_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import presence
from soc.views.models import document as document_view
from soc.views.models import sponsor as sponsor_view
from soc.views.sitemap import sidebar

from soc.modules.gsoc.logic.models import student_proposal as student_proposal_logic

import soc.cache.logic
import soc.logic.models.program
import soc.models.work


class View(presence.View):
  """View methods for the Program model.
  """

  DEF_SLOTS_ALLOCATION_MSG = ugettext("Use this view to assign slots.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
        host_logic.logic])]
    rights['edit'] = ['checkIsHostForProgram']
    rights['delete'] = ['checkIsDeveloper']
    rights['assign_slots'] = ['checkIsHostForProgram']
    rights['slots'] = ['checkIsHostForProgram']
    rights['show_duplicates'] = ['checkIsHostForProgram']
    rights['assigned_proposals'] = ['checkIsHostForProgram']
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', program_logic.logic])]
    rights['list_projects'] = [('checkIsAfterEvent',
        ['accepted_students_announced_deadline',
         '__all__', program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.program.logic
    new_params['rights'] = rights

    new_params['scope_view'] = sponsor_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'program'

    new_params['extra_dynaexclude'] = ['timeline', 'org_admin_agreement',
        'mentor_agreement', 'student_agreement']

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>assign_slots)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.assign_slots',
          'Assign slots'),
        (r'^%(url_name)s/(?P<access_type>slots)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.slots',
          'Assign slots (JSON)'),
        (r'^%(url_name)s/(?P<access_type>show_duplicates)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.show_duplicates',
          'Show duplicate slot assignments'),
        (r'^%(url_name)s/(?P<access_type>assigned_proposals)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.assigned_proposals',
          "Assigned proposals for multiple organizations"),
        (r'^%(url_name)s/(?P<access_type>accepted_orgs)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.accepted_orgs',
          "List all accepted organizations"),
        (r'^%(url_name)s/(?P<access_type>list_projects)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.list_projects',
          "List all Student Projects"),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Program Link ID',
         },
        ]

    # TODO add clean field to check for uniqueness in link_id and scope_path
    new_params['create_extra_dynaproperties'] = {
        'description': forms.fields.CharField(widget=helper.widgets.TinyMCE(
            attrs={'rows':10, 'cols':40})),
        'accepted_orgs_msg': forms.fields.CharField(required=False,
            widget=helper.widgets.TinyMCE(attrs={'rows':10, 'cols':40})),
        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),
        }

    reference_fields = [
        ('org_admin_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Organization Admin Agreement Document link ID')),
        ('mentor_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Mentor Agreement Document link ID')),
        ('student_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Student Agreement Document link ID')),
        ('home_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Home page Document link ID')),
        ]

    result = {}

    for key, help_text, label in reference_fields:
      result[key] = widgets.ReferenceField(
          reference_url='document', filter=['__scoped__'],
          filter_fields={'prefix': new_params['document_prefix']},
          required=False, label=label, help_text=help_text)

    result['clean'] = cleaning.clean_refs(new_params,
                                          [i for i,_,_ in reference_fields])

    new_params['edit_extra_dynaproperties'] = result

    document_references = [
        ('org_admin_agreement_link_id', 'org_admin_agreement',
         lambda x: x.org_admin_agreement),
        ('mentor_agreement_link_id', 'mentor_agreement',
         lambda x: x.mentor_agreement),
        ('student_agreement_link_id', 'student_agreement',
         lambda x: x.student_agreement),
        ]

    new_params['references'] = document_references

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _getOrgsWithProfilesList(self, program_entity, org_view, description,
                               use_cache):
    """Returns a content of a list of all organizations that got accepted to
    the program and there is an Organization-like entity in datastore.

    Args:
      program_entity: program which list the organizations for
      use_cache: whether or not to use the memcache
      org_view: a view for organization model
      description: the description of the list
    """

    ao_params = org_view.getParams().copy()

    org_logic = ao_params['logic']

    filter = {
        'scope': program_entity,
        'status': ['new', 'active']
        }
    order = ['name']

    if not use_cache:
      entities = org_logic.getForFields(filter=filter, order=order)
    else:
      # only cache if all profiles are created
      fun =  soc.cache.logic.cache(self._getData)
      entities = fun(org_logic.getModel(), filter, order, org_logic)

    result = dicts.rename(ao_params, ao_params['list_params'])
    result['action'] = (redirects.getHomeRedirect, ao_params)
    result['description'] = description
    result['pagination'] = 'soc/list/no_pagination.html'
    result['data'] = entities

    return result

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

    program = program_logic.logic.getFromKeyFieldsOr404(kwargs)
    program_slots = program.slots

    filter = {
          'scope': program,
          'status': 'active',
          }

    query = org_logic.logic.getQueryForFields(filter=filter)
    organizations = org_logic.logic.getAll(query)

    locked_slots = adjusted_slots = {}

    if request.method == 'POST' and 'result' in request.POST:
      result = request.POST['result']
      submit = request.GET.get('submit')
      load = request.GET.get('load')
      stored = program.slots_allocation

      if load and stored:
        result = stored

      from_json = simplejson.loads(result)

      locked_slots = dicts.groupDictBy(from_json, 'locked', 'slots')

      if submit:
        program.slots_allocation = result
        program.put()

    orgs = {}
    applications = {}
    max = {}

    for org in organizations:
      orgs[org.link_id] = org
      applications[org.link_id] = org.nr_applications
      max[org.link_id] = min(org.nr_mentors, org.slots_desired)

    max_slots_per_org = program.max_slots
    min_slots_per_org = program.min_slots
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

    from soc.views.models import organization as organization_view

    org_params = organization_view.view.getParams().copy()
    org_params['list_template'] = 'soc/program/allocation/allocation.html'
    org_params['list_heading'] = 'soc/program/allocation/heading.html'
    org_params['list_row'] = 'soc/program/allocation/row.html'
    org_params['list_pagination'] = 'soc/list/no_pagination.html'

    program = program_logic.logic.getFromKeyFieldsOr404(kwargs)

    description = self.DEF_SLOTS_ALLOCATION_MSG

    filter = {
        'scope': program,
        'status': 'active',
        }

    content = self._getAcceptedOrgsList(description, org_params, filter, False)

    contents = [content]

    return_url =  "http://%(host)s%(index)s" % {
      'host' : system.getHostname(),
      'index': redirects.getSlotsRedirect(program, params)
      }

    context = {
        'total_slots': program.slots,
        'uses_json': True,
        'uses_slot_allocator': True,
        'return_url': return_url,
        }

    return self._list(request, org_params, contents, page_name, context)


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

    program_entity = program_logic.logic.getFromKeyFieldsOr404(kwargs)

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

      org_admin = org_admin_logic.logic.getForFields(fields, unique=True)

      if org_admin:
        # pylint: disable-msg=E1103
        org_data['admin_name'] = org_admin.name()
        org_data['admin_email'] = org_admin.email

      proposals = student_proposal_logic.logic.getProposalsToBeAcceptedForOrg(
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

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    super(View, self)._editPost(request, entity, fields)

    if not entity:
      # there is no existing entity so create a new timeline
      fields['timeline'] = self._params['logic'].createTimelineForType(fields)
    else:
      # use the timeline from the entity
      fields['timeline'] = entity.timeline

  def _getStandardProgramEntries(self, entity, id, user, params):
    """Returns those entries for a program which are available to regular users,
    not only to hosts or developers. 
    """

    items = []

    # show the documents for this program, even for not logged in users
    items += document_view.view.getMenusForScope(entity, params)

    # also show time-dependent entities for a given user
    items += self._getTimeDependentEntries(entity, params, id, user)

    return items

  def _getTimeDependentEntries(self, program_entity, params, id, user):
    """Returns a list with time dependent menu items. Should be redefined
    in a module specific view.
    """

    return []

  def _getHostEntries(self, entity, params, prefix):
    """Returns a list with menu items for program host.
    
    Args:
      entity: program entity to get the entries for
      params: view specific params
      prefix: module prefix for the program entity
    """

    items = []

    # add link to edit Program Profile
    items += [(redirects.getEditRedirect(entity, params),
            'Edit Program Profile', 'any_access')]
    # add link to edit Program Timeline
    items += [(redirects.getEditRedirect(entity, 
            {'url_name': prefix + '/timeline'}),
            "Edit Program Timeline", 'any_access')]
    # add link to create a new Program Document
    items += [(redirects.getCreateDocumentRedirect(
            entity, params['document_prefix']),
            "Create a New Document", 'any_access')]
    # add link to list all Program Document
    items += [(redirects.getListDocumentsRedirect(
            entity, params['document_prefix']),
            "List Documents", 'any_access')]

    return items

  def _getStudentEntries(self, program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    if timeline_helper.isBeforeEvent(program_entity.timeline, 'program_end'):
      items += [(redirects.getEditRedirect(student_entity,
          {'url_name': prefix + '/student'}),
          "Edit my Student Profile", 'any_access')]

      items += [(redirects.getManageRedirect(student_entity,
          {'url_name': prefix + '/student'}),
          "Resign as a Student", 'any_access')]

    return items

  def _getOrganizationEntries(self, program_entity, org_admin_entity,
                              mentor_entity, params, id, user):
    """Returns a list with menu items for org admins and mentors in a
       specific program.
    """

    # TODO(ljvderijk) think about adding specific org items like submit review

    items = []

    return items


view = View()

accepted_orgs = responses.redirectLegacyRequest
list_projects = responses.redirectLegacyRequest
admin = responses.redirectLegacyRequest
assign_slots = responses.redirectLegacyRequest
assigned_proposals = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest
show_duplicates = responses.redirectLegacyRequest
slots = responses.redirectLegacyRequest
home = responses.redirectLegacyRequest
pick = responses.redirectLegacyRequest

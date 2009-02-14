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

"""Views for Organization App profiles.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils import simplejson

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import models as model_logic
from soc.logic.models import program as program_logic
from soc.logic.models import org_app as org_app_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import group_app
from soc.views.models import program as program_view

import soc.logic.dicts


class View(group_app.View):
  """View methods for the Organization Application model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['delete'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic]),
                       ('checkIsActivePeriod', ['org_signup', 'scope_path'])]
    rights['edit'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic]),
                       ('checkIsActivePeriod', ['org_signup', 'scope_path'])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_self'] = ['checkIsUser']
    rights['public'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic])]
    rights['review'] = ['checkIsHostForProgramInScope',
                        ('checkCanReviewGroupApp', [org_app_logic.logic])]
    rights['review_overview'] = ['checkIsHostForProgramInScope']
    rights['bulk_accept'] = ['checkIsHostForProgramInScope']
    rights['apply'] = ['checkIsUser',
                             ('checkCanCreateOrgApp', ['org_signup'])]

    new_params = {}

    new_params['rights'] = rights
    new_params['logic'] = org_app_logic.logic

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['sidebar_grouping'] = 'Organizations'

    patterns = [(r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.create',
        'Create an %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>bulk_accept)/%(scope)s$',
        'soc.views.models.%(module_name)s.bulk_accept',
        'Bulk Acceptation of %(name_plural)s'),]

    new_params['extra_django_patterns'] = patterns
    new_params['extra_key_order'] = ['admin_agreement',
                                     'agreed_to_admin_agreement']

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin', 'status',
        'created_on', 'last_modified_on']

    new_params['create_extra_dynafields'] = {
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'admin_agreement': forms.fields.Field(required=False,
            widget=widgets.AgreementField),
        'agreed_to_admin_agreement': forms.fields.BooleanField(
            initial=False, required=True),
        'clean_ideas': cleaning.clean_url('ideas'),
        'clean_contrib_template': cleaning.clean_url('contrib_template'),
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            model_logic.organization, org_app_logic)}

    # get rid of the clean method
    new_params['edit_extra_dynafields'] = {
        'clean': (lambda x: x.cleaned_data)}

    new_params['name'] = "Organization Application"
    new_params['name_plural'] = "Organization Applications"
    new_params['name_short'] = "Org App"
    new_params['url_name'] = "org_app"
    new_params['group_url_name'] = 'org'

    new_params['review_template'] = 'soc/org_app/review.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @ decorators.merge_params
  def reviewOverview(self, request, access_type,
               page_name=None, params=None, **kwargs):

    params['list_template'] = 'soc/org_app/review_overview.html'
    context = {'bulk_accept_link': '/org_app/bulk_accept/%(scope_path)s' %(
        kwargs)}

    return super(View, self).reviewOverview(request, access_type,
        page_name=page_name, params=params, context=context, **kwargs)

  def _editContext(self, request, context):
    """See base.View._editContext.
    """

    entity = context['entity']
    form = context['form']

    if 'scope_path' in form.initial:
      scope_path = form.initial['scope_path']
    elif 'scope_path' in request.POST:
      # TODO: do this nicely
      scope_path = request.POST['scope_path']
    else:
      # TODO: is this always sufficient?
      del form.fields['admin_agreement']
      return

    entity = program_logic.logic.getFromKeyName(scope_path)

    if not entity or not entity.org_admin_agreement:
      return

    content = entity.org_admin_agreement.content

    form.fields['admin_agreement'].widget.text = content


  def _review(self, request, params, app_entity, status, **kwargs):
    """Sends out an email if an org_app has been reviewed and accepted.

    For params see group_app.View._review().
    """

    if status == 'accepted':
      #TODO(ljvderijk) create the email template
      pass


  @decorators.merge_params
  @decorators.check_access
  def bulkAccept(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Returns a HTTP Response containing JSON information needed 
       to bulk-accept orgs.
    """

    program_entity = program_logic.logic.getFromKeyName(kwargs['scope_path'])

    # get all pre-accepted org applications for the given program
    filter = {'scope' : program_entity,
              'status' : 'pre-accepted'}
    org_app_entities = org_app_logic.logic.getForFields(filter=filter)

    # convert each application into a dictionary containing only the fields
    # given by the dict_filter
    dict_filter = ['link_id', 'name']
    org_apps = [dicts.filter(i.toDict(), dict_filter) for i in org_app_entities]

    to_json = {
        'program' : program_entity.name,
        'nr_applications' : len(org_apps),
        'application_type' : params['name_plural'],
        'applications': org_apps,
        'link' : '/org_app/review/%s/(link_id)?status=accepted' %(
            program_entity.key().name()),
        }

    json = simplejson.dumps(to_json)

    # use the standard JSON template to return our response
    context = {'json': json}
    template = 'soc/json.html'

    response = responses.respond(request, template, context)
    # TODO IE7 seems to ignore the headers
    response['Pragma'] = 'no-cache'
    response['Cache-Control'] = 'no-cache, must-revalidate'
    return response


view = View()

bulk_accept = view.bulkAccept
create = view.create
delete = view.delete
edit = view.edit
list = view.list
list_self = view.listSelf
public = view.public
export = view.export
review = view.review
review_overview = view.reviewOverview


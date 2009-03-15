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


import os

from django import forms
from django.utils import simplejson

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import mail_dispatcher
from soc.logic import models as model_logic
from soc.logic.models import program as program_logic
from soc.logic.models import org_app as org_app_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import group_app
from soc.views.models import program as program_view


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
    rights['delete'] = ['checkIsDeveloper']
    rights['edit'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic]),
                       ('checkIsActivePeriod', ['org_signup', 'scope_path'])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_self'] = ['checkIsUser']
    rights['show'] = ['checkIsUser']
    rights['review'] = ['checkIsHostForProgramInScope',
                        ('checkCanReviewGroupApp', [org_app_logic.logic])]
    rights['review_overview'] = ['checkIsHostForProgramInScope']
    rights['bulk_accept'] = ['checkIsHostForProgramInScope']
    rights['bulk_reject'] = ['checkIsHostForProgramInScope']
    rights['apply'] = ['checkIsUser',
                             ('checkCanCreateOrgApp', ['org_signup']),
                       'checkIsNotStudentForProgramInScope']

    new_params = {}

    new_params['rights'] = rights
    new_params['logic'] = org_app_logic.logic

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['sidebar_grouping'] = 'Organizations'

    new_params['list_key_order'] = [
        'link_id', 'scope_path', 'name', 'home_page', 'email',
        'description', 'why_applying','pub_mailing_list','irc_channel',
        'member_criteria', 'prior_participation', 'prior_application',
        'license_name', 'ideas', 'dev_mailing_list', 'contrib_template',
        'contrib_disappears', 'member_disappears', 'encourage_contribs',
        'continued_contribs']

    patterns = [(r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.create',
        'Create an %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>bulk_accept)/%(scope)s$',
        'soc.views.models.%(module_name)s.bulk_accept',
        'Bulk Acceptation of %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>bulk_reject)/%(scope)s$',
        'soc.views.models.%(module_name)s.bulk_reject',
        'Bulk Rejection of %(name_plural)s'),]

    new_params['extra_django_patterns'] = patterns
    new_params['extra_key_order'] = ['admin_agreement',
                                     'agreed_to_admin_agreement']

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin', 'status',
        'created_on', 'last_modified_on']

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'contrib_template': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'description': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'admin_agreement': forms.fields.Field(required=False,
            widget=widgets.AgreementField),
        'agreed_to_admin_agreement': forms.fields.BooleanField(
            initial=False, required=True),

        'clean_description': cleaning.clean_html_content('description'),
        'clean_contrib_template': cleaning.clean_html_content('contrib_template'),
        'clean_ideas': cleaning.clean_url('ideas'),
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            model_logic.organization, org_app_logic)}

    # get rid of the clean method
    new_params['edit_extra_dynaproperties'] = {
        'clean': (lambda x: x.cleaned_data)}

    new_params['name'] = "Organization Application"
    new_params['name_plural'] = "Organization Applications"
    new_params['name_short'] = "Org App"
    new_params['url_name'] = "org_app"
    new_params['group_name'] = "Organization"
    new_params['group_url_name'] = 'org'

    new_params['review_template'] = 'soc/org_app/review.html'
    # TODO use a proper template that works for each program
    new_params['accepted_mail_template'] = 'soc/org_app/mail/accepted_gsoc2009.html'
    new_params['rejected_mail_template'] = 'soc/org_app/mail/rejected.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @ decorators.merge_params
  def reviewOverview(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """View that allows to see organization application review overview.

       For Args see base.View.public().
    """

    params['list_template'] = 'soc/org_app/review_overview.html'
    context = {
        'bulk_accept_link': '/org_app/bulk_accept/%(scope_path)s' % (kwargs),
        'bulk_reject_link': '/org_app/bulk_reject/%(scope_path)s' % (kwargs),}

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
      scope_path = request.POST['scope_path']
    else:
      del form.fields['admin_agreement']
      return

    entity = program_logic.logic.getFromKeyName(scope_path)

    if not (entity and entity.org_admin_agreement):
      return

    agreement = entity.org_admin_agreement

    content = agreement.content
    params = {'url_name': 'document'}

    widget = form.fields['admin_agreement'].widget
    widget.text = content
    widget.url = redirects.getPublicRedirect(agreement, params)

  def _review(self, request, params, app_entity, status, **kwargs):
    """Sends out an email if an org_app has been accepted or rejected.

    For params see group_app.View._review().
    """

    if status == 'accepted' or status == 'rejected':

      default_sender = mail_dispatcher.getDefaultMailSender()

      if not default_sender:
        # no default sender abort
        return
      else:
        (sender_name, sender) = default_sender

      # construct the contents of the email
      user_entity = app_entity.applicant
      to = accounts.denormalizeAccount(user_entity.account).email()

      context = {'sender': sender,
              'to': to,
              'sender_name': sender_name,
              'to_name': user_entity.name,
              'program_name': app_entity.scope.name}

      if status == 'accepted':
        # use the accepted template and subject
        template = params['accepted_mail_template']
        context['subject'] = 'Congratulations!'
        context['HTTP_host'] = 'http://%s' %(os.environ['HTTP_HOST'])
      elif status == 'rejected':
        # use the rejected template and subject
        template = params['rejected_mail_template']
        context['subject'] = 'Thank you for your application'

      # send out the constructed email
      mail_dispatcher.sendMailFromTemplate(template, context)

  @decorators.merge_params
  @decorators.check_access
  def bulkAccept(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Returns a HTTP Response containing JSON information needed
       to bulk-accept orgs.
    """

    program_keyname = kwargs['scope_path']
    return self._bulkReview(request, params, 'pre-accepted', 'accepted',
        program_keyname)

  @decorators.merge_params
  @decorators.check_access
  def bulkReject(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Returns a HTTP Response containing JSON information needed
       to bulk-accept orgs.
    """

    program_keyname = kwargs['scope_path']
    return self._bulkReview(request, params, 'pre-rejected', 'rejected',
                            program_keyname)

  def _bulkReview(self, request, params, from_status, to_status,
                  program_keyname):
    """Returns a HTTP Response containing JSON information needed
       to bulk-review organization applications.

       Args:
         request: Standard Django HTTP Request object
         params: Params for this view
         from_status: The status for the applications which should
                      be reviewed (can be a list)
         to_status: The status to which all applications should be changed to
         program_keyname: The keyname for the program to which
                          the application belongs
    """

    # get the program entity from the keyname
    program_entity = program_logic.logic.getFromKeyName(program_keyname)

    # get all the organization applications for the 
    # given program and from_status
    filter = {'scope': program_entity,
              'status': from_status}

    org_app_entities = params['logic'].getForFields(filter=filter)

    # convert each application into a dictionary containing only the fields
    # given by the dict_filter
    dict_filter = ['link_id', 'name']
    org_apps = [dicts.filter(i.toDict(), dict_filter) for i in org_app_entities]

    to_json = {
        'program' : program_entity.name,
        'nr_applications' : len(org_apps),
        'application_type' : params['name_plural'],
        'applications': org_apps,
        'link' : '/%s/review/%s/(link_id)?status=%s' %(
            params['url_name'] ,program_entity.key().name(), to_status),
        }

    json = simplejson.dumps(to_json)

    # use the standard JSON template to return our response
    context = {'json': json}
    template = 'soc/json.html'

    return responses.respond(request, template, context)


view = View()

admin = decorators.view(view.admin)
bulk_accept = decorators.view(view.bulkAccept)
bulk_reject = decorators.view(view.bulkReject)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_self = decorators.view(view.listSelf)
public = decorators.view(view.public)
export = decorators.view(view.export)
review = decorators.view(view.review)
review_overview = decorators.view(view.reviewOverview)

#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Views for OrgAppSurveys.
"""


__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django import http

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import surveys
from soc.views.helper import widgets
from soc.views.models import survey as survey_view

from soc.logic.models.org_app_survey import logic as org_app_logic


class View(survey_view.View):
  """View methods for the ProjectSurvey model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = org_app_logic

    new_params['name'] = "Org Application Survey"
    new_params['url_name'] = 'org_app'

    new_params['extra_dynaexclude'] = ['taking_access']

    new_params['survey_take_form'] = OrgAppSurveyForm
    new_params['survey_record_form'] = OrgAppRecordForm

    new_params['extra_django_patterns'] = [
         (r'^%(url_name)s/(?P<access_type>list_self)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.list_self',
         'Overview of %(name_plural)s Taken by You'),
         (r'^%(url_name)s/(?P<access_type>review)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.review',
         'Review %(name)s from '),
         (r'^%(url_name)s/(?P<access_type>review_overview)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.review_overview',
         'Overview of %(name_plural)s for Review')
         ]

    new_params['review_template'] = 'soc/org_app_survey/review.html'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    # create the form to review an Organization Application
    dynaproperties = {
        'status': forms.fields.ChoiceField(required=True,
            label = 'New Status',
            choices = [('accepted', 'Accept'),
                       ('pre-accepted', 'Pre-Accept'),
                       ('rejected', 'Reject'),
                       ('pre-rejected', 'Pre-Reject'),
                       ('ignored', 'Ignore'),])
        }

    review_form = dynaform.newDynaForm(
        dynabase = self._params['dynabase'],
        dynaproperties = dynaproperties,
    )

    self._params['review_form'] = review_form

    # define the params for the OrgAppSurveyRecord listing
    record_list_params = dicts.rename(self._params,
                                      self._params['list_params'])
    record_list_params['list_params'] = self._params['list_params']
    record_list_params['logic'] = self._params['logic'].getRecordLogic()
    record_list_params['js_uses_all'] = self._params['js_uses_all']
    record_list_params['list_template'] = self._params['list_template']

    # define the fields for the public list
    record_list_params['public_field_keys'] = ['name', 'home_page']
    record_list_params['public_field_names'] = ['Name', 'Home Page']

    # define the fields for the self list
    record_list_params['self_field_keys'] = [
        'name', 'main_admin', 'backup_admin'
    ]
    record_list_params['self_field_names'] = [
        'Organization Name', 'Main Admin', 'Backup Admin'
    ]
    record_list_params['self_field_extra'] = lambda entity: {
        'main_admin': entity.main_admin.name,
        'backup_admin': entity.backup_admin.name}

    # define the fields for the overview list
    record_list_params['overview_field_keys'] = [
        'name', 'home_page', 'status'
    ]
    record_list_params['overview_field_names'] = [
        'Organization Name', 'Home Page', 'Application Status'
    ]
    record_list_params['overview_field_extra'] = lambda entity: {
        'home_page': lists.urlize(entity.home_page)}
    record_list_params['overview_button_global'] = [{
          'bounds': [0,'all'],
          'id': 'bulk_process',
          'caption': 'Bulk Accept/Reject Organizations',
          'type': 'post',
          'parameters': {
            'url': '',
         }}]

    self._params['record_list_params'] = record_list_params

  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays the create page for this entity type.

    If an OrgAppSurvey already exists it will redirect to the edit page.
    """

    params = dicts.merge(params, self._params)
    program_view = params['scope_view']
    program_logic = program_view.getParams()['logic']

    program_entity = program_logic.getFromKeyName(kwargs['scope_path'])
    org_app = org_app_logic.getForProgram(program_entity)

    if org_app:
      # redirect to edit page
      return http.HttpResponseRedirect(
          redirects.getEditRedirect(org_app, params))
    else:
      # show create page
      return super(View, self).create(request, access_type,
                                      page_name=page_name, params=params,
                                      **kwargs)

  def _getSurveyRecordFor(self, survey, request, params):
    """Returns the SurveyRecord for the given Survey and request.

    This method also take the ID specified as GET param into
    account when querying for the SurveyRecord.

    For params see survey.View._getSurveyRecordFor().
    """

    get_dict = request.GET
    record_id = get_dict.get('id', None)

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    if not record_id or not record_id.isdigit():
      return None
    else:
      return record_logic.getFromIDOr404(int(record_id))

  def _takeGet(self, request, template, context, params, entity, record,
              **kwargs):
    """Hooking into the view for the take's page GET request.

    For params see survey.View._takeGet().
    """

    # the form action should contain the requested record
    if record:
      context['form_action'] = "?id=%s" %(request.GET['id'])

  def _takePost(self, request, params, entity, record, properties):
    """Hook into the view for the take's page POST request.

    For params see survey.View._takePost().
    """

    from soc.logic.models.user import logic as user_logic

    if not record:
      # creating a new record
      user_entity = user_logic.getForCurrentAccount()
      properties['main_admin'] = user_entity

      if properties['agreed_to_tos']:
        properties['agreed_to_admin_agreement'] = True

    # remove fields we don't need to store in the SurveyRecord
    properties.pop('tos')
    properties.pop('agreed_to_tos')

  def _getRedirectOnSuccessfulTake(self, request, params, survey, record):
    """Returns a path to which the user should be redirected after successfully
    taking a OrgAppSurvey.
    """
    return request.path + '?id=' + str(record.key().id_or_name())

  @decorators.merge_params
  @decorators.check_access
  def listSelf(self, request, access_type, page_name=None,
           params=None, **kwargs):
    """View that lists all the OrgAppRecords you have access to.

    For Args see base.View().public().
    """

    survey_logic = params['logic']

    entity = survey_logic.getFromKeyFieldsOr404(kwargs)

    list_params = params['record_list_params'].copy()

    if timeline_helper.isActivePeriod(entity, 'survey'):
      info = {'url_name': params['url_name'],
              'survey':entity}
      list_params['public_row_extra'] = lambda entity: {
          'link': redirects.getRetakeOrgAppSurveyRedirect(entity, info)
      }
    else:
      list_params['public_row_extra'] = lambda entity: {
          'link': redirects.getViewSurveyRecordRedirect(entity, params)
      }

    ma_params = list_params.copy()
    ma_params['list_description'] = \
        'List of Applications for which you are Main Admin.'

    ba_params = list_params.copy()
    ba_params['list_description'] = \
        'List of Applications for which your are Backup Admin.'

    if request.GET.get('fmt') == 'json':
      return self._getListSelfData(request, entity, ma_params, ba_params)

    ma_list = lists.getListGenerator(request, ma_params, idx=0)
    ba_list = lists.getListGenerator(request, ba_params, idx=1)

    contents = [ma_list, ba_list]

    return self._list(request, list_params, contents, page_name)

  def _getListSelfData(self, request, entity, ma_params, ba_params):
    """Returns the listSelf data.
    """

    from django.utils import simplejson

    from soc.logic.models.user import logic as user_logic

    user_entity = user_logic.getForCurrentAccount()

    idx = request.GET.get('idx', '')
    idx = int(idx) if idx.isdigit() else -1

    if idx == 0:
      fields = {'survey': entity,
                'main_admin': user_entity}
      params = ma_params
    elif idx == 1:
      fields = {'survey': entity,
                'backup_admin': user_entity}
      params = ba_params
    else:
        return responses.jsonErrorResponse(request, "idx not valid")

    contents = lists.getListData(request, params, fields, visibility='self')

    json = simplejson.dumps(contents)
    return responses.jsonResponse(request, json)

  @decorators.merge_params
  @decorators.check_access
  def reviewOverview(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays a list of applications that are in a different
    status of the application process.
    """

    from django.utils import simplejson

    survey_logic = params['logic']

    entity = survey_logic.getFromKeyFieldsOr404(kwargs)

    if request.POST:
      # POST request received, check and respond to button actions
      post_dict = request.POST

      if post_dict.get('button_id') == 'bulk_process':
        params['bulk_process_task'].start(entity.scope)

      return http.HttpResponse()

    list_params = params['record_list_params'].copy()
    list_params['list_description'] = (
        'List of all the Organization Applications made to the %s program. '
        'Click an application to review it, or use the buttons on the top of '
        'the list for bulk actions.' %(entity.scope.name))

    info = {'url_name': params['url_name'],
            'survey':entity}
    list_params['public_row_extra'] = lambda entity: {
        'link': redirects.getRetakeOrgAppSurveyRedirect(entity, info)
    }

    if request.GET.get('fmt') == 'json':
      # get all records for the entity specified in the URL
      fields = {'survey': entity}
      # use the overview visibility to show the correct columns to the Host
      contents = lists.getListData(request, list_params, fields,
                                   visibility='overview')

      json = simplejson.dumps(contents)
      return responses.jsonResponse(request, json)

    overview_list = lists.getListGenerator(request, list_params, idx=0)
    contents = [overview_list]

    return self._list(request, list_params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def review(self, request, access_type, page_name=None, params=None,
             **kwargs):
    """View that lists a OrgAppSurveyRecord to be reviewed.

    For Args see base.View().public().
    """

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    try:
      survey_entity = survey_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    get_dict = request.GET
    record_id = get_dict.get('id')

    if record_id and record_id.isdigit():
      record_id = int(record_id)
      record_entity = record_logic.getFromIDOr404(record_id)
    else:
      raise out_of_band.Error('No valid Record ID given')

    if record_entity.survey.key() != survey_entity.key():
      # record does not match the retrieved survey
      raise out_of_band.Error('Record ID does not match the given survey')

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = '%s %s' %(page_name, record_entity.name)
    context['entity'] = survey_entity
    context['record'] = record_entity

    # store the read only survey form in the context
    survey_form = params['survey_record_form'](
       survey=survey_entity,
       survey_record=record_entity,
       survey_logic=self._params['logic'],
       read_only=True)
    survey_form.getFields()
    context['survey_form'] = survey_form

    if request.POST:
      return self.reviewPost(request, params, context, survey_entity,
                             record_entity)
    else:
      return self.reviewGet(request, params, context, survey_entity,
                            record_entity)

  def reviewGet(self, request, params, context, survey, record):
    """Handles the GET request for reviewing an OrgAppSurveyRecord.

    Args:
      request: HTTPRequest object
      params: View params dict
      context: page context dictionary
      survey: OrgAppSurvey entity
      record: OrgAppSurveyRecord under review
    """

    review_form = params['review_form']()
    review_form.fields['status'].initial = record.status
    context['review_form'] = review_form

    template = params['review_template']
    return responses.respond(request, template, context)

  def reviewPost(self, request, params, context, survey, record):
    """Handles the GET request for reviewing an OrgAppSurveyRecord.

    Args:
      request: HTTPRequest object
      params: View params dict
      context: page context dictionary
      survey: OrgAppSurvey entity
      record: OrgAppSurveyRecord under review
    """

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    post_dict = request.POST
    review_form = params['review_form'](post_dict)

    if not review_form.is_valid():
      context['review_form'] = review_form
      template = params['review_template']
      return responses.respond(request, template, context)

    new_status = review_form.cleaned_data['status']

    # only update if the status actually changes
    if record.status != new_status:
      fields = {'status' : new_status}
      record_logic.updateEntityProperties(record, fields)

    # TODO(ljvderijk) fix redirect
    return http.HttpResponseRedirect('')

class OrgAppSurveyForm(surveys.SurveyTakeForm):
  """Extends SurveyTakeForm by adding fields required for OrgAppSurvey.
  """

  def setCleaners(self, post_dict=None):
    """Add the new fields to the clean_data.

    For args see surveys.SurveyTakeForm.setCleaners().
    """

    clean_data = super(OrgAppSurveyForm, self).setCleaners(
        post_dict=post_dict)

    if post_dict:
      clean_data['name'] = post_dict.get('name', None)
      clean_data['description'] = post_dict.get('description', None)
      clean_data['home_page'] = post_dict.get('home_page', None)
      clean_data['backup_admin'] = post_dict.get('backup_admin', None)
      clean_data['agreed_to_tos'] = post_dict.get('agreed_to_tos', None)

    return clean_data

  def clean_backup_admin(self):
    """Cleans the backup admin field.

    Backup admin may not be equal to the Main admin if a SurveyRecord already
    exists otherwise it may not be equal to the current user.
    """

    from soc.logic import cleaning

    if self.survey_record:
      backup_admin = cleaning.clean_existing_user('backup_admin')(self)
      main_admin = self.survey_record.main_admin
      if main_admin.key() == backup_admin.key():
        #raise validation error, non valid backup admin
        raise forms.ValidationError('You may not enter the Main Admin here.')
    else:
      backup_admin = cleaning.clean_users_not_same('backup_admin')(self)

    return backup_admin

  def getFields(self, post_dict=None):
    """Set the values for the extra fields.

    Args:
        post_dict: dict with POST data if exists
    """

    # set the field values
    if not self.has_post and self.survey_record:
      # we have a survey record to set the data
      self.data['name'] = self.survey_record.name
      self.data['description'] = self.survey_record.description
      self.data['home_page'] = self.survey_record.home_page
      self.data['backup_admin'] = self.survey_record.backup_admin.link_id
      self.data['agreed_to_tos'] = self.survey_record.agreed_to_admin_agreement

    return super(OrgAppSurveyForm, self).getFields(post_dict)

  def insertFields(self):
    """Add the necessary fields to the Form.
    """

    # add common survey fields
    fields = super(OrgAppSurveyForm, self).insertFields()

    name = forms.fields.CharField(
        label='Organization Name', required=True,
        initial=self.data.get('name'))

    description = forms.fields.CharField(
        label='Description', required=True,
        widget=forms.widgets.Textarea,
        initial=self.data.get('description'))

    home_page = forms.fields.URLField(
        label='Home page', required=True, initial=self.data.get('home_page'))

    backup_admin = forms.fields.CharField(
        label='Backup Admin (Link ID)', required=True,
        initial=self.data.get('backup_admin'))

    tos_field = forms.fields.CharField(
        label='Admin Agreement', required=False,
        widget=widgets.AgreementField)

    # set the contents to the current ToS for Org Admins
    admin_agreement = self.survey.scope.org_admin_agreement
    if admin_agreement:
      tos_field.widget.text = admin_agreement.content

      params = {'url_name': 'document'}
      tos_field.widget.url = redirects.getPublicRedirect(admin_agreement,
                                                         params)

    agreed_to_tos = forms.fields.BooleanField(
        label='I agree to the Admin Agreement',
        required=True, initial=self.data.get('agreed_to_tos'))

    # add fields to the top of the form
    fields.insert(0, 'name', name)
    fields.insert(1, 'description', description)
    fields.insert(2, 'home_page', home_page)
    # add fields to the bottom of the form
    fields['backup_admin'] = backup_admin
    fields['tos'] = tos_field
    fields['agreed_to_tos'] = agreed_to_tos

    return fields


class OrgAppRecordForm(surveys.SurveyRecordForm):
  """RecordForm for the OrgAppSurveyForm.
  """

  def getFields(self, *args):
    """Add the extra grade field's value from survey_record.
    """

    # set the field values
    if self.survey_record:
      self.data['name'] = self.survey_record.name
      self.data['description'] = self.survey_record.description
      self.data['home_page'] = self.survey_record.home_page
      self.data['backup_admin'] = self.survey_record.backup_admin.link_id
      self.data['agreed_to_tos'] = self.survey_record.agreed_to_admin_agreement

    return super(OrgAppRecordForm, self).getFields(*args)

  def insertFields(self):
    """Add custom fields to the Survey form.
    """

    # add common survey fields
    fields = super(OrgAppRecordForm, self).insertFields()

    name = forms.fields.CharField(
        label='Organization Name',
        widget=widgets.PlainTextWidget,
        required=True, initial=self.data.get('name'))

    description = forms.fields.CharField(
        label='Description',
        widget=widgets.PlainTextWidget,
        required=True, initial=self.data.get('description'))

    home_page = forms.fields.URLField(
        label='Home page',
        widget=widgets.PlainTextWidget,
        required=True, initial=self.data.get('home_page'))

    backup_admin = forms.fields.CharField(
        label='Backup Admin (Link ID)',
        widget=widgets.PlainTextWidget,
        required=True, initial=self.data.get('backup_admin'))

    agreed_to_tos = forms.fields.BooleanField(
        label='I agree to the Admin Agreement',
        required=True, initial=self.data.get('agreed_to_tos'))
    agreed_to_tos.widget.attrs['disabled'] = 'disabled'

    # add fields to the top of the form
    fields.insert(0, 'name', name)
    fields.insert(1, 'description', description)
    fields.insert(2, 'home_page', home_page)
    # add fields to the bottom of the form
    fields['backup_admin'] = backup_admin
    fields['agreed_to_tos'] = agreed_to_tos

    return fields

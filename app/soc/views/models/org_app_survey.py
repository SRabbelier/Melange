#!/usr/bin/python2.5
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
         ]

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

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
  def list_self(self, request, access_type, page_name=None,
           params=None, **kwargs):
    """View that lists all the OrgRecords you have access to.

    For Args see base.View().public().
    """

    from soc.logic.models.user import logic as user_logic

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    try:
      entity = survey_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['entity'] = entity

    list_contents = []
    user_entity = user_logic.getForCurrentAccount()

    list_params = params.copy()
    list_params['logic'] = record_logic
    list_params['list_heading'] = 'soc/org_app_survey/list/records_heading.html'
    list_params['list_row'] = 'soc/org_app_survey/list/records_row.html'

    if timeline_helper.isActivePeriod(entity, 'survey'):
      info = {'url_name': list_params['url_name'],
              'survey':entity}
      list_params['public_row_extra'] = lambda entity: {
          'link': redirects.getRetakeOrgAppSurveyRedirect(entity, info)
      }
    else:
      list_params['public_row_extra'] = lambda entity: {
          'link': redirects.getViewSurveyRecordRedirect(entity, list_params)
      }

    fields = {'survey': entity,
              'main_admin': user_entity}
    list_params['list_description'] = \
        'List of Applications for which you are Main Admin.'
    main_list = lists.getListContent(request, list_params, fields,
                                     need_content=True, idx=0)
# TODO(LIST)
    if main_list:
      list_contents.append(main_list)

    fields = {'survey': entity,
              'backup_admin': user_entity}
    list_params['list_description'] = \
        'List of Applications for which your are Backup Admin.'
    backup_list = lists.getListContent(request, list_params, fields,
                                       need_content=True, idx=1)

    if backup_list:
      list_contents.append(backup_list)

    return self._list(request, list_params, list_contents, page_name, context)


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

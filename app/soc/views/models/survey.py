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

"""Views for Surveys.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]

import csv
import datetime
import re
import StringIO
import string

from google.appengine.ext import db

from django import forms
from django import http
from django.utils import simplejson

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models.survey import GRADES
from soc.logic.models.survey import logic as survey_logic
from soc.logic.models.user import logic as user_logic
from soc.models.survey import Survey
from soc.models.survey_record import SurveyRecord
from soc.models.user import User
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import surveys
from soc.views.helper import widgets
from soc.views.models import base


CHOICE_TYPES = set(('selection', 'pick_multi', 'choice', 'pick_quant'))
TEXT_TYPES = set(('long_answer', 'short_answer'))
PROPERTY_TYPES = tuple(CHOICE_TYPES) + tuple(TEXT_TYPES)

_short_answer = ("Short Answer",
                "Less than 40 characters. Rendered as a text input. "
                "It's possible to add a free form question (Content) "
                "and a in-input prompt/example text.")
_choice = ("Selection",
           "Can be set as a single choice (selection) or multiple choice "
           "(pick_multi) question. Rendered as a select (single choice) "
           "or a group of checkboxes (multiple choice). It's possible to "
           "add a free form question (Content) and as many free form options "
           "as wanted. Each option can be edited (double-click), deleted "
           "(click on (-) button) or reordered (drag and drop).")
_long_answer = ("Long Answer",
                "Unlimited length, auto-growing field. Rendered as a textarea. "
                 "It's possible to add a free form question (Content) and "
                 "an in-input prompt/example text.")
QUESTION_TYPES = dict(short_answer=_short_answer, long_answer=_long_answer,
                      choice=_choice)

# for to_csv and View.exportSerialized
FIELDS = 'author modified_by'
PLAIN = 'is_featured content created modified'


class View(base.View):
  """View methods for the Survey model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    # TODO: read/write access needs to match survey
    # TODO: usage requirements

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = [('checkIsSurveyWritable', survey_logic)]
    rights['create'] = ['checkIsUser']
    rights['edit'] = [('checkIsSurveyWritable', survey_logic)]
    rights['delete'] = ['checkIsDeveloper'] # TODO: fix deletion of Surveys
    rights['list'] = ['checkDocumentList']
    rights['pick'] = ['checkDocumentPick']
    rights['take'] = ['checkIsDeveloper'] # TODO(ljvderijk) test proper check

    new_params = {}
    new_params['logic'] = survey_logic
    new_params['rights'] = rights

    new_params['name'] = "Survey"
    new_params['pickable'] = True

    new_params['extra_django_patterns'] = [
         (r'^%(url_name)s/(?P<access_type>take)/%(key_fields)s$',
         'soc.views.models.%(module_name)s.take',
         'Take %(module_name)s'),
         (r'^%(url_name)s/(?P<access_type>json)/%(scope)s$',
         'soc.views.models.%(module_name)s.json',
         'Export %(name)s as JSON'),
        (r'^%(url_name)s/(?P<access_type>results)/%(scope)s$',
         'soc.views.models.%(module_name)s.results',
         'View survey results for %(name)s'),
        (r'^%(url_name)s/(?P<access_type>show)/user/(?P<link_id>)\w+$',
         'soc.views.models.%(module_name)s.results',
         'View survey results for user'),
        ]

    new_params['export_content_type'] = 'text/text'
    new_params['export_extension'] = '.csv'
    new_params['export_function'] = to_csv
    new_params['delete_redirect'] = '/'
    new_params['list_key_order'] = [
        'link_id', 'scope_path', 'name', 'short_name', 'title',
        'content', 'prefix','read_access','write_access']

    new_params['edit_template'] = 'soc/survey/edit.html'
    new_params['create_template'] = 'soc/survey/edit.html'
    new_params['take_template'] = 'soc/survey/take.html'

    # TODO which one of these are leftovers from Document?
    new_params['no_create_raw'] = True
    new_params['no_create_with_scope'] = True
    new_params['no_create_with_key_fields'] = True
    new_params['no_list_raw'] = True
    new_params['sans_link_id_create'] = True
    new_params['sans_link_id_list'] = True

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Survey Link ID',
         },
        ]

    # survey_html: save form content if POST fails, so fields remain in UI
    new_params['create_extra_dynaproperties'] = {
        #'survey_content': forms.fields.CharField(widget=surveys.EditSurvey(),
                                                 #required=False),
        'survey_html': forms.fields.CharField(widget=forms.HiddenInput,
                                              required=False),
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'prefix': forms.fields.CharField(widget=widgets.ReadOnlyInput(),
                                        required=True),
        'clean_content': cleaning.clean_html_content('content'),
        'clean_link_id': cleaning.clean_link_id('link_id'),
        'clean_scope_path': cleaning.clean_scope_path('scope_path'),
        'clean': cleaning.validate_document_acl(self, True),
        }

    new_params['extra_dynaexclude'] = ['author', 'created', 'content',
                                       'home_for', 'modified_by', 'modified',
                                       'take_survey', 'survey_content']

    new_params['edit_extra_dynaproperties'] = {
        'doc_key_name': forms.fields.CharField(widget=forms.HiddenInput),
        'created_by': forms.fields.CharField(widget=widgets.ReadOnlyInput(),
                                             required=False),
        'last_modified_by': forms.fields.CharField(
                                widget=widgets.ReadOnlyInput(), required=False),
        'clean': cleaning.validate_document_acl(self),
        }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def list(self, request, access_type, page_name=None, params=None,
           filter=None, order=None, **kwargs):
    """See base.View.list.
    """

    return super(View, self).list(request, access_type, page_name=page_name,
                                  params=params, filter=kwargs)

  def _public(self, request, entity, context):
    """Add a preview version of the Survey to the page's context.

    Args:
      request: the django request object
      entity: the entity to make public
      context: the context object
    """

    # construct the form to be shown on the page
    # TODO(ljvderijk) Generate SurveyForm without passing along the logic
    survey_form = surveys.SurveyForm(survey_content=entity.survey_content,
                                     survey_logic=self._params['logic'])

    # TOOD(ljvderijk) pose question about the getFields method name and working
    survey_form.getFields()

    context['survey_form'] = survey_form

    # return True to signal that the page may be displayed
    return True

  def _editContext(self, request, context):
    """Performs any required processing on the context for edit pages.

    Args:
      request: the django request object
      context: the context dictionary that will be used

      Adds list of SurveyRecord results as supplement to view.

      See surveys.SurveyResults for details.
    """

    if not getattr(self, '_entity', None):
      return

    results = surveys.SurveyResults()

    context['survey_records'] = results.render(self._entity, self._params,
                                               filter={})

    super(View, self)._editContext(request, context)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().

    Processes POST request items to add new dynamic field names,
    question types, and default prompt values to SurveyContent model.
    """

    user = user_logic.getForCurrentAccount()
    schema = {}
    survey_fields = {}

    if not entity:
      # new Survey
      if 'serialized' in request.POST:
        fields, schema, survey_fields = self.importSerialized(request, fields, user)
      fields['author'] = user
    else:
      fields['author'] = entity.author
      schema = self.loadSurveyContent(schema, survey_fields, entity)

    # remove deleted properties from the model
    self.deleteQuestions(schema, survey_fields, request.POST)

    # add new text questions and re-build choice questions
    self.getRequestQuestions(schema, survey_fields, request.POST)

    # get schema options for choice questions
    self.getSchemaOptions(schema, survey_fields, request.POST)

    survey_content = getattr(entity,'survey_content', None)
    # create or update a SurveyContent for this Survey
    survey_content = survey_logic.createSurvey(survey_fields, schema,
                                                survey_content=survey_content)

    # save survey_content for existent survey or pass for creating a new one
    if entity:
      entity.modified_by = user
      entity.survey_content = survey_content
      db.put(entity)
    else:
      fields['survey_content'] = survey_content

    fields['modified_by'] = user
    super(View, self)._editPost(request, entity, fields)

  def loadSurveyContent(self, schema, survey_fields, entity):
    """Populate the schema dict and get text survey questions.
    """

    if hasattr(entity, 'survey_content'):

      # there is a SurveyContent already
      survey_content = entity.survey_content
      schema = eval(survey_content.schema)

      for question_name in survey_content.dynamic_properties():

        # get the current questions from the SurveyContent
        if question_name not in schema:
          continue

        if schema[question_name]['type'] not in CHOICE_TYPES:
          # Choice questions are always regenerated from request, see
          # self.get_request_questions()
          question = getattr(survey_content, question_name)
          survey_fields[question_name] = question

    return schema

  def deleteQuestions(self, schema, survey_fields, POST):
    """Process the list of questions to delete, from a hidden input.
    """

    deleted = POST.get('__deleted__', '')

    if deleted:
      deleted = deleted.split(',')
      for field in deleted:

        if field in schema:
          del schema[field]

        if field in survey_fields:
          del survey_fields[field]

  def getRequestQuestions(self, schema, survey_fields, POST):
    """Get fields from request.

    We use two field/question naming and processing schemes:
      - Choice questions consist of <input/>s with a common name, being rebuilt
        anew on every edit POST so we can gather ordering, text changes,
        deletions and additions.
      - Text questions only have special survey__* names on creation, afterwards
        they are loaded from the SurveyContent dynamic properties.
    """

    for key, value in POST.items():

      if key.startswith('id_'):
        # Choice question fields, they are always generated from POST contents,
        # as their 'content' is editable and they're reorderable. Also get
        # its field index for handling reordering fields later.
        name, number = key[3:].replace('__field', '').rsplit('_', 1)

        if name not in schema:
          if 'NEW_' + name in POST:
            # new Choice question, set generic type and get its index
            schema[name] = {'type': 'choice'}
            schema[name]['index'] = int(POST['index_for_' + name])

        if name in schema and schema[name]['type'] in CHOICE_TYPES:
          # build an index:content dictionary
          if name in survey_fields:
            if value not in survey_fields[name]:
              survey_fields[name][int(number)] = value
          else:
            survey_fields[name] = {int(number): value}

      elif key.startswith('survey__'): # new Text question
        # this is super ugly but unless data is serialized the regex is needed
        prefix = re.compile('survey__([0-9]{1,3})__')
        prefix_match = re.match(prefix, key)

        index = prefix_match.group(0).replace('survey', '').replace('__','')
        index = int(index)

        field_name = prefix.sub('', key)
        field = 'id_' + key

        for ptype in PROPERTY_TYPES:
          # should only match one
          if ptype + "__" in field_name:
            field_name = field_name.replace(ptype + "__", "")
            schema[field_name] = {}
            schema[field_name]["index"] = index
            schema[field_name]["type"] = ptype

        survey_fields[field_name] = value

  def getSchemaOptions(self, schema, survey_fields, POST):
    """Get question, type, rendering and option order for choice questions.
    """

    RENDER = {'checkboxes': 'multi_checkbox', 'select': 'single_select',
              'radio_buttons': 'quant_radio'}

    RENDER_TYPES = {'select': 'selection',
                    'checkboxes': 'pick_multi',
                    'radio_buttons': 'pick_quant' }

    for key in schema:
      if schema[key]['type'] in CHOICE_TYPES and key in survey_fields:
        render_for = 'render_for_' + key
        if render_for in POST:
          schema[key]['render'] = RENDER[POST[render_for]]
          schema[key]['type'] = RENDER_TYPES[POST[render_for]]

        # handle reordering fields
        ordered = False
        order = 'order_for_' + key
        if order in POST and isinstance(survey_fields[key], dict):
          order = POST[order]

          # 'order_for_name' is jquery serialized from a sortable, so it's in
          # a 'name[]=1&name[]=2&name[]=0' format ('id-li-' is set in our JS)
          order = order.replace('id-li-%s[]=' % key, '')
          order = order.split('&')

          if len(order) == len(survey_fields[key]) and order[0]:
            order = [int(number) for number in order]

            if set(order) == set(survey_fields[key]):
              survey_fields[key] = [survey_fields[key][i] for i in order]
              ordered = True

          if not ordered:
            # we don't have a good ordering to use
            ordered = sorted(survey_fields[key].items())
            survey_fields[key] = [value for index, value in ordered]

      # set 'question' entry (free text label for question) in schema
      question_for = 'NEW_' + key
      if question_for in POST:
        schema[key]["question"] = POST[question_for]

  def createGet(self, request, context, params, seed):
    """Pass the question types for the survey creation template.
    """

    context['question_types'] = QUESTION_TYPES

    # avoid spurious results from showing on creation
    context['new_survey'] = True
    return super(View, self).createGet(request, context, params, seed)

  def editGet(self, request, entity, context, params=None):
    """Process GET requests for the specified entity.

    Builds the SurveyForm that represents the Survey question contents.
    """

    # TODO(ajaksu) Move CHOOSE_A_PROJECT_FIELD and CHOOSE_A_GRADE_FIELD
    # to template.

    CHOOSE_A_PROJECT_FIELD = """<tr class="role-specific">
    <th><label>Choose Project:</label></th>
    <td>
      <select disabled="TRUE" id="id_survey__NA__selection__project"
        name="survey__1__selection__see">
          <option>Survey Taker's Projects For This Program</option></select>
     </td></tr>
     """

    CHOOSE_A_GRADE_FIELD = """<tr class="role-specific">
    <th><label>Assign Grade:</label></th>
    <td>
      <select disabled=TRUE id="id_survey__NA__selection__grade"
       name="survey__1__selection__see">
        <option>Pass/Fail</option>
      </select></td></tr>
    """

    self._entity = entity
    survey_content = entity.survey_content
    user = user_logic.getForCurrentAccount()
    # no project or survey_record needed for survey prototype
    project = None
    survey_record = None


    survey_form = surveys.SurveyForm(survey_content=survey_content,
                                     this_user=user, project=project,
                                     survey_logic=params['logic'],
                                     survey_record=survey_record,
                                     editing=True, read_only=False)
    survey_form.getFields()


    # activate grades flag -- TODO: Can't configure notice on edit page
    if request._get.get('activate'):
      context['notice'] = "Evaluation Grades Have Been Activated"

    local = dict(survey_form=survey_form, question_types=QUESTION_TYPES,
                survey_h=entity.survey_content)
    context.update(local)

    params['edit_form'] = HelperForm(params['edit_form'])
    if entity.survey_end and datetime.datetime.now() > entity.survey_end:
      # are we already passed the survey_end?
      context["passed_survey_end"] = True

    return super(View, self).editGet(request, entity, context, params=params)

  @decorators.merge_params
  @decorators.check_access
  def take(self, request, access_type, page_name=None,
           params=None, **kwargs):
    """View for taking a Survey.

    For Args see base.View().public().
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    template = params['take_template']

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = "%s titled '%s'" % (page_name, entity.title)
    context['entity'] = entity

    if request.POST:
      return self.takePost(request, template, context, params, entity,
                           **kwargs)
    else: #request.GET
      return self.takeGet(request, template, context, params, entity,
                          **kwargs)

  def takeGet(self, request, template, context, params, entity, **kwargs):
    """Handles the GET request for the Survey's take page.

    Args:
        template: the template used for this view
        entity: the student project entity
        rest: see base.View.public()
    """

    # TODO(ljvderijk) implement takeGet

    return http.HttpResponse("Work in Progress")

  def takePost(self, request, template, context, params, entity, **kwargs):
    """Handles the POST request for the Survey's take page.

    Args:
        template: the template used for this view
        entity: the student project entity
        rest: see base.View.public()
    """

    # TODO(ljvderijk) implement takePost

    return httpHttpResponse("Work in Progress")

  def activate(self, request, **kwargs):
    """This is a hack to support the 'Enable grades' button.
    """
    self.activateGrades(request)
    redirect_path = request.path.replace('/activate/', '/edit/') + '?activate=1'
    return http.HttpResponseRedirect(redirect_path)

  def activateGrades(self, request, **kwargs):
    """Updates SurveyRecord's grades for a given Survey.
    """
    survey_key_name = survey_logic.getKeyNameFromPath(request.path)
    survey = Survey.get_by_key_name(survey_key_name)
    survey_logic.activateGrades(survey)
    return

  @decorators.merge_params
  @decorators.check_access
  def viewResults(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """View for SurveyRecord and SurveyRecordGroup.
    """

    results_logic = params['logic'].getRecordLogic()

    user = user_logic.getForCurrentAccount()

    # TODO(ajaksu) use the named parameter link_id from the re
    if request.path == '/survey/show/user/' + user.link_id:
      records = tuple(user.surveys_taken.run())
      context = responses.getUniversalContext(request)
      context['content'] = records[0].survey.survey_content
      responses.useJavaScript(context, params['js_uses_all'])
      context['page_name'] = u'Your survey records.'
    else:
      entity, context = self.getContextEntity(request, page_name,
                                              params, kwargs)

      if context is None:
        # user cannot see this page, return error response
        return entity
      context['content'] = entity.survey_content
      can_write = False
      rights = self._params['rights']
      try:
        rights.checkIsSurveyWritable({'key_name': entity.key().name(),
                                      'prefix': entity.prefix,
                                      'scope_path': entity.scope_path,
                                      'link_id': entity.link_id,},
                                     'key_name')
        can_write = True
      except out_of_band.AccessViolation:
        pass

      filter = self._params.get('filter') or {}

      # if user can edit the survey, show everyone's results
      if can_write:
        filter['survey'] = entity
      else:
        filter.update({'user': user, 'survey': entity})

      limit = self._params.get('limit') or 1000
      offset = self._params.get('offset') or 0
      order = self._params.get('order') or []
      idx = self._params.get('idx') or 0

      records = results_logic.getForFields(filter=filter, limit=limit,
                                        offset=offset, order=order)

    updates = dicts.rename(params, params['list_params'])
    context.update(updates)

    context['results'] = records, records

    template = 'soc/survey/results_page.html'
    return responses.respond(request, template, context=context)

  @decorators.merge_params
  @decorators.check_access
  def exportSerialized(self, request, access_type, page_name=None,
                       params=None, **kwargs):

    sur, context = self.getContextEntity(request, page_name, params, kwargs)

    if context is None:
      # user cannot see this page, return error response
      return sur

    json = sur.toDict()
    json.update(dict((f, str(getattr(sur, f))) for f in PLAIN.split()))
    static = ((f, str(getattr(sur, f).link_id)) for f in FIELDS.split())
    json.update(dict(static))

    dynamic = sur.survey_content.dynamic_properties()
    content = ((prop, getattr(sur.survey_content, prop)) for prop in dynamic)
    json['survey_content'] = dict(content)

    schema =  sur.survey_content.schema
    json['survey_content']['schema'] = eval(sur.survey_content.schema)

    data = simplejson.dumps(json, indent=2)

    return self.json(request, data=json)

  def importSerialized(self, request, fields, user):
    json = request.POST['serialized']
    json = simplejson.loads(json)['data']
    survey_content = json.pop('survey_content')
    schema = survey_content.pop('schema')
    del json['author']
    del json['created']
    del json['modified']
    #del json['is_featured']
    # keywords can't be unicode
    keywords = {}
    for key, val in json.items():
      keywords[str(key)] = val
    if 'is_featured' in keywords:
      keywords['is_featured'] = eval(keywords['is_featured'])
    return keywords, schema, survey_content

  def getContextEntity(self, request, page_name, params, kwargs):
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name
    entity = None

    # TODO(ajaksu) there has to be a better way in this universe to get these
    kwargs['prefix'] = 'program'
    kwargs['link_id'] = request.path.split('/')[-1]
    kwargs['scope_path'] = '/'.join(request.path.split('/')[4:-1])

    entity = survey_logic.getFromKeyFieldsOr404(kwargs)

    if not self._public(request, entity, context):
      error = out_of_band.Error('')
      error = responses.errorResponse(
          error, request, template=params['error_public'], context=context)
      return error, None

    return entity, context

  def getMenusForScope(self, entity, params):
    """List featured surveys if after the survey_start date and before survey_end.
    """

    # only list surveys for registered users
    user = user_logic.getForCurrentAccount()
    if not user:
      return []

    filter = {
        'prefix' : params['url_name'],
        'scope_path': entity.key().id_or_name(),
        'is_featured': True,
        }

    entities = self._logic.getForFields(filter)
    submenus = []
    now = datetime.datetime.now()

    # cache ACL
    survey_rights = {}

    # add a link to all featured documents
    for entity in entities:

      # only list those surveys the user can read
      if entity.read_access not in survey_rights:

        params = dict(prefix=entity.prefix, scope_path=entity.scope_path,
                      link_id=entity.link_id, user=user)

        # TODO(ajaksu) use access.Checker.checkIsSurveyReadable
        checker = access.rights_logic.Checker(entity.prefix)
        roles = checker.getMembership(entity.read_access)
        rights = self._params['rights']
        can_read = access.Checker.hasMembership(rights, roles, params)

        # cache ACL for a given entity.read_access
        survey_rights[entity.read_access] = can_read

        if not can_read:
          pass#continue

      elif not survey_rights[entity.read_access]:
        pass#continue

      # omit if either before survey_start or after survey_end
      if entity.survey_start and entity.survey_start > now:
        pass#continue

      if entity.survey_end and entity.survey_end < now:
        pass#continue

      taken_status = ""
      taken_status = "(new)"
      #TODO only if a document is readable it might be added
      submenu = (redirects.getPublicRedirect(entity, self._params),
      'Survey ' +  taken_status + ': ' + entity.short_name,
      'show')

      submenus.append(submenu)
    return submenus

class HelperForm(object):
  """Thin wrapper for adding values to params['edit_form'].fields.
  """

  def __init__(self, form=None):
    """Store the edit_form.
    """

    self.form = form

  def __call__(self, instance=None):
    """Transparently instantiate and add initial values to the edit_form.
    """

    form = self.form(instance=instance)
    form.fields['created_by'].initial = instance.author.name
    form.fields['last_modified_by'].initial = instance.modified_by.name
    form.fields['doc_key_name'].initial = instance.key().id_or_name()
    return form


def _get_csv_header(sur):
  """CSV header helper, needs support for comment lines in CSV.
  """

  tpl = '# %s: %s\n'

  # add static properties
  fields = ['# Melange Survey export for \n#  %s\n#\n' % sur.title]
  fields += [tpl % (k,v) for k,v in sur.toDict().items()]
  fields += [tpl % (f, str(getattr(sur, f))) for f in PLAIN.split()]
  fields += [tpl % (f, str(getattr(sur, f).link_id)) for f in FIELDS.split()]
  fields.sort()

  # add dynamic properties
  fields += ['#\n#---\n#\n']
  dynamic = sur.survey_content.dynamic_properties()
  dynamic = [(prop, getattr(sur.survey_content, prop)) for prop in dynamic]
  fields += [tpl % (k,v) for k,v in sorted(dynamic)]

  # add schema
  fields += ['#\n#---\n#\n']
  schema =  sur.survey_content.schema
  indent = '},\n#' + ' ' * 9
  fields += [tpl % ('Schema', schema.replace('},', indent)) + '#\n']

  return ''.join(fields).replace('\n', '\r\n')


def _get_records(recs, props):
  """Fetch properties from SurveyRecords for CSV export.
  """

  records = []
  props = props[1:]
  for rec in recs:
    values = tuple(getattr(rec, prop, None) for prop in props)
    leading = (rec.user.link_id,)
    records.append(leading + values)
  return records


def to_csv(survey):
  """CSV exporter.
  """

  # get header and properties
  header = _get_csv_header(survey)
  leading = ['user', 'created', 'modified']
  properties = leading + survey.survey_content.orderedProperties()

  try:
    first = survey.survey_records.run().next()
  except StopIteration:
    # bail out early if survey_records.run() is empty
    return header, survey.link_id

  # generate results list
  recs = survey.survey_records.run()
  recs = _get_records(recs, properties)

  # write results to CSV
  output = StringIO.StringIO()
  writer = csv.writer(output)
  writer.writerow(properties)
  writer.writerows(recs)

  return header + output.getvalue(), survey.link_id


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
edit = decorators.view(view.edit)
export = decorators.view(view.export)
delete = decorators.view(view.delete)
json = decorators.view(view.exportSerialized)
list = decorators.view(view.list)
public = decorators.view(view.public)
pick = decorators.view(view.pick)
results = decorators.view(view.viewResults)
take = decorators.view(view.take)

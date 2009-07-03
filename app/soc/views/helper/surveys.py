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

"""Custom widgets used for Survey form fields, plus the SurveyContent form.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from itertools import chain
import csv
import datetime
import logging
import StringIO

from google.appengine.ext.db import djangoforms

from django import forms
from django.forms import widgets
from django.forms.fields import CharField
from django.template import loader
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe

from soc.logic import dicts
from soc.logic.lists import Lists
from soc.models.survey import COMMENT_PREFIX
from soc.models.survey import SurveyContent


# TODO(ajaksu) add this to template
REQUIRED_COMMENT_TPL = """
  <label for="required_for_{{ name }}">Required</label>
  <select id="required_for_{{ name }}" name="required_for_{{ name }}">
    <option value="True" {% if is_required %} selected='selected' {% endif %}
     >True</option>
    <option value="False" {% if not is_required %} selected='selected'
     {% endif %}>False</option>
  </select><br/>

  <label for="comment_for_{{ name }}">Allow Comments</label>
  <select id="comment_for_{{ name }}" name="comment_for_{{ name }}">
    <option value="True" {% if has_comment %} selected='selected' {% endif %}
     >True</option>
    <option value="False" {% if not has_comment %} selected='selected'
     {% endif %}>False</option>
  </select><br/>
"""


class SurveyForm(djangoforms.ModelForm):
  """Main SurveyContent form.

  This class is used to produce survey forms for several circumstances:
    - Admin creating survey from scratch
    - Admin updating existing survey
    - User taking survey
    - User updating already taken survey

  Using dynamic properties of the survey model (if passed as an arg) the
  survey form is dynamically formed.
  """

  def __init__(self, *args, **kwargs):
    """Store special kwargs as attributes.

      read_only: controls whether the survey taking UI allows data entry.
      editing: controls whether to show the edit or show form.
    """

    self.kwargs = kwargs
    self.survey_content = self.kwargs.pop('survey_content', None)
    self.this_user = self.kwargs.pop('this_user', None)
    self.project = self.kwargs.pop('project', None)
    self.survey_logic = self.kwargs.pop('survey_logic', None)
    self.survey_record = self.kwargs.pop('survey_record', None)

    self.read_only = self.kwargs.pop('read_only', None)
    self.editing = self.kwargs.pop('editing', None)

    self.fields_map = dict(
        long_answer=self.addLongField,
        short_answer=self.addShortField,
        selection=self.addSingleField,
        pick_multi=self.addMultiField,
        pick_quant=self.addQuantField,
        )

    self.kwargs['data'] = {}
    super(SurveyForm, self).__init__(*args, **self.kwargs)

  def getFields(self, post_dict=None):
    """Build the SurveyContent (questions) form fields.

    params:
      post_dict: dict with POST data that will be used for validation

    Populates self.survey_fields, which will be ordered in self.insert_fields.
    Also populates self.data, which will be used in form validation.
    """

    if not self.survey_content:
      return

    post_dict = post_dict or {}
    self.survey_fields = {}
    schema = SurveyContentSchema(self.survey_content.schema)
    has_record = (not self.editing) and (self.survey_record or post_dict)
    extra_attrs = {}

    # figure out whether we want a read-only view
    if not self.editing:
      # only survey taking can be read-only
      read_only = self.read_only

      if not read_only:
        survey_content = self.survey_content
        survey_entity = self.survey_logic.getSurveyForContent(survey_content)
        deadline = survey_entity.survey_end
        read_only =  deadline and (datetime.datetime.now() > deadline)
      else:
        extra_attrs['disabled'] = 'disabled'

    # add unordered fields to self.survey_fields
    for field in self.survey_content.dynamic_properties():

      # a comment made by the user
      comment = ''

      # flag to know where the value came from
      from_content = False

      if has_record and field in post_dict:
        # entered value that is not yet saved
        value = post_dict[field]
        if COMMENT_PREFIX + field in post_dict:
          comment = post_dict[COMMENT_PREFIX + field]
      elif has_record and hasattr(self.survey_record, field):
        # previously entered value
        value = getattr(self.survey_record, field)
        if hasattr(self.survey_record, COMMENT_PREFIX + field):
          comment = getattr(self.survey_record, COMMENT_PREFIX + field)
      else:
        # use prompts set by survey creator
        value = getattr(self.survey_content, field)
        from_content = True

      label = schema.getLabel(field)
      if label is None:
        continue

      # fix validation for pick_multi fields
      is_multi = schema.getType(field) == 'pick_multi'
      if not from_content and schema.getType(field) == 'pick_multi':
        if isinstance(value, basestring):
          value = value.split(',')
      elif from_content and is_multi:
        value = []

      # record field value for validation
      if not from_content:
        self.data[field] = value

      # find correct field type
      addField = self.fields_map[schema.getType(field)]

      # check if question is required, it's never required when editing
      required = not self.editing and schema.getRequired(field)
      kwargs = dict(label=label, req=required)

      # add new field
      addField(field, value, extra_attrs, schema, **kwargs)

      # handle comments if question allows them
      if schema.getHasComment(field):
        self.data[COMMENT_PREFIX + field] = comment
        self.addCommentField(field, comment, extra_attrs, tip='Add a comment.')

    return self.insertFields()

  def insertFields(self):
    """Add ordered fields to self.fields.
    """

    survey_order = self.survey_content.getSurveyOrder()

    # first, insert dynamic survey fields
    for position, property in survey_order.items():
      position = position * 2
      self.fields.insert(position, property, self.survey_fields[property])
      if not self.editing:
        # add comment if field has one and this isn't an edit view
        property = COMMENT_PREFIX + property
        if property in self.survey_fields:
          self.fields.insert(position - 1, property,
                             self.survey_fields[property])
    return self.fields

  def addLongField(self, field, value, attrs, schema, req=True, label='',
                   tip='', comment=''):
    """Add a long answer fields to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      req: required bool
      label: label for field
      tip: tooltip text for field
      comment: initial comment value for field
    """

    # use a widget that allows setting required and comments
    has_comment = schema.getHasComment(field)
    is_required = schema.getRequired(field)
    widget = LongTextarea(is_required, has_comment, attrs=attrs,
                          editing=self.editing)

    if not tip:
      tip = 'Please provide a long answer to this question.'

    question = CharField(help_text=tip, required=req, label=label,
                         widget=widget, initial=value)

    self.survey_fields[field] = question

  def addShortField(self, field, value, attrs, schema, req=False, label='',
                    tip='', comment=''):
    """Add a short answer fields to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      req: required bool
      label: label for field
      tip: tooltip text for field
      comment: initial comment value for field
    """

    attrs['class'] = "text_question"

    # use a widget that allows setting required and comments
    has_comment = schema.getHasComment(field)
    is_required = schema.getRequired(field)
    widget = ShortTextInput(is_required, has_comment, attrs=attrs,
                          editing=self.editing)

    if not tip:
      tip = 'Please provide a short answer to this question.'

    question = CharField(help_text=tip, required=req, label=label,
                         widget=widget, max_length=140, initial=value)

    self.survey_fields[field] = question

  def addSingleField(self, field, value, attrs, schema, req=False, label='',
                     tip='', comment=''):
    """Add a selection field to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      req: required bool
      label: label for field
      tip: tooltip text for field
      comment: initial comment value for field
    """

    widget = schema.getWidget(field, self.editing, attrs)

    these_choices = []
    # add all properties, but select chosen one
    options = getattr(self.survey_content, field)
    has_record = not self.editing and self.survey_record
    if has_record and hasattr(self.survey_record, field):
      these_choices.append((value, value))
      if value in options:
        options.remove(value)

    for option in options:
      these_choices.append((option, option))
    if not tip:
      tip = 'Please select an answer this question.'

    question = PickOneField(help_text=tip, required=req, label=label,
                            choices=tuple(these_choices), widget=widget)

    self.survey_fields[field] = question

  def addMultiField(self, field, value, attrs, schema, req=False, label='',
                    tip='', comment=''):
    """Add a pick_multi field to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      req: required bool
      label: label for field
      tip: tooltip text for field
      comment: initial comment value for field

    """

    widget = schema.getWidget(field, self.editing, attrs)

    # TODO(ajaksu) need to allow checking checkboxes by default
    if self.survey_record and isinstance(value, basestring):
      # pass value as 'initial' so MultipleChoiceField renders checked boxes
      value = value.split(',')

    these_choices = [(v,v) for v in getattr(self.survey_content, field)]
    if not tip:
      tip = 'Please select one or more of these choices.'

    question = PickManyField(help_text=tip, required=req, label=label,
                             choices=tuple(these_choices), widget=widget,
                             initial=value)

    self.survey_fields[field] = question

  def addQuantField(self, field, value, attrs, schema, req=False, label='',
                    tip='', comment=''):
    """Add a pick_quant field to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      req: required bool
      label: label for field
      tip: tooltip text for field
      comment: initial comment value for field

    """

    widget = schema.getWidget(field, self.editing, attrs)

    if self.survey_record:
      value = value
    else:
      value = None

    these_choices = [(v,v) for v in getattr(self.survey_content, field)]
    if not tip:
      tip = 'Please select one of these choices.'

    question = PickQuantField(help_text=tip, required=req, label=label,
                             choices=tuple(these_choices), widget=widget,
                             initial=value)
    self.survey_fields[field] = question

  def addCommentField(self, field, comment, attrs, tip):
    if not self.editing:
      widget = widgets.Textarea(attrs=attrs)
      comment_field = CharField(help_text=tip, required=False, label='Comments',
                          widget=widget, initial=comment)
      self.survey_fields[COMMENT_PREFIX + field] = comment_field

  class Meta(object):
    model = SurveyContent
    exclude = ['schema']


class SurveyContentSchema(object):
  """Abstract question metadata handling.
  """

  def __init__(self, schema):
    self.schema = eval(schema)

  def getType(self, field):
    return self.schema[field]["type"]

  def getRequired(self, field):
    """Check whether survey question is required.
    """

    return self.schema[field]["required"]

  def getHasComment(self, field):
    """Check whether survey question allows adding a comment.
    """

    return self.schema[field]["has_comment"]

  def getRender(self, field):
    return self.schema[field]["render"]

  def getWidget(self, field, editing, attrs):
    """Get survey editing or taking widget for choice questions.
    """

    if editing:
      kind = self.getType(field)
      render = self.getRender(field)
      is_required = self.getRequired(field)
      has_comment = self.getHasComment(field)
      widget = UniversalChoiceEditor(kind, render, is_required, has_comment)
    else:
      widget = WIDGETS[self.schema[field]['render']](attrs=attrs)
    return widget

  def getLabel(self, field):
    """Fetch the free text 'question' or use field name as label.
    """

    if field not in self.schema:
      logging.error('field %s not found in schema %s' %
                    (field, str(self.schema)))
      return
    elif 'question' in self.schema[field]:
      label = self.schema[field].get('question') or field
    else:
      label = field
    return label


class UniversalChoiceEditor(widgets.Widget):
  """Edit interface for choice questions.

  Allows adding and removing options, re-ordering and editing option text.
  """

  def __init__(self, kind, render, is_required, has_comment, attrs=None,
               choices=()):
    """
    params:
      kind: question kind (one of selection, pick_multi or pick_quant)
      render: question widget (single_select, multi_checkbox or quant_radio)
      is_required: bool, controls selection in the required_for field
      has_comments: bool, controls selection in the has_comments field
    """

    self.attrs = attrs or {}

    # Choices can be any iterable, but we may need to render this widget
    # multiple times. Thus, collapse it into a list so it can be consumed
    # more than once.
    self.choices = list(choices)
    self.kind = kind
    self.render_as = render
    self.is_required = is_required
    self.has_comment = has_comment


  def render(self, name, value, attrs=None, choices=()):
    """Render UCE widget.

    Option reordering, editing, addition and deletion are added here.
    """

    if value is None:
      value = ''

    final_attrs = self.build_attrs(attrs, name=name)

    # find out which options should be selected in type and render drop-downs.
    selected = 'selected="selected"'
    context =  dict(
        name=name,
        is_selection=selected * (self.kind == 'selection'),
        is_pick_multi=selected * (self.kind == 'pick_multi'),
        is_pick_quant=selected * (self.kind == 'pick_quant'),
        is_select=selected * (self.render_as == 'single_select'),
        is_checkboxes=selected * (self.render_as == 'multi_checkbox'),
        is_radio_buttons=selected * (self.render_as == 'quant_radio'),
        )

    # set required and has_comment selects
    context.update(dict(
        is_required = self.is_required,
        has_comment = self.has_comment,
        ))

    str_value = forms.util.smart_unicode(value) # normalize to string.
    chained_choices = enumerate(chain(self.choices, choices))
    choices = {}

    for i, (option_value, option_label) in chained_choices:
      option_value = escape(forms.util.smart_unicode(option_value))
      choices[i] = option_value
    context['choices'] = choices

    template = 'soc/survey/universal_choice_editor.html'
    return loader.render_to_string(template, context)


class PickOneField(forms.ChoiceField):
  """Stub for customizing the single choice field.
  """
  #TODO(james): Ensure that more than one option cannot be selected

  def __init__(self, *args, **kwargs):
    super(PickOneField, self).__init__(*args, **kwargs)


class PickManyField(forms.MultipleChoiceField):
  """Stub for customizing the multiple choice field.
  """

  def __init__(self, *args, **kwargs):
    super(PickManyField, self).__init__(*args, **kwargs)


class PickQuantField(forms.MultipleChoiceField):
  """Stub for customizing the multiple choice field.
  """
  #TODO(james): Ensure that more than one quant cannot be selected

  def __init__(self, *args, **kwargs):
    super(PickQuantField, self).__init__(*args, **kwargs)


class LongTextarea(widgets.Textarea):
  """Set whether long question is required or allows comments.
  """

  def __init__(self, is_required, has_comment, attrs=None, editing=False):
    """Initialize widget and store editing mode.

    params:
      is_required: bool, controls selection in the 'required' extra field
      has_comments: bool, controls selection in the 'has_comment' extra field
      editing: bool, controls rendering as plain textarea or with extra fields
    """

    self.editing = editing
    self.is_required = is_required
    self.has_comment = has_comment

    super(LongTextarea, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    """Render plain textarea or widget with extra fields.

    Extra fields are 'required' and 'has_comment'.
    """

    # plain text area
    output = super(LongTextarea, self).render(name, value, attrs)

    if self.editing:
      # add 'required' and 'has_comment' fields
      context = dict(name=name, is_required=self.is_required,
                     has_comment=self.has_comment)
      template = loader.get_template_from_string(REQUIRED_COMMENT_TPL)
      rendered = template.render(context=loader.Context(dict_=context))
      output =  rendered + output

      output = '<fieldset>' + output + '</fieldset>'
    return output


class ShortTextInput(widgets.TextInput):
  """Set whether short answer question is required or allows comments.
  """

  def __init__(self, is_required, has_comment, attrs=None, editing=False):
    """Initialize widget and store editing mode.

    params:
      is_required: bool, controls selection in the 'required' extra field
      has_comments: bool, controls selection in the 'has_comment' extra field
      editing: bool, controls rendering as plain text input or with extra fields
    """

    self.editing = editing
    self.is_required = is_required
    self.has_comment = has_comment

    super(ShortTextInput, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    """Render plain text input or widget with extra fields.

    Extra fields are 'required' and 'has_comment'.
    """

    # plain text area
    output = super(ShortTextInput, self).render(name, value, attrs)

    if self.editing:
      # add 'required' and 'has_comment' fields
      context = dict(name=name, is_required=self.is_required,
                     has_comment=self.has_comment)
      template = loader.get_template_from_string(REQUIRED_COMMENT_TPL)
      rendered = template.render(context=loader.Context(dict_=context))
      output =  rendered + output

      output = '<fieldset>' + output + '</fieldset>'
    return output


class PickOneSelect(forms.Select):
  """Stub for customizing the single choice select widget.
  """

  def __init__(self, *args, **kwargs):
    super(PickOneSelect, self).__init__(*args, **kwargs)


class PickManyCheckbox(forms.CheckboxSelectMultiple):
  """Customized multiple choice checkbox widget.
  """

  def __init__(self, *args, **kwargs):
    super(PickManyCheckbox, self).__init__(*args, **kwargs)

  def render(self, name, value, attrs=None, choices=()):
    """Render checkboxes as list items grouped in a fieldset.

    This is the pick_multi widget for survey taking
    """

    if value is None:
      value = []
    has_id = attrs and attrs.has_key('id')
    final_attrs = self.build_attrs(attrs, name=name)

    # normalize to strings.
    str_values = set([forms.util.smart_unicode(v) for v in value])
    is_checked = lambda value: value in str_values
    smart_unicode = forms.util.smart_unicode

    # set container fieldset and list
    output = [u'<fieldset id="id_%s">\n  <ul class="pick_multi">' % name]

    # add numbered checkboxes wrapped in list items
    chained_choices = enumerate(chain(self.choices, choices))
    for i, (option_value, option_label) in chained_choices:
      option_label = escape(smart_unicode(option_label))

      # If an ID attribute was given, add a numeric index as a suffix,
      # so that the checkboxes don't all have the same ID attribute.
      if has_id:
        final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))

      cb = widgets.CheckboxInput(final_attrs, check_test=is_checked)
      rendered_cb = cb.render(name, option_value)
      cb_label = (rendered_cb, option_label)

      output.append(u'    <li><label>%s %s</label></li>' % cb_label)

    output.append(u'  </ul>\n</fieldset>')
    return u'\n'.join(output)

  def id_for_label(self, id_):
    # see the comment for RadioSelect.id_for_label()
    if id_:
      id_ += '_fieldset'
    return id_
  id_for_label = classmethod(id_for_label)


class PickQuantRadioRenderer(widgets.RadioFieldRenderer):
  """Used by PickQuantRadio to enable customization of radio widgets.
  """

  def __init__(self, *args, **kwargs):
    super(PickQuantRadioRenderer, self).__init__(*args, **kwargs)

  def render(self):
    """Outputs set of radio fields in a div.
    """

    return mark_safe(u'<div class="quant_radio">\n%s\n</div>'
                     % u'\n'.join([u'%s' % force_unicode(w) for w in self]))


class PickQuantRadio(forms.RadioSelect):
  """TODO(James,Ajaksu) Fix Docstring
  """

  renderer = PickQuantRadioRenderer

  def __init__(self, *args, **kwargs):
    super(PickQuantRadio, self).__init__(*args, **kwargs)


# in the future, we'll have more widget types here
WIDGETS = {'multi_checkbox': PickManyCheckbox,
           'single_select': PickOneSelect,
           'quant_radio': PickQuantRadio}


class SurveyResults(widgets.Widget):
  """Render List of Survey Results For Given Survey.
  """

  def render(self, survey, params, filter=filter, limit=1000, offset=0,
             order=[], idx=0, context={}):
    """ renders list of survey results

    params:
      survey: current survey
      params: dict of params for rendering list
      filter: filter for list results
      limit: limit for list results
      offset: offset for list results
      order: order for list results
      idx: index for list results
      context: context dict for template
    """

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()
    filter = {'survey': survey}
    data = record_logic.getForFields(filter=filter, limit=limit, offset=offset,
                              order=order)

    params['name'] = "Survey Results"
    content = {
      'idx': idx,
      'data': data,
      'logic': record_logic,
      'limit': limit,
     }
    updates = dicts.rename(params, params['list_params'])
    content.update(updates)
    contents = [content]

    if len(content) == 1:
      content = content[0]
      key_order = content.get('key_order')

    context['list'] = Lists(contents)

    # TODO(ajaksu) is this the best way to build the results list?
    for list_ in context['list']._contents:
      if len(list_['data']) < 1:
        return "<p>No Survey Results Have Been Submitted</p>"

      list_['row'] = 'soc/survey/list/results_row.html'
      list_['heading'] = 'soc/survey/list/results_heading.html'
      list_['description'] = 'Survey Results:'

    context['properties'] = survey.survey_content.orderedProperties()
    context['entity_type'] = "Survey Results"
    context['entity_type_plural'] = "Results"
    context['no_lists_msg'] = "No Survey Results"

    path = (survey.entity_type().lower(), survey.prefix,
            survey.scope_path, survey.link_id)
    context['grade_action'] = "/%s/grade/%s/%s/%s" % path

    markup = loader.render_to_string('soc/survey/results.html',
                                     dictionary=context).strip('\n')
    return markup


def getSurveyResponseFromPost(survey, post_dict):
  """Returns the data for a SurveyRecord that answer the questions
  posed in the given Survey's schema.

  Args:
      survey: a Survey entity
      post_dict: dictionary with data from the POST request
  """

  # TODO(ljvderijk) deal with the comment fields neatly

  # get the schema for this survey
  schema = SurveyContentSchema(survey.survey_content.schema)
  schema_dict = schema.schema

  # fill a dictionary with the data to be stored in the SurveyRecord
  response_dict = {}

  for name, value in post_dict.items():
    # make sure name is a string
    name = name.encode()

    if name not in schema_dict:
      # property not in survey schema ignore
      continue
    else:
      pick_multi = schema.getType(name) == 'pick_multi'

      if pick_multi and hasattr(post_dict, 'getlist'): # it's a multidict
        # validation asks for a list of values
        value = post_dict.getlist(name)

    response_dict[name] = value

    # handle comments
    if schema.getHasComment(name):
      comment_name = COMMENT_PREFIX + name
      comment = post_dict.get(comment_name)
      if comment:
        response_dict[comment_name] = comment

  return response_dict


def getRoleSpecificFields(survey, user, this_project, survey_form,
                          survey_record):
  """For evaluations, mentors get required Project and Grade fields, and
  students get a required Project field.

  Because we need to get a list of the user's projects, we call the
  logic getProjects method, which doubles as an access check.
  (No projects means that the survey cannot be taken.)

  params:
    survey: the survey being taken
    user: the survey-taking user
    this_project: either an already-selected project, or None
    survey_form: the surveyForm widget for this survey
    survey_record: an existing survey record for a user-project-survey combo,
      or None
  """

  field_count = len(eval(survey.survey_content.schema).items())
  these_projects = survey_logic.getProjects(survey, user)
  if not these_projects:
    return False # no projects found

  project_pairs = []
  #insert a select field with options for each project
  for project in these_projects:
    project_pairs.append((project.key(), project.title))
  if project_pairs:
    project_tuples = tuple(project_pairs)
    # add select field containing list of projects
    projectField =  forms.fields.ChoiceField(
                              choices=project_tuples,
                              required=True,
                              widget=forms.Select())
    projectField.choices.insert(0, (None, "Choose a Project")  )
    # if editing an existing survey
    if not this_project and survey_record:
      this_project = survey_record.project
    if this_project:
      for tup in project_tuples:
        if tup[1] == this_project.title:
          if survey_record: project_name = tup[1] + " (Saved)"
          else: project_name = tup[1]
          projectField.choices.remove(tup)
          projectField.choices.insert(0, (tup[0], project_name)  )
          break
    survey_form.fields.insert(0, 'project', projectField )

  if survey.taking_access == "mentor evaluation":
    # If this is a mentor, add a field
    # determining if student passes or fails.
    # Activate grades handler should determine whether new status
    # is midterm_passed, final_passed, etc.
    grade_choices = (('pass', 'Pass'), ('fail', 'Fail'))
    grade_vals = { 'pass': True, 'fail': False }
    gradeField = forms.fields.ChoiceField(choices=grade_choices,
                                           required=True,
                                           widget=forms.Select())

    gradeField.choices.insert(0, (None, "Choose a Grade")  )
    if survey_record:
      for g in grade_choices:
        if grade_vals[g[0]] == survey_record.grade:
          gradeField.choices.insert(0, (g[0],g[1] + " (Saved)")   )
          gradeField.choices.remove(g)
          break;
      gradeField.show_hidden_initial = True

    survey_form.fields.insert(field_count + 1, 'grade', gradeField)

  return survey_form


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

  Args:
      sur: Survey entity
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


def to_csv(survey_view):
  """CSV exporter.

  Args:
      survey_view: instance of the SurveyView
  """

  def wrapper(survey):
    """Wrapper function.
    """
    survey_logic = survey_view.getParams()['logic']
    record_logic = survey_logic.getRecordLogic()

    # get header and properties
    header = _get_csv_header(survey)
    leading = ['user', 'created', 'modified']
    properties = leading + survey.survey_content.orderedProperties()

    # retrieve the query of the data to export
    fields = {'survey': survey}
    record_query = record_logic.getQueryForFields(fields)

    try:
      first = record_query.run().next()
    except StopIteration:
      # bail out early if survey_records.run() is empty
      return header, survey.link_id

    # generate results list
    recs = record_query.run()
    recs = _get_records(recs, properties)

    # write results to CSV
    output = StringIO.StringIO()
    writer = csv.writer(output)
    writer.writerow(properties)
    writer.writerows(recs)

    return header + output.getvalue(), survey.link_id
  return wrapper

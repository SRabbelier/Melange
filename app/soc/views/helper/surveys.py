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

"""Custom widgets used for Survey form fields, plus the SurveyContent form.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from itertools import chain
import csv
import datetime
import logging
import StringIO

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

from django import forms
from django.forms import widgets
from django.forms.fields import CharField
from django.template import loader
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.encoding import smart_unicode
from django.utils.html import escape

from soc.models.survey import COMMENT_PREFIX
from soc.models.survey import SurveyContent

from soc.views.helper import widgets as custom_widgets


CHOICE_TYPES = set(('selection', 'pick_multi', 'choice', 'pick_quant'))

# TODO(ajaksu) add this to template
REQUIRED_COMMENT_TPL = """
  <label for="required_for_{{ name }}">Required</label>
  <select id="required_for_{{ name }}" name="required_for_{{ name }}">
    <option value="True" {% if is_required %} selected='selected' {% endif %}
     >True</option>
    <option value="False" {% if not is_required %} selected='selected'
     {% endif %}>False</option>
  </select>

  <label for="comment_for_{{ name }}">Allow Comments</label>
  <select id="comment_for_{{ name }}" name="comment_for_{{ name }}">
    <option value="True" {% if has_comment %} selected='selected' {% endif %}
     >True</option>
    <option value="False" {% if not has_comment %} selected='selected'
     {% endif %}>False</option>
  </select>
"""


class SurveyTakeForm(djangoforms.ModelForm):
  """SurveyContent form for recording survey answers.

  This class is used to produce survey forms for survey taking:
    - User taking survey
    - User updating already taken survey

  Using dynamic properties of the survey model (if passed as an arg) the
  survey form is dynamically formed.
  """

  def __init__(self, *args, **kwargs):
    """Store special kwargs as attributes.

    params:
      survey: a Survey entity
      survey_content: a SuveryContent entity (if no Survey is provided).
      survey_logic: instance of SurveyLogic.
      survey_record: optionally a SurveyRecord entity.
      read_only: controls whether the survey taking UI allows data entry.
      data: dictionary mapping fields to data for validation.
    """

    self.kwargs = kwargs

    self.survey = self.kwargs.pop('survey', None)
    if self.survey:
      self.survey_content = self.survey.survey_content
    else:
      self.survey_content = self.kwargs.pop('survey_content', None)
    self.survey_logic = self.kwargs.pop('survey_logic', None)
    self.survey_record = self.kwargs.pop('survey_record', None)
    # TODO: This should be removed since readonly is covered by the RecordForm
    self.read_only = self.kwargs.pop('read_only', None)

    self.fields_map = dict(
        long_answer=self.addLongField,
        short_answer=self.addShortField,
        selection=self.addSingleField,
        pick_multi=self.addMultiField,
        pick_quant=self.addQuantField,
        )

    # get the POST data dict if present
    post_data = self.kwargs.pop('data', None)

    # set cleaner methods for fields, only needed if we have POST data
    if post_data:
      # prepare to render a bound, validating form
      self.has_post = True
      clean_data = self.setCleaners(post_data)
    else:
      self.has_post = False
      clean_data = self.setCleaners()

    # update with fields from subclasses
    if hasattr(self, 'data') and self.data:
      clean_data.update(self.data)
      delattr(self, 'data')

    # pass data, so form is bound
    if post_data:
      self.kwargs['data'] = clean_data

    super(SurveyTakeForm, self).__init__(*args, **self.kwargs)

    self.fields = self.getFields(clean_data)

  def setCleaners(self, post_dict=None):
    """Set cleaner methods for dynamic fields.

    Used for storing textual input as Text instead of StringProperty. If
    passed a dict of field names/values (as the kwarg 'data' to __init__),
    it's possible to set clean_[field_id] methods for validation.

    This method populates the 'data' dict used for generating form fields.

    Args:
      post_dict: dictionary used to populate the fields
    """

    # prefix for method names
    clean = 'clean_'

    # data is passed to super's __init__ as the 'data' kwarg
    data = {}

    # flag whether we can use getlist to retrieve multiple values
    is_post = hasattr(post_dict, 'getlist')

    schema = {}
    if self.survey_content:
      schema = eval(self.survey_content.schema)

    for key, val in schema.items():
      if val['type'] == 'long_answer':

        # store > 500 chars per long answer
        setattr(self, clean + key,
                lambda key=key: db.Text(self.cleaned_data.get(key))
                )

      if val['has_comment']:
        comment = COMMENT_PREFIX + key

        #store > 500 chars per comment field
        setattr(self, clean + comment,
                lambda comment=comment: db.Text(self.cleaned_data.get(comment))
                )

        # put comment in self.data
        if post_dict:
          comment_val = post_dict.get(comment) or None
        else:
          comment_val = getattr(self.survey_record, comment, None)
        data[comment] = comment_val

      # put POST or record value for field in self.data
      is_multi = val['type'] == 'pick_multi'
      if post_dict:
        if is_multi and is_post:
          key_val = post_dict.getlist(key)
        else:
          key_val = post_dict.get(key)
      else:
        key_val = getattr(self.survey_record, key, None)
        if is_multi and isinstance(key_val, basestring):
          # TODO(ajaksu): find out if we still need this safety net
          key_val = key_val.split(',')
        elif not is_multi and isinstance(key_val, list):
          # old pick_multi record for a question that is now single choice
          key_val = key_val[0] if key_val else ''

      data[key] = key_val

    return data

  def getFields(self, post_dict=None):
    """Build the SurveyContent (questions) form fields.

    params:
      post_dict: dict with POST data that will be used for validation

    Populates self.survey_fields, which will be ordered in self.insertFields.
    """

    if not self.survey_content:
      return

    post_dict = post_dict or {}
    self.survey_fields = {}
    schema = SurveyContentSchema(self.survey_content.schema)
    attrs = {}

    # figure out whether we want a read-only view
    read_only = self.read_only

    if not read_only:
      survey_content = self.survey_content
      survey_entity = self.survey_logic.getSurveyForContent(survey_content)
      deadline = survey_entity.survey_end
      read_only = deadline and (datetime.datetime.now() > deadline)

    if read_only:
      attrs['disabled'] = 'disabled'

    # add unordered fields to self.survey_fields
    for field in self.survey_content.dynamic_properties():

      value = post_dict.get(field)

      # skip comments, as they should go below their corresponding questions
      if field.startswith(COMMENT_PREFIX):
        continue

      label = schema.getLabel(field)
      if label is None:
        # we log this error in getLabel
        continue

      # find correct field type
      addField = self.fields_map[schema.getType(field)]

      # check if question is required, it's never required when editing
      required = schema.getRequired(field)

      tip = schema.getTip(field)
      kwargs = dict(label=label, req=required, tip=tip)

      # copy attrs
      extra_attrs = attrs.copy()

      # add new field
      addField(field, value, extra_attrs, schema, **kwargs)

      # handle comments if question allows them
      if schema.getHasComment(field):
        comment = post_dict.get(COMMENT_PREFIX + field)
        self.addCommentField(field, comment, extra_attrs, tip='Add a comment.')

    return self.insertFields()

  def insertFields(self):
    """Add ordered fields to self.fields.
    """
    fields = SortedDict()
    survey_order = self.survey_content.getSurveyOrder()

    # first, insert dynamic survey fields
    for _, property in sorted(survey_order.items()):
      fields.insert(len(fields) + 1, property, self.survey_fields[property])

      # add comment if field has one and this isn't an edit view
      property = COMMENT_PREFIX + property
      if property in self.survey_fields:
        fields.insert(len(fields) + 1, property, self.survey_fields[property])
    return fields

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

    #fix growfield wrapping
    attrs['wrap'] = 'hard'
    # no way not to use cols attr with Django oldforms, use a big number
    attrs['cols'] = 999999
    widget = widgets.Textarea(attrs=attrs)

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

    widget = widgets.TextInput(attrs=attrs)

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

    widget = PickOneSelect(attrs)

    these_choices = []
    # add all properties, but select chosen one
    # TODO(ajaksu): this breaks ordering and blocks merging choice methods
    options = getattr(self.survey_content, field)
    if self.survey_record and hasattr(self.survey_record, field):
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

    widget = PickManyCheckbox(attrs)

    # TODO(ajaksu) need to allow checking checkboxes by default
    if self.survey_record and isinstance(value, basestring):
      # pass value as 'initial' so MultipleChoiceField renders checked boxes
      value = value.split(',')

    these_choices = [(v, v) for v in getattr(self.survey_content, field)]
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

    widget = PickQuantRadio(attrs)

    if self.survey_record:
      value = value
    else:
      value = None

    these_choices = [(v, v) for v in getattr(self.survey_content, field)]
    if not tip:
      tip = 'Please select one of these choices.'

    question = PickQuantField(help_text=tip, required=req, label=label,
                             choices=tuple(these_choices), widget=widget,
                             initial=value)
    self.survey_fields[field] = question

  def addCommentField(self, field, comment, attrs, tip):
    """Add comment field to a question.

    params:
      field: the name of the field to add the comment field to
      comment: the initial value of this field.
      attrs: the attrs for the widget
      tip: tooltip text for this field
    """

    attrs['class'] = 'comment'
    attrs['rows'] = '1'
    widget = widgets.Textarea(attrs=attrs)
    comment_field = CharField(help_text=tip, required=False,
        label='Add a Comment (optional)', widget=widget, initial=comment)
    self.survey_fields[COMMENT_PREFIX + field] = comment_field


  class Meta(object):
    model = SurveyContent
    fields = None
    exclude = ['schema']


class SurveyRecordForm(SurveyTakeForm):
  """SurveyContent form for showing record of survey answers.
  """

  def addLongField(self, field, value, attrs, schema, label='', **kwargs):
    """Add plain text long answer fields to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      label: label for this field
    """

    question = CharField(widget=custom_widgets.PlainTextWidget, initial=value,
                         label=label)
    self.survey_fields[field] = question

  def addShortField(self, field, value, attrs, schema, label='', **kwargs):
    """Add plain text short answer fields to this form.

    params:
      field: the current field
      value: the initial value for this field
      attrs: additional attributes for field
      schema: schema for survey
      label: label for this field
    """

    question = CharField(widget=custom_widgets.PlainTextWidget, initial=value,
                         label=label)
    self.survey_fields[field] = question

  def addCommentField(self, field, comment, attrs, tip):
    """Add plain text comment field to a question.

    params:
      field: the name of the field to add the comment field to
      comment: the initial value of this field.
      attrs: the attrs for the widget
      tip: tooltip text for this field
    """

    widget = custom_widgets.PlainTextWidget
    comment_field = CharField(label='Comment', widget=widget, initial=comment)
    self.survey_fields[COMMENT_PREFIX + field] = comment_field


class SurveyEditForm(djangoforms.ModelForm):
  """SurveyContent form for editing a survey.

  This class is used to produce survey forms for several circumstances:
    - Admin creating survey from scratch
    - Admin updating existing survey

  Using dynamic properties of the survey model (if passed as an arg) the
  survey form is dynamically formed.
  """

  def __init__(self, *args, **kwargs):
    """Store special kwargs as attributes.

    params:
      survey_content: a SurveyContent entity.
      survey_logic: an instance of SurveyLogic.
    """

    self.kwargs = kwargs
    self.survey_content = self.kwargs.pop('survey_content', None)
    self.survey_logic = self.kwargs.pop('survey_logic', None)

    super(SurveyEditForm, self).__init__(*args, **self.kwargs)

  def getFields(self):
    """Build the SurveyContent (questions) form fields.

    params:
      post_dict: dict with POST data that will be used for validation

    Populates self.survey_fields, which will be ordered in self.insert_fields.
    Also populates self.data, which will be used in form validation.
    """

    if not self.survey_content:
      return

    self.survey_fields = {}
    schema = SurveyContentSchema(self.survey_content.schema)
    extra_attrs = {}

    # add unordered fields to self.survey_fields
    for field in self.survey_content.dynamic_properties():

      # use prompts set by survey creator
      value = getattr(self.survey_content, field)
      from_content = True

      label = schema.getLabel(field)
      if label is None:
        continue

      tip = schema.getTip(field)
      kwargs = schema.getEditFieldArgs(field, value, tip, label)

      kwargs['widget'] = schema.getEditWidget(field, extra_attrs, tip)

      # add new field
      self.survey_fields[field] = schema.getEditField(field)(**kwargs)

    # TODO(ajaksu): find a new way to keep fields in order
    return self.insertFields()

  def insertFields(self):
    """Add ordered fields to self.fields.
    """

    survey_order = self.survey_content.getSurveyOrder()

    # insert dynamic survey fields
    for position, property in survey_order.items():
      self.fields.insert(position, property, self.survey_fields[property])

    return self.fields

  class Meta(object):
    model = SurveyContent
    fields = None
    exclude = ['schema']


class SurveyContentSchema(object):
  """Abstract question metadata handling.
  """

  def __init__(self, schema):
    """Set the dictionary that this class encapsulates.

    Args:
      schema: schema as stored in SurveyConent entity
    """

    self.schema = eval(schema)

  def getType(self, field):
    """Fetch question type for field e.g. short_answer, pick_multi, etc.

    Args:
      field: name of the field to get the type for
    """

    return self.schema[field]["type"]

  def getTip(self, field):
    """Fetch question help text, used for tooltips.

    Args:
      field: name of the field to get the tooltip for
    """

    return self.schema[field].get('tip', '')


  def getRequired(self, field):
    """Check whether survey question is required.

    Args:
      field: name of the field to check the required property for
    """

    return self.schema[field]["required"]

  def getHasComment(self, field):
    """Check whether survey question allows adding a comment.

    Args:
      field: name of the field to get the hasComment property for
    """

    return self.schema[field]["has_comment"]

  def getRender(self, field):
    """Get rendering options for choice questions.

    Args:
      field: name of the field to get the rendering option for
    """

    return self.schema[field]["render"]

  def getEditField(self, field):
    """For a given question kind, get the correct edit view field.
    """

    kind = self.getType(field)
    if kind in CHOICE_TYPES:
      Field = PickOneField
    else:
      Field = CharField

    return Field

  def getEditFieldArgs(self, field, value, tip, label):
    """Build edit view field arguments.

    params:
      field: field name
      value: field value (text for text questions, list for choice questions)
      tipe: help text, to be used in a tooltip
      label: the field's question (or identifier if question is missing)
    """

    kind = self.getType(field)

    kwargs = dict(help_text=tip, required=False, label=label)

    if kind in CHOICE_TYPES:
      kwargs['choices'] = tuple([(val, val) for val in value])
    else:
      kwargs['initial'] = tip

    return kwargs

  def getEditWidget(self, field, attrs, tip):
    """Get survey editing widget for questions.
    """

    kind = self.getType(field)
    is_required = self.getRequired(field)
    has_comment = self.getHasComment(field)

    if kind in CHOICE_TYPES:
      widget = UniversalChoiceEditor
      render = self.getRender(field)
      args = kind, render, is_required, has_comment, tip
    else:
      args = is_required, has_comment
      if kind == 'long_answer':
        widget = LongTextarea
      elif kind == 'short_answer':
        widget = ShortTextInput
      attrs = attrs.copy()
      attrs['class'] = kind

    kwargs = dict(attrs=attrs)

    return widget(*args, **kwargs)

  def getLabel(self, field):
    """Fetch the free text 'question' or use field name as label.
    """

    if field not in self.schema:
      logging.error('field %s not found in schema %s' %
                    (field, str(self.schema)))
      return
    else:
      label = self.schema[field].get('question') or field

    return label

  def getAllFieldKeys(self):
    """Returns a list of all field keys present in this SurveyContentSchema.
    """
    return self.schema.keys()


class UniversalChoiceEditor(widgets.Widget):
  """Edit interface for choice questions.

  Allows adding and removing options, re-ordering and editing option text.
  """

  def __init__(self, kind, render, is_required, has_comment, tip,
               attrs=None, choices=()):
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
    self.tooltip_content = tip or ''

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

    str_value = smart_unicode(value) # normalize to string.
    chained_choices = enumerate(chain(self.choices, choices))
    choices = {}

    for i, (option_value, option_label) in chained_choices:
      option_value = escape(smart_unicode(option_value))
      choices[i] = option_value
    context['choices'] = choices

    tooltip_content = escape(smart_unicode(self.tooltip_content))
    context['tooltip_content'] = tooltip_content

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

  def clean(self, value):
    """Validates that the input is a list or tuple. If no fields are marked,
    an empty string is returned istead of an empty list.
    """
    
    value = super(PickManyField, self).clean(value)
    return value if value else ''


class PickQuantField(forms.ChoiceField):
  """Stub for customizing the choice field.
  """

  def __init__(self, *args, **kwargs):
    super(PickQuantField, self).__init__(*args, **kwargs)


class LongTextarea(widgets.Textarea):
  """Set whether long question is required or allows comments.
  """

  def __init__(self, is_required, has_comment, attrs=None):
    """Initialize widget and store editing mode.

    params:
      is_required: bool, controls selection in the 'required' extra field
      has_comments: bool, controls selection in the 'has_comment' extra field
    """

    self.is_required = is_required
    self.has_comment = has_comment

    super(LongTextarea, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    """Render plain textarea or widget with extra fields.

    Extra fields are 'required' and 'has_comment'.
    """

    # plain text area
    output = super(LongTextarea, self).render(name, value, attrs)

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

  def __init__(self, is_required, has_comment, attrs=None):
    """Initialize widget and store editing mode.

    params:
      is_required: bool, controls selection in the 'required' extra field
      has_comments: bool, controls selection in the 'has_comment' extra field
    """

    self.is_required = is_required
    self.has_comment = has_comment

    super(ShortTextInput, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    """Render plain text input or widget with extra fields.

    Extra fields are 'required' and 'has_comment'.
    """

    # plain text area
    output = super(ShortTextInput, self).render(name, value, attrs)

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
    str_values = set([smart_unicode(v) for v in value])
    is_checked = lambda value: value in str_values

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

    from django.utils.html import linebreaks

    return linebreaks(u'<div class="quant_radio">%s</div>'
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


def getCSVHeader(survey_entity):
  """CSV header helper, needs support for comment lines in CSV.

  Args:
      survey_entity: Survey entity
  """

  tpl = '# %s: %s\n'

  # add static properties
  fields = ['# Melange Survey export for \n#  %s\n#\n' % survey_entity.title]
  fields += [tpl % (k, v) for k, v in survey_entity.toDict().items()]
  fields += [tpl % (f, str(getattr(survey_entity, f))) for f in PLAIN.split()]
  fields += [tpl % (f, str(getattr(survey_entity, f).link_id))
             for f in FIELDS.split()]
  fields.sort()

  # add dynamic properties
  fields += ['#\n#---\n#\n']
  dynamic = survey_entity.survey_content.dynamic_properties()
  dynamic = [(prop, getattr(survey_entity.survey_content, prop))
             for prop in dynamic]
  fields += [tpl % (k, v) for k, v in sorted(dynamic)]

  # add schema
  fields += ['#\n#---\n#\n']
  schema =  survey_entity.survey_content.schema
  indent = '},\n#' + ' ' * 9
  fields += [tpl % ('Schema', schema.replace('},', indent)) + '#\n']

  return ''.join(fields).replace('\n', '\r\n')


def getRecords(recs, props):
  """Fetch properties from SurveyRecords for CSV export.
  """

  records = []
  props = props[1:]
  for rec in recs:
    values = tuple(getattr(rec, prop, None) for prop in props)
    leading = (rec.user.link_id,)
    records.append(leading + values)
  return records


def toCSV(survey_view):
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
    header = getCSVHeader(survey)
    leading = ['user', 'created', 'modified']
    properties = leading + survey.survey_content.orderedProperties()

    # retrieve the query of the data to export
    fields = {'survey': survey}
    record_query = record_logic.getQueryForFields(fields)

    try:
      _ = record_query.run().next()
    except StopIteration:
      # bail out early if survey_records.run() is empty
      return header, survey.link_id

    # generate results list
    recs = record_query.run()
    recs = getRecords(recs, properties)

    # write results to CSV
    output = StringIO.StringIO()
    writer = csv.writer(output)
    writer.writerow(properties)
    writer.writerows(recs)

    return header + output.getvalue(), survey.link_id
  return wrapper

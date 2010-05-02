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

"""Statistic (Model) query functions.
"""

__authors__ = [
    '"Daniel Hans" <Daniel.M.Hans@gmail.com>',
  ]


import calendar

from datetime import date
from datetime import datetime
from datetime import timedelta
from django.utils import simplejson
from gviz import gviz_api

from soc.logic.models import base

from soc.modules.gsoc.logic.models import program as program_logic
from soc.modules.gsoc.logic.models import student_proposal as \
    gsoc_proposal_logic
from soc.modules.gsoc.logic.models import student_project as \
    gsoc_project_logic

import soc.models.countries
import soc.models.student as student_model
import soc.modules.statistic.logic.instr_to_obj_mapper
import soc.modules.statistic.models.statistic


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


class ProtocolError(Error):
  """Class which concerns protocol errors.
  """

  pass

class Logic(base.Logic):
  """Logic methods for the statistic model
  """

  ACCESS_TYPES = ['org_admin', 'host']

  BATCH_SIZE = 10

  def __init__(self, model=soc.modules.statistic.models.statistic.Statistic,
               base_model=None, scope_logic=program_logic):
    """Defines the name, key_name and model for this entity.
    """

    self.helper = soc.modules.statistic.logic.instr_to_obj_mapper.Mapper(self)

    super(Logic, self).__init__(model=model, base_model=base_model,
        scope_logic=program_logic)


  def collectDispatcher(self, statistic):
    """Chooses a function for statistic collection depending on the its type.
    """

    instructions = simplejson.loads(statistic.instructions_json)
    type = instructions.get('type')

    if type == 'per_field':
      return self._preparePerField(statistic, instructions)
    elif type == 'overall':
      return self._prepareOverall(statistic, instructions)
    elif type == 'average':
      return self._prepareAverage(statistic, instructions)

  def clearStatistic(self, statistic):
    """Clears all data for a given statistic.
    """

    properties = {
        'working_json': None,
        'final_json': None,
        'choices_json': None,
        'calculated_on': None,
        'next_entity': None
        }

    return self.updateEntityProperties(statistic, properties)

  def _preparePerField(self, statistic, instructions):
    """Prepares all settings needed by 'per field' statistics to be collected.
    """

    params = instructions.get('params', {})
    params['statistic'] = statistic
    params['model'] = instructions.get('model')

    field = instructions.get('field')
    choice_instructions = instructions.get('choice_instructions')
    # choices have to be collected manually; there is no predefined list
    if choice_instructions:

      # all possible choices have not been collected yet
      if statistic.choices_json is None:
        model = choice_instructions.get('model')
        if not model:
          raise ProtocolError()

        filter = choice_instructions.get('filter')
        program_field = None
        if filter == 'one_program_filter':
          program_field = self.helper.getProgramFieldForModel(model)
          if not program_field:
            raise ProtocolError()

        choices_collector, choices_logic = self.helper.getChoicesCollector(
            model)
        choices = choices_collector(statistic, choices_logic,
            filter_field=program_field)

        # still there are choices to be collected; next task is needed
        if not choices:
          return statistic, False

        params['choices_logic'] = choices_logic
      else:
        choices = simplejson.loads(statistic.choices_json)
    else:
      choices = self.helper.getChoices(field)

    filter = self.helper.getFilter(instructions, params)
    checker = self.helper.getChecker(instructions)
    logic = self.helper.getLogicForItem(instructions, 'model')
    selector = self.helper.getSelector(field)
    subsets = self.helper.getSubsets(instructions)
    transformer = self.helper.getTransformer(instructions)

    return self._collectPerField(statistic, logic, choices, selector,
        transformer, filter, subsets, params=params)


  def _prepareOverall(self, statistic, instructions):
    """Prepares all settings needed by 'overall' statistics to be collected.
    """

    items = instructions.get('items', [])
    statistic = self._checkIfAllCalculated(statistic, items)

    for item in items:
      name = item.get('name')
      if not name:
        raise ProtocolError()

      if self._checkIfCompleted(statistic, name):
        continue

      is_last_item = item == items[-1]

      type = item['type']
      if type == 'number':
        model = item.get('model')
        if not model:
          raise ProtocolError()

        program_field = self.helper.getProgramFieldForModel(model)
        logic = self.helper.getLogicForItem(item, 'model')
        fields = item.get('fields', [])
        filter_field = self.helper.getProgramFieldForModel(model)
        result = self._collectNumber(statistic, logic, fields, program_field)

      elif type == "average":
        model = item.get('model')
        if not model:
          raise ProtocolError()

        program_field = self.helper.getProgramFieldForModel(model)
        logic = self.helper.getLogicForItem(item, 'model')
        ref_logic = self.helper.getLogicForItem(item, 'ref_logic')
        ref_field = item['ref_field']
        result = self._collectAverage(statistic, logic, ref_logic, ref_field,
            program_field)

      if result is not None:
        self._updateFinalJsonString(statistic, {name: result}, is_last_item)

      return (statistic, True) if is_last_item else (statistic, False)

  def _collectChoicesList(self, statistic, logic, fields=[], filter_field=None):
    """Collects list of choices for certain statistics.

    Args:
      statistic: statistic entity
      logic: logic for a model to collect choices from
      fields: attribute names to represent a choice
      filter_field: collect choices only based only on the program
        in scope for the statistic entity

    Returns:
      List of choices if the list is completed or None otherwise.
    """

    choices = []
    if statistic.working_json:
      choices = simplejson.loads(statistic.working_json)

    filter = {}
    if filter_field:
      filter = {filter_field: statistic.scope}
      filter_key = statistic.scope.key()

    query = logic.getQueryForFields(filter=filter)

    next_key = None
    if statistic.next_entity:
      next_key = statistic.next_entity.key()
      query.filter('__key__ > ', next_key)

    entities = query.fetch(self.BATCH_SIZE)

    if not entities:
      next_entity = None
      result = choices
      json_to_update = 'choices_json'
    else:
      new_choices = []

      for entity in entities:

        if filter_field:
          if not entity.__getattribute__(filter_field).key() == filter_key:
            continue

        for field in fields:
          entity = entity.__getattribute__(field)

        new_choices.append(entity.key().id_or_name())

      choices += new_choices
      choices = list(set(choices))
      next_entity = entities[-1]
      result = None
      json_to_update = 'working_json'

    properties = {
        'next_entity': next_entity,
        json_to_update: simplejson.dumps(choices)
        }

    self.updateEntityProperties(statistic, properties,
        store=True)

    return result


  def _collectNumber(self, statistic, model, fields, filter_field):
    """Collects one batch of data for "number" statistics.
    """

    choices = self._collectChoicesList(statistic, model, fields, filter_field)
    return len(choices) if choices is not None else None


  def _collectAverage(self, statistic, logic, ref_logic, ref_field,
                      program_field):
    """Collects one batch of data for "average" statistics.
    """

    if program_field:
      filter = {program_field: statistic.scope}
    else:
      filter = {}

    query = logic.getQueryForFields(filter=filter)

    if statistic.next_entity:
      next_key = statistic.next_entity.key()
      query.filter('__key__ >= ', next_key)
      partial_stats = simplejson.loads(statistic.working_json)
    else:
      next_key = None
      partial_stats = {"sum": 0, "entities_num": 0}

    entities = query.fetch(self.BATCH_SIZE + 1)

    if len(entities) == self.BATCH_SIZE + 1:
      next_entity = entities.pop()
    else:
      next_entity = None

    entities_num = int(partial_stats["entities_num"]) + len(entities)
    sum = int(partial_stats["sum"])

    for entity in entities:
      query = ref_logic.getQueryForFields(filter={ref_field: entity})
      sum += len(query.fetch(1000))

    if next_entity:
      properties = {
          "working_json": simplejson.dumps({
              "sum": sum,
              "entities_num": entities_num
              }),
          "next_entity": next_entity
          }
      self.updateEntityProperties(statistic, properties, store=True)
      return None

    return float(sum) / float(entities_num)

  def _collectPerField(self, statistic, logic, choices, selector,
                       transformer=None, filter=None, subsets=None,
                       params=None):
    """Collects one batch of data for "per_field" statistics.

    Args:
      statistic: a statistic entity for which data is collected
      logic: logic for a model which entities should be fetched from
      choices: a list of possible choices for the statistic
      selector: for a processed entity it selects a choice from choices
      transformer: when all data is collected, it may transform the result in
        some custom way
      filter: checks if a processed entity should be taken into account
      subsets: a list of subsets of the model for which data should be
        collected
      params: a dictionary containing additional, statistic specific params

    """

    next_key = None
    if statistic.next_entity:
      next_key = statistic.next_entity.key()

    query = logic.getQueryForFields()

    # if the next_key field is specified, it is not the first batch
    if next_key:
      partial_stats = simplejson.loads(statistic.working_json)
      query = query.filter('__key__ >=', next_key)
    else:
      partial_stats = {}
      for choice in choices:
        partial_stats[choice] = [0 for subset in subsets]

    # next batch of entities is fetched from data store

    entities = query.fetch(self.BATCH_SIZE + 1)

    # batch_size + 1 entities means that it is not the last batch
    if len(entities) == self.BATCH_SIZE + 1:
      next_entity = entities.pop()
    else:
      next_entity = None

    if not params:
      params = {}

    for entity in entities:
      params['entity'] = entity

      # checks if the entity should be collected
      if filter:
        if not filter(entity, params):
          continue

      # selects a choice for the entity
      choice = selector(params)
      if not choice:
        continue

      for i, fun in enumerate(subsets):
        # checks if the entity is in the processed subset
        if callable(fun) and not fun(entity, params):
          continue

        # data is updated for the i-th subset
        if choice in partial_stats:
          partial_stats[choice][i] += 1

    # if next_entity is None, all data is gathered
    if not next_entity:
      data = transformer(partial_stats, params)
    else:
      data = partial_stats

    properties = self._updateStatisticProperties(statistic, data, next_entity)

    # statistic is updated, but stored in the data model iff all data gathered
    completed = next_entity is None
    new_entity = self.updateEntityProperties(statistic, properties,
        store=completed)

    return new_entity, completed

  def _updateStatisticProperties(self, statistic, data, next_entity):
    """Updates properties for a statistic after one batch of data is collected
       for a per field statistic.
    """

    properties = {
        'next_entity': next_entity,
        }

    if not next_entity:
      properties['choices_json'] = None
      properties['working_json'] = None
      properties['final_json'] = simplejson.dumps(data)
      properties['calculated_on'] = datetime.utcnow()
    else:
      properties['working_json'] = simplejson.dumps(data)

    return properties

  def _updateFinalJsonString(self, statistic, data, completed):
    """Updates final_json field with new arguments specified in data when
       a new item is collected for an overall statistic.
    """

    if statistic.final_json:
      items = simplejson.loads(statistic.final_json)
    else:
      items = {}

    items.update(data)

    properties = {
        'choices_json': None,
        'working_json': None,
        'next_entity': None,
        'final_json': simplejson.dumps(items),
        }

    if completed:
      properties['calculated_on'] = datetime.utcnow()

    return self.updateEntityProperties(statistic, properties)

  def _checkIfCompleted(self, statistic, name):
    """Checks if a specified item of an overall statistic is already collected.
    """

    if statistic.final_json:
      items = simplejson.loads(statistic.final_json)
      return name in items
    else:
      return False

  def _checkIfAllCalculated(self, statistic, items):
    """Checks if all items are already collected. If so, final_json
       is removed, so that the statistic may be re-collected.
    """

    if statistic.final_json:
      collected_items = simplejson.loads(statistic.final_json)
      if len(collected_items.keys()) >= len(items):
        properties = {
            'final_json': None,
            }
        statistic = self.updateEntityProperties(statistic, properties,
            store=False)

    return statistic

  def _defaultTransformer(self, working_stats, params):
    """Default transformer used when no transformer is defined for a statistic.
    """

    return working_stats

  def _defaultFilter(self, *args, **kwargs):
    """Default filter which does not check anything.
    """

    return True

  def _enumerateTransformer(self, working_stats, params):
    """Transforms json_string before saving it.

    Args:
      working_stats: a dict containing a collected statistic
      params: a dictionary containing additional, statistic specific params

    Returns:
      a dict containing pairs (a value from working_stats, a number of keys
      from working_stats containing that value)
    """

    filtered_stats = {}

    if len(working_stats.keys()) == 0:
      return filtred_stats

    values = [values_list[0] for values_list in working_stats.values()]

    max_value = max(values) + 1

    for i in range(0, max_value):
      filtered_stats[str(i)] = [0]

    for key in working_stats:
      filtered_key = str(working_stats[key][0])
      filtered_stats[filtered_key][0] += 1

    return filtered_stats

  def _getPrettyNamesTransformer(self, working_stats, params):
    """Transforms json_string before saving it.

    Args:
      working_stats: a dict containing a collected stat
      params: a dictionary containing additional, statistic specific params

    Returns:
      a dict containing the collected stat, but choices are represented
      by thier names instead of their key names
    """

    filtered_stat = {}
    logic = params['choices_logic']
    for choice, result in working_stats.iteritems():
      entity = logic.getFromKeyName(choice)
      filtered_stat[entity.name] = result

    return filtered_stat

  def _removeInsufficientTransformer(self, working_stats, params):
    """Transforms json_string before saving it.

    Args:
      working_stats: a dict containing a collected stat
      params: a dictionary containing additional, statistic specific params

    Returns:
      a dict containing the collected stat, but without choices which
      are not selected at all.
    """

    for choice, subsets in working_stats.items():
      sufficient_values = [value for value in subsets if value > 0]
      if not sufficient_values:
        del working_stats[choice]

    return working_stats

  def _removeOutOfRangeTransformer(self, working_stats, params):
    """Transforms json_string before saving it.

    Args:
      working_stats: a dict containing a collected stat
      params: a dictionary containing additional, statistic specific params

    Returns:
      a dict containing the collected stat, but with choices limited to
      the range <minimal_non_empty_choice, maximal_non_empty_choice>
    """

    choices = [int(choice) for choice, subsets in working_stats.iteritems()
               if [value for value in subsets if value > 0]]

    min_choice = min(choices)
    max_choice = max(choices)

    for choice in working_stats.keys():
      if int(choice) < min_choice or int(choice) > max_choice:
        del working_stats[choice]

    return working_stats

  def _getCountriesTransformer(self, working_stats, params):
    """Transforms json_string before saving it.

    Args:
      working_stats: a dict containing a collected stat
      params: a dictionary containing additional, statistic specific params

    Returns:
      a dict containing the collected stat, but with country names renamed
      according to COUNTRIES_TO_VIS_NAME dictionary
    """

    transformed_stats = {}

    for country, value in working_stats.iteritems():
      key = self.helper.COUNTRIES_TO_VIS_NAME.get(country, country)
      transformed_stats[key] = value

    return transformed_stats

  def _perFieldsChoiceSelector(self, params):
    """Standard choice selector for "per_field" statistics.

    Params usage:
      fields: a list of fields to be checked in order. All fields except the
        last one should be references and the last one may be a string
        property.

    Returns:
      Value of the last field for the entity obtained from the rest of the list
    """

    if 'fields' not in params:
      return None

    fields = params['fields']
    result = params['entity']

    try:
      for field in fields[:-1]:
        result = result.__getattribute__(field)

      # there is a special case if the last field is __key__
      if fields[-1] == '__key__':
        result = result.key().id_or_name()
      else:
        result = result.__getattribute__(fields[-1])

    except Exception, e:
      raise ProtocolError()

    return str(result)

  def _perAgeChoiceSelector(self, params):
    """Choice selector for per age statistics.
    """

    entity = params['entity']

    birth_date = entity.birth_date
    today = params.get('today', date.today())

    days = today - birth_date
    days -= timedelta(days=calendar.leapdays(birth_date.year, today.year))
    if calendar.isleap(today.year) and today.timetuple()[7] > 31 + 29:
      days += timedelta(days=1)
    if calendar.isleap(birth_date.year) and birth_date.timetuple()[7] > 31 + 29:
      days += timedelta(days=1)

    return str(days.days / 365)

  def _perContinentChoiceSelector(self, params):
    """Choice selector for per continent statistics.
    """

    entity = params['entity']
    choices = soc.models.countries.COUNTRIES_TO_CONTINENT

    if 'fields' in params:
      fields = params['fields']

      for field in fields:
        entity = entity.__getattribute__(field)

    return choices[entity.res_country]

  def _oneProgramFilter(self, entity, params):
    """Checks if the entity is defined for the same program as the statistic
    which is being calculated.
    """

    desired_keyname = params.get('desired_keyname')
    if not desired_keyname:
      statistic = params.get('statistic')
      desired_keyname = statistic.scope.key().id_or_name()
      params['desired_keyname'] = desired_keyname

    program_field = params.get('program_field')
    if not program_field:
      program_field = self.helper.getProgramFieldForModel(params.get('model'))
      params['program_field'] = program_field
      if not program_field:
        raise ProtocolError()

    current_keyname = entity.__getattribute__(program_field).key().id_or_name()

    if current_keyname != desired_keyname:
      return False
    else:
      return True

  def _isReferencedChecker(self, entity, params):
    """Checks if an entity is referenced by at least one entity from another
       model.
    """

    params['no_ref'] = False
    return self._referencedChecker(entity, params)

  def _isNotReferencedChecker(self, entity, params):
    """Checks if an entity is not referenced by at least one entity from
       another model.
    """

    params['no_ref'] = True
    return self._referencedChecker(entity, params)

  def _referencedChecker(self, entity, params):
    """Checks if an entity is referenced by at least one entity from another
       model.

    Args:
      entity: an entity that is checked
      params: a dict containing some additional parameters

    Params usage:
      ref_logic: a string containing logic name for the referencing model
      ref_field: a string name of the field is a reference to entity's model
      no_ref: if specified, True is returned iff nothing refers to the entity
    """

    if 'ref_logic' not in params:
      return False

    logic = self.helper.getLogicForItem(params, 'ref_logic')
    filter = {
        params['ref_field']: entity.key()
        }
    ref_entity = logic.getForFields(filter=filter, unique=True)

    result = ref_entity is not None

    no_ref = params.get('no_ref')
    if no_ref:
      result = not result

    return result

  def getDataTableObject(self, statistic, statistic_name):
    """Returns dataTable object for a specified virtual statistic.
    """

    statistic_type = self._getStatisticType(statistic)
    if statistic_type == 'per_field':
      return self.getDataTableObjectForPerField(statistic, statistic_name)
    elif statistic_type == 'overall':
      return self.getDataTableObjectForOverall(statistic)

  def getDataTableObjectForPerField(self, statistic, statistic_name):
    """Returns dataTable object for a specified virtual 'per field' statistic.
    """

    if statistic.chart_json:
      chart_json = simplejson.loads(statistic.chart_json)
      options = chart_json['options']
      data_tables = {}
      for k, v in options.items():
        columns = v['columns'] if len(options) > 1 else [0]
        data_table = self.getDataTableObjectForColumns(statistic, columns)
        if not data_table:
          return None
        data_tables[k] = data_table

      return data_tables[statistic_name]

    return None

  def getDataTableObjectForOverall(self, statistic):
    """Returns dataTable object for overall statistics.
    """

    chart_options = simplejson.loads(statistic.chart_json)
    description = [tuple(item) for item in chart_options['description']]
    final_stat = simplejson.loads(statistic.final_json)
    data = [t for t in final_stat.iteritems()]
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    return data_table

  def getDataTableObjectForColumns(self, statistic, columns=None):
    """Returns data table object for a given statistic.
    """

    if statistic.chart_json:
      chart_json = simplejson.loads(statistic.chart_json)
      description_columns = [column + 1 for column in columns]
      description_columns.insert(0, 0)
      description = [tuple(item)
                     for index, item in enumerate(chart_json['description'])
                     if index in description_columns]
      column_types = [column[1] for column in description]

      data = self._getDataForColumns(statistic, column_types, columns)
      data.sort()
      if data is None:
        return None

      data_table = gviz_api.DataTable(description)
      data_table.LoadData(data)
      return data_table
    else:
      return None

  def getCSV(self, statistic):
    """Returns CSV object for a given statistic.
    """

    if not statistic.final_json:
      return ['The statistic has not been collected']

    statistic_type = self._getStatisticType(statistic)
    if statistic_type == 'per_field':
      return self._getCSVForPerField(statistic)
    elif statistic_type == 'overall':
      return self._getCSVForOverall(statistic)

  def _getCSVForPerField(self, statistic):
    """Returns CSV object for a given statistic 'per field' statistic.
    """

    rows = []

    chart_json = simplejson.loads(statistic.chart_json)
    description = chart_json['description'] 
    header = []
    for item in description:
      header.append(item[-1].encode('utf-8'))
    rows.append(header)

    final_stat = simplejson.loads(statistic.final_json)
    for choice, result in final_stat.iteritems():
      row = []
      row.append(str(choice).encode('utf-8'))
      for item in result:
        row.append(str(item).encode('utf-8'))
      rows.append(row)

    return rows

  def _getCSVForOverall(self, statistic):
    """Returns CSV object for a given statistic 'overall' statistic.
    """

    rows = []

    final_stat = simplejson.loads(statistic.final_json)
    for name, result in final_stat.iteritems():
      rows.append([name, result])

    return rows

  def getVisualizationTypes(self, statistic):
    """Returns a list of visualization options for a given statistic.
    """

    chart_json = simplejson.loads(statistic.chart_json)
    if not chart_json:
      return []

    options = chart_json['options']
    visualizations = {}
    for k, v in options.items():
      visualizations[k] = v['visualizations']

    return visualizations

  def getVisualizationTypesJson(self, statistic):
    """Returns a list of visualization options for a statistic in JSON format.
    """

    return simplejson.dumps(self.getVisualizationTypes(statistic))

  def _getDataForColumns(self, statistic, column_types, columns):
    """Returns data table object for columns types of objects.
    """

    if not self.checkIfStatisticReady(statistic):
      return None

    statistic_data = simplejson.loads(statistic.final_json)
    data = []
    for k, v in statistic_data.items():
      row = []

      if column_types[0] == 'string':
        row.append(str(k))
      elif column_types[0] == 'number':
        row.append(int(k))
      row_data = [item for i, item in enumerate(v) if i in columns]

      for i, column_type in enumerate(column_types[1:]):
        if column_type == 'string':
          row.append(str(row_data[i]))
        elif column_type == 'number':
          row.append(int(row_data[i]))

      data.append(tuple(row))

    return data

  def _getStatisticType(self, statistic):
    """Returns type of a given statistic.
    """

    instructions = simplejson.loads(statistic.instructions_json)
    return instructions['type']

  def checkIfStatisticReady(self, statistic):
    """Checks if a specified statistic is collected.
    """

    return statistic.final_json is not None


logic = Logic()

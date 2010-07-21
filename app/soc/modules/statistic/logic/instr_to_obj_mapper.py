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

"""Helper class for statistic gathering logic.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from soc.logic.models import host as host_logic

from soc.modules.gsoc.logic.models import mentor as gsoc_mentor_logic
from soc.modules.gsoc.logic.models import program as gsoc_program_logic
from soc.modules.gsoc.logic.models import org_admin as gsoc_org_admin_logic
from soc.modules.gsoc.logic.models import organization as \
    gsoc_org_logic
from soc.modules.gsoc.logic.models import student as gsoc_student_logic
from soc.modules.gsoc.logic.models import student_proposal as \
    gsoc_proposal_logic
from soc.modules.gsoc.logic.models import student_project as \
    gsoc_project_logic

import soc.models.countries as countries
import soc.models.student as student_model


class Mapper(object):
  """Helper for how the statistics should be actually collected according to
     instruction field stored in statistic model. It translates string objects
     into actual python ones which can be used for further processing.
  """

  LOGICS_DICT = {
      'host': host_logic,
      'gsoc_mentor': gsoc_mentor_logic,
      'gsoc_organization': gsoc_org_logic,
      'gsoc_org_admin': gsoc_org_admin_logic,
      'gsoc_program': gsoc_program_logic,
      'gsoc_student': gsoc_student_logic,
      'gsoc_student_project': gsoc_project_logic,
      'gsoc_student_proposal': gsoc_proposal_logic
      }

  COUNTRIES_TO_VIS_NAME = {
      "Afghanistan, Islamic State of": "Afghanistan",
      "Congo": "Congo - Brazzaville",
      "Congo, Democratic Republic of the": "Congo - Kinshasa",
      "Russian Federation": "Russia",
      }

  PROGRAM_FIELD_FOR_MODEL = {
      'gsoc_mentor': 'program',
      'gsoc_org_admin': 'program',
      'gsoc_student_project': 'program',
      'gsoc_student_proposal': 'program'
      }

  def __init__(self, logic):
    """Initializes all data structures for Helper class.
    """

    self.checkers_dict = {
      'referenced': logic._referencedChecker
      }

    self.choices_dict = {
        'age': [str(i) for i in range(0, 100)],
        'continent': frozenset(countries.COUNTRIES_TO_CONTINENT.values()),
        'country': countries.COUNTRIES_AND_TERRITORIES,
        'degree': student_model.Student.degree.choices,
        'expected_graduation': [str(i) for i in range(2008, 2031)],
        'gsoc_program': logic._collectChoicesList,
        'gsoc_student': logic._collectChoicesList,
        }

    self.filters_dict = {
        'property_filter': logic._propertyFilter
        }

    self.selectors_dict = {
        'age': logic._perAgeChoiceSelector,
        'continent': logic._perContinentChoiceSelector
        }

    self.subsets_dict = {
        'all': None,
        'referenced': logic._isReferencedChecker,
        'no-referenced': logic._isNotReferencedChecker,
        'with_values': logic._hasValuesCheckerWrapper,
        }

    self.transformers_dict = {
        'enumerate': logic._enumerateTransformer,
        'pretty_names': logic._getPrettyNamesTransformer,
        'remove-insufficient': logic._removeInsufficientTransformer,
        'remove-out-of-range': logic._removeOutOfRangeTransformer,
        'get-vis-names': logic._getCountriesTransformer
        }

    self.default_checker = None
    self.default_choices_selector = logic._collectChoicesList
    self.default_selector = logic._perFieldsChoiceSelector
    self.default_filter = logic._defaultFilter
    self.default_subsets = [self.subsets_dict['all']]
    self.default_transformer = logic._defaultTransformer

  def getLogicForItem(self, item, field):
    """Returns based on item[field] entry.
    """

    logic_name = item[field]
    return self.getLogicForName(logic_name)

  def getLogicForName(self, logic_name):
    """Returns logic for a given name based on LOGICS_DICT dictionary.
    """

    logic_module = self.LOGICS_DICT[logic_name]
    return logic_module.logic

  def getChoicesCollector(self, field):
   """Returns function for choices collections and logic which will be used.
   """

   fun = self.choices_dict.get(field, self.default_choices_selector)
   choices_logic = self.getLogicForName(field)

   return fun, choices_logic

  def getChecker(self, field):
    """Tries to return checker if it is defined for a given field.
    """

    if 'checker' in field:
      return self.checkers_dict.get(field)
    else:
      return self.default_checker

  def getFilter(self, instructions):
    """Returns filter for the collected entities based on instruction. 
    """

    filter = instructions.get('filter')

    if filter:
      return self.filters_dict.get(filter)
    else:
      return self.default_filter

  def getChoices(self, field):
    """Tries to return choices if they are defined for a given field.
    """

    return self.choices_dict.get(field) if field else None

  def getSelector(self, field):
    """Tries to return selector if it is defined for a given field.
    """

    if field in self.selectors_dict:
      return self.selectors_dict.get(field)
    else:
      return self.default_selector

  def getSubsets(self, item):
    """Tries to return subsets if it is defined for a given field.
    """

    if 'subsets' not in item:
      return self.default_subsets
    else:
      subsets = []
      for subset, args in item['subsets'].iteritems():
        if not args:
          subsets.append(self.subsets_dict[subset])
        else:
          subsets.append(self.subsets_dict[subset](args))
      return subsets

  def getTransformer(self, item):
    """Tries to return transformer if it is defined.
    """

    if 'transformer' in item:
      transformer_name = item['transformer']
      return self.transformers_dict.get(transformer_name)
    else:
      return self.default_transformer

  def getProgramFieldForModel(self, model):
    """Tries to return scpecific field name which refers to program for
    a given model name.
    """

    if model in self.PROGRAM_FIELD_FOR_MODEL:
      return self.PROGRAM_FIELD_FOR_MODEL[model]
    else:
      return 'scope'

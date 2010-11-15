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

"""Starts an interactive shell which allows to create statistic entities.

Usage is simple:

In order to seed all available statistics, just type:
>>> seed_all()

In order to seed one statistic:
>>> seed_one(link_id)
where link_id is for the desired statistic

In order to change program in scope:
>>> set_program(key_name)
where key_name represents a new program

In order to terminate the script:
>>> exit()
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


import sys
import interactive
interactive.setup()

from django.utils import simplejson

from soc.logic import dicts

from soc.modules.gci.logic.models.program import logic as program_logic

from soc.modules.statistic.logic.models.statistic import logic as \
    statistic_logic

from soc.modules.statistic.models.statistic import Statistic


SUCCESS_MSG_FMT = 'Statistic %s has been sucessfully added.'
FAILURE_MSG_FMT = 'An error occured while adding %s statistic.'
DOES_NOT_EXISTS_MSG_FMT = 'Statistic %s does not exists.'

VISUALIZATION_SETS = {
    "cumulative_standard": [
        "Table",
        "BarChart",
        "ColumnChart",
        "ImageChartBar",
        ],
    "cumulative_countries": [
        "Table"
        ],
    "single_standard": [
        "Table",
        "BarChart",
        "ColumnChart",
        "ImageChartBar",
        "ImageChartP",
        "ImageChartP3",
        "PieChart",
        "ScatterChart"
        ],
      "single_countries": [
          "Table",
          "GeoMap"
          ]
    }

STATISTIC_PROPERTIES = {
    "mentors_per_continent": (
        "Mentors Per Continent",
        {
        "type": "per_field",
        "field": "continent",
        "model": "gci_mentor",
        "subsets": [("all", {}), ("referenced", {}), ("no-referenced", {})],
        "filter": "property_filter",
        "params": {
            "ref_logic": "gci_task",
            "ref_field": "mentor",
            "program_field": "program",
            "property_conditions": {
                "status": ["active", "inactive"]
                 },
            }
        },
        {
        "description": [("continent", "string", "Continent"),
                        ("all_mentors", "number", "Mentors"),
                        ("pro_mentors", "number", "Mentors with tasks"),
                        ("nop_mentors", "number", "Mentors without tasks")],
        "options": {
            'Mentors Per Continent (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_standard'],
                "columns": [0, 1, 2]
                },
            'Mentors Per Continent (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Mentors Per Continent (with tasks)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Mentors Per Continent (without tasks)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            }
        },
        "org_admin"),
}

STATISTICS_LIST = [k for k in STATISTIC_PROPERTIES]
NAMES_DICT = dict((k, v) for k, (v, _, _, _)
    in STATISTIC_PROPERTIES.iteritems())
INSTRUCTIONS_DICT = dict((k, v) for k, (_, v, _, _)
    in STATISTIC_PROPERTIES.iteritems())
CHARTS_DICT = dict((k, v) for k, (_, _, v, _)
    in STATISTIC_PROPERTIES.iteritems())
ACCESS_DICT = dict((k, v) for k, (_, _, _, v)
    in STATISTIC_PROPERTIES.iteritems())

program_keyname = 'melange/gcirunthrough'


def _getCommonProperties():
  """Returns properties that are common for all statistic entities.
  """

  program = program_logic.getFromKeyName(program_keyname)

  properties = {
      'access_for_other_programs': 'invisible',
      'scope': program,
      'scope_path': program_keyname,
      }

  return properties


def _getSpecificProperties(link_id):
  """Returns properties that are specific to a particular statistic.
  """

  properties = {
      'link_id': link_id,
      'name': NAMES_DICT[link_id],
      'chart_json': simplejson.dumps(CHARTS_DICT[link_id]),
      'instructions_json': simplejson.dumps(INSTRUCTIONS_DICT[link_id]),
      'read_access': ACCESS_DICT[link_id]
      }

  return properties


def _seedStatistic(properties):
  """Saves a new statistic entity, described by properties, in data store.
  """

  entity = statistic_logic.updateOrCreateFromFields(properties, silent=True)

  if entity:
    print SUCCESS_MSG_FMT % properties['link_id']
  else:
    print FALIURE_MSG_FMT % properties['link_id']


def exit():
  """Terminates the script.
  """

  sys.exit(0)


def seedOne(link_id):
  """Seeds a single statistic to the data store.

  Args:
    link_id: link_id of the statistic that should be added.
  """

  if link_id not in STATISTICS_LIST:
    print DOES_NOT_EXISTS_MSG_FMT % link_id
  else:
    properties = _getCommonProperties()
    new_properties = _getSpecificProperties(link_id)
    properties.update(new_properties)
    _seedStatistic(properties)


def seedAll():
  """Seeds all available statistics to the data store.
  """

  properties = _getCommonProperties()

  for statistic in STATISTICS_LIST:

    new_properties = _getSpecificProperties(statistic)
    properties.update(new_properties)
    _seedStatistic(properties)


def setProgram(keyname):
  """Sets program key name.
  """

  program_keyname = keyname


def main(args):

  context = {
      'exit': exit,
      'seed_all': seedAll,
      'seed_one': seedOne,
      'statistics_list': STATISTICS_LIST,
      'set_program': setProgram,
      }

  interactive.remote(args, context)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % (sys.argv[0],)
    sys.exit(1)

  main(sys.argv[1:])

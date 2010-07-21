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

from soc.modules.gsoc.logic.models.program import logic as program_logic

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
    "applications_per_program": (
        "Applications Per Program",
        {
        "params": {"fields": ["program", "__key__"]},
        "type": "per_field",
        "model": "gsoc_student_proposal",
        "choice_instructions":
        {
            "model": "gsoc_program",
        },
        "transformer": "pretty_names",
        },
        {
        "description": [("program", "string", "Program"),
                        ("number", "number", "Number")],
        "options": {
            'Applications Per Program': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "applications_per_student": (
        "Applications Per Student",
        {
        "type": "per_field",
        "model": "gsoc_student_proposal",
        "choice_instructions":
        {
            "program_field": "student",
            "model": "gsoc_student",
            "filter": "property_filter",
            "property_conditions": {
                "status": ['active', 'inactive']
                 },
        },
        "transformer": "enumerate",
        "params": {
            "fields": ["scope", "__key__"],
            "program_field": "program",
            }
        },
        {
        "description": [("app_number", "string", "Number of Applications"),
                        ("student_number", "number", "Number of Students")],
        "options": {
            'Applications Per Student': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "mentors_per_continent": (
        "Mentors Per Continent",
        {
        "type": "per_field",
        "field": "continent",
        "model": "gsoc_mentor",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "filter": "property_filter",
        "params": {
            "ref_logic": "gsoc_student_project",
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
                        ("pro_mentors", "number", "Mentors with projects"),
                        ("nop_mentors", "number",
                         "Mentors without projects")],
        "options": {
            'Mentors Per Continent (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_standard'],
                "columns": [0, 1, 2]
                },
            'Mentors Per Continent (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Mentors Per Continent (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Mentors Per Continent (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            }
        },
        "org_admin"),
    "mentors_per_country": (
        "Mentors Per Country",
        {
        "type": "per_field",
        "field": "country",
        "model": "gsoc_mentor",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "filter": "property_filter",
        "transformer": "get-vis-names",
        "params": {
            "fields": ["res_country"],
            "ref_logic": "gsoc_student_project",
            "ref_field": "mentor",
            "program_field": "program",
            "property_conditions": {
                "status": ["active", "inactive"]
                 },
            }
        },
        {
        "description": [("country", "string", "Country"),
                        ("all_mentors", "number", "Mentors"),
                        ("pro_mentors", "number", "Mentors with projects"),
                        ("nop_mentors", "number",
                         "Mentors without projects")],
        "options": {
            'Mentors Per Country (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_countries'],
                "columns": [0, 1, 2]
                },
            'Mentors Per Country (all)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [0]
                },
            'Mentors Per Country (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [1]
                },
            'Mentors Per Country (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [2]
                }
            }
        },
        "org_admin"),
    "mentors_per_organization": (
        "Mentors Per Organization",
        {
        "type": "per_field",
        "model": "gsoc_mentor",
        "choice_instructions": {
            "program_field": "scope",
            "model": "gsoc_organization",
            "filter": "property_filter",
            "property_conditions": {
                "status": ['new', 'active', 'inactive']
                 },
            },
        "transformer": "pretty_names",
        "filter": "property_filter",
        "params": {
            "fields": ["scope", "__key__"],
            "program_field": "program",
            "property_conditions": {
                "status": ['active', 'inactive']
                 },
            }
        },
        {
        "description": [("org_name", "string", "Organization"),
                        ("student_number", "number", "Number of Mentors")],
        "options": {
            'Mentors Per Organization': {
                "visualizations": ["Table"]
                }
            }
        },
        "host"),
    "organizations_per_program": (
        "Organizations Per Program",
        {
        "type": "per_field",
        "model": "gsoc_organization",
        "choice_instructions": {
            "model": "gsoc_program",
        },
        "transformer": "pretty_names",
        "filter": "property_filter",
        "params": {
            "fields": ["scope", "__key__"],
            "property_conditions": {
                "status": ['new', 'active', 'inactive']
                 },
            }
        },
        {
        "description": [("program", "string", "Program"),
                        ("number", "number", "Number")],
        "options": {
            'Organizations Per Program': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "organization_admins_per_age": (# strange visualizations
        "Organization Admins Per Age",
        {
        "type": "per_field",
        "field": "age",
        "model": "gsoc_org_admin",
        "transformer": "remove-out-of-range",
        "filter": "property_filter",
        "params": {
            "program_field": "program",
            "property_conditions": {
                "status": ['active', 'inactive']
                 },
            }
        },
        {
        "description": [("age", "number", "Age"),
                        ("number", "number", "Number")],
        "options": {
            'Organization Admins Per Age': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "student_projects_per_continent": (
        "Student Projects Per Continent",
        {
        "type": "per_field",
        "field": "continent",
        "model": "gsoc_student_project",
        "filter": "property_filter",
        "params": {
            "fields": ["student"],
            "property_conditions": {
                  "status": ["accepted", "completed", "failed"]
                  },
            "program_field": "program",
            }
        },
        {
        "description": [("continent", "string", "Continent"),
                        ("number", "number", "Number")],
        "options": {
            'Student Projects Per Continent': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "student_projects_per_country": (
        "Student Projects Per Country",
        {
        "type": "per_field",
        "model": "gsoc_student_project",
        "field": "country",
        "transformer": "get-vis-names",
        "filter": "property_filter",
        "params": {
            "fields": ["student", "res_country"],
            "property_conditions": {
                  "status": ["accepted", "completed", "failed"]
                  },
            "program_field": "program",
            }
        },
        {
        "description": [("country", "string", "Country"),
                        ("number", "number", "Number")],
        "options": {
            'Student Projects Per Country': {
                "visualizations": VISUALIZATION_SETS['single_countries']
                }
            }
        },
        "host"),
    "student_projects_per_organization": (
        "Student Projects Per Organization",
        {
        "type": "per_field",
        "filter": "property_filter",
        "model": "gsoc_student_project",
        "transformer": "pretty_names",
        "subsets": {
            'all':{}, 
            'with_values': {'constraints': {'status':['accepted']}}
            },
        "choice_instructions": {
            "program_field": "scope",
            "model": "gsoc_organization",
            "filter": "property_filter",
            "property_conditions": {
                "status": ['new', 'active', 'inactive']
                },
            },
        "params": {
            "fields": ["scope", "__key__"],
             "program_field": "program",
             "property_conditions": {
                  "status": ["accepted", "completed", "failed"]
                  },
             }            
        },
        {
        "description": [("organization", "string", "Organization"),
                        ("accepted_projects", "number", "Accepted projects"),
                        ("passed_projects", "number", "Passed projects")],
        "options": {
            'Student Projects Per Organization (cumulative)': {
                "visualizations": ['Table'],
                "columns": [0, 1]
                },
            'Accepted Student Projects Per Organization': {
                "visualizations": ["Table", "ColumnChart"],
                "columns": [0]
                },
            'Passed Student Projects Per Organization': {
                "visualizations": ["Table", "ColumnChart"],
                "columns": [1]
                },
            }
        },
        "host"),
    "student_proposals_per_continent": (
        "Student Proposals Per Continent",
        {
        "type": "per_field",
        "field": "continent",
        "model": "gsoc_student_proposal",
        "params": {
            "fields": ["scope"],
            "program_field": "program",
            }
        },
        {
        "description": [("continent", "string", "Continent"),
                        ("number", "number", "Number")],
        "options": {
            'Student Proposals Per Continent': {
                "visualizations": VISUALIZATION_SETS['single_standard']
                }
            }
        },
        "host"),
    "student_proposals_per_country": (
        "Student Proposals Per Country",
        {
        "type": "per_field",
        "field": "country",
        "model": "gsoc_student_proposal",
        "transformer": "get-vis-names",
        "params": {
            "fields": ["scope", "res_country"],
            "program_field": "program",
            }
        },
        {
        "description": [("country", "string", "Country"),
                        ("number", "number", "Number")],
        "options": {
            'Student Proposals Per Country': {
                "visualizations": VISUALIZATION_SETS['single_countries']
                }
            }
        },
        "host"),
    "student_proposals_per_organization": (
        "Student Proposals Per Organization",
        {
        "type": "per_field",
        "model": "gsoc_student_proposal",
        "choice_instructions": {
            "program_field": "scope",
            "model": "gsoc_organization",
            "filter": "property_filter",
            "property_conditions": {
                "status": ['new', 'active', 'inactive']
                 },
        },
        "transformer": "pretty_names",
        "params": {
            "fields": ["org", "__key__"],
             "program_field": "program",
             }
        },
        {
        "description": [("organization", "string", "Organization"),
                        ("number", "number", "Number")],
        "options": {
            'Student Proposals Per Organization': {
                "visualizations": ["Table", "ColumnChart"]
                }
            }
        },
        "host"),
    "students_per_age": (
        "Students Per Age",
        {
        "type": "per_field",
        "field": "age",
        "filter": "property_filter",
        "model": "gsoc_student",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "transformer": "remove-out-of-range",
        "params": {
            "ref_logic": "gsoc_student_project",
            "ref_field": "student",
            "program_field": "scope",
            "property_conditions": {
                  "status": ["active", "inactive"]
                  },
            }
        },
        {
        "description": [("age", "string", "Age"),
                        ("all_students", "number", "Students"),
                        ("pro_students", "number",
                         "Students with projects"),
                        ("nop_students", "number",
                         "Students without projects")],
        "options": {
            'Students Per Age (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_standard'],
                "columns": [0, 1, 2]
                },
            'Students Per Age (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Students Per Age (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Students Per Age (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            }
        },
        "host"),
    "students_per_continent": (
        "Students Per Continent",
        {
        "type": "per_field",
        "field": "continent",
        "filter": "property_filter",
        "model": "gsoc_student",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "params": {
            "ref_logic": "gsoc_student_project",
            "ref_field": "student",
            "program_field": "scope",
            "property_conditions": {
                  "status": ["active", "inactive"]
                  },
            }
        },
        {
        "description": [("age", "string", "Continent"),
                        ("all_students", "number", "Students"),
                        ("pro_students", "number",
                         "Students with projects"),
                        ("nop_students", "number",
                         "Students without projects")],
          "options": {
            'Students Per Continent (cumulative)': {
                "visualizations": [
                    "Table",
                    "BarChart",
                    "ColumnChart",
                    "ImageChartBar",
                ],
                "columns": [0, 1, 2]
                },
            'Students Per Continent (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Students Per Continent (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Students Per Continent (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            },
        },
        "host"),
    "students_per_country": (
        "Students Per Country",
        {
        "type": "per_field",
        "field": "country",
        "filter": "property_filter",
        "model": "gsoc_student",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "transformer": "get-vis-names",
        "params": {
            "fields": ["res_country"],
            "ref_logic": "gsoc_student_project",
            "ref_field": "student",
            "program_field": "scope",
            "property_conditions": {
                  "status": ["active", "inactive"]
                  },
            }
        },
        {
        "description": [("country", "string", "Country"),
                        ("all_students", "number", "Students"),
                        ("pro_students", "number",
                         "Students with projects"),
                        ("nop_students", "number",
                         "Students without projects")],
        "options": {
            'Students Per Country (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_countries'],
                "columns": [0, 1, 2]
                },
            'Students Per Country (all)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [0]
                },
            'Students Per Country (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [1]
                },
            'Students Per Country (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_countries'],
                "columns": [2]
                }
            },
        },
        "host"),
    "students_per_degree": (
        "Students Per Degree",
        {
        "type": "per_field",
        "field": "degree",
        "filter": "property_filter",
        "model": "gsoc_student",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "params": {
            "fields": ["degree"],
            "ref_logic": "gsoc_student_project",
            "ref_field": "student",
            "program_field": "scope",
            "property_conditions": {
                  "status": ["active", "inactive"]
                  },
            }
        },
        {
        "description": [("degree", "string", "Degree"),
                        ("all_students", "number", "Students"),
                        ("pro_students", "number",
                         "Students with projects"),
                        ("nop_students", "number",
                         "Students without projects")],
        "options": {
            'Students Per Degree (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_standard'],
                "columns": [0, 1, 2]
                },
            'Students Per Degree (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Students Per Degree (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Students Per Degree (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            }
        },
        "host"),
    "students_per_graduation_year": (
        "Students Per Graduation Year",
        {
        "type": "per_field",
        "field": "expected_graduation",
        "filter": "property_filter",
        "model": "gsoc_student",
        "subsets": {"all":{}, "referenced":{}, "no-referenced":{}},
        "transformer": "remove-out-of-range",
        "params": {
            "fields": ["expected_graduation"],
            "ref_logic": "gsoc_student_project",
            "ref_field": "student",
            "program_field": "scope",
            "property_conditions": {
                  "status": ["active", "inactive"]
                  },
            }
        },
        {
        "description": [("graduation_year", "string", "Graduation Year"),
                        ("all_students", "number", "Students"),
                        ("pro_students", "number",
                         "Students with projects"),
                        ("nop_students", "number",
                         "Students without projects")],
        "options": {
            'Students Per Graduation Year (cumulative)': {
                "visualizations": VISUALIZATION_SETS['cumulative_standard'],
                "columns": [0, 1, 2]
                },
            'Students Per Graduation Year (all)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [0]
                },
            'Students Per Graduation Year (with projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [1]
                },
            'Students Per Graduation Year (without projects)': {
                "visualizations": VISUALIZATION_SETS['single_standard'],
                "columns": [2]
                }
            }
        },
        "host"),
    "gsoc2010_overall": (
        "GSoC2010 Overall",
        {
        "type": "overall",
        "items": (
            {
            "name": "Number of Students",
            "type": "number",
            "model": "gsoc_student",
            "program_field": "scope",
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["active", "inactive"]
                    },
                }
            },
            {
            "name": "Number of Mentors",
            "type": "number",
            "model": "gsoc_mentor",
            "program_field": "program",
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["active", "inactive"]
                    },
                }
            },
            {
            "name": "Number of Student Proposals",
            "type": "number",
            "model": "gsoc_student_proposal",
            "program_field": "program",
            },
            {
            "name": "Number of Student Projects",
            "type": "number",
            "model": "gsoc_student_project",
            "program_field": "program",
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["accepted", "completed", "failed"]
                    },
                }
            },
            {
            "name": "Number of Organization Admins",
            "type": "number",
            "model": "gsoc_org_admin",
            "program_field": "program",
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["active", "inactive"]
                    },
                }
            },
            {
            "name": "Number of Mentors With Projects",
            "type": "number",
            "model": "gsoc_student_project",
            "program_field": "program",
            "fields": ["mentor"],
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["accepted", "completed", "failed"]
                    },
                }
            },
            {
            "name": "Number of Students With Projects",
            "type": "number",
            "model": "gsoc_student_project",
            "program_field": "program",
            "fields": ["student"],
            "filter": "property_filter",
            "params": {
                "property_conditions": {
                    "status": ["accepted", "completed", "failed"]
                    },
                }
            },
            {
            "name": "Number of Students With Proposals",
            "type": "number",
            "model": "gsoc_student_proposal",
            "program_field": "program",
            "fields": ["scope"]
            },
            {
            "name": "Average Number of Projects Per Mentor",
            "type": "average",
            "model": "gsoc_mentor",
            "program_field": "program",
            "ref_logic": "gsoc_student_project",
            "ref_field": "mentor"
            },
            {
            "name": "Average Number of Proposals Per Student",
            "type": "average",
            "model": "gsoc_student",
            "program_field": "scope",
            "ref_logic": "gsoc_student_proposal",
            "ref_field": "scope"
            },
            )
        },
        {
        "description": [("stat_name", "string", "Statistic Name"),
                        ("value", "number", "Value")],
        "options": {
            'Google Summer of Code 2009 (overall)': {
                'visualizations': [
                    'Table'
                    ]
                }
            }
        },
        "host"),
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

program_keyname = 'google/gsoc2010'

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

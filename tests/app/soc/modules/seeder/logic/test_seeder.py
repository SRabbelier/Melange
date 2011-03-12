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
"""Tests Data Seeder seeding logic.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


from soc.modules.seeder.logic.seeder import logic as seeder_logic
from soc.modules.seeder.logic.seeder import ConfigurationValueError
from soc.modules.seeder.logic.seeder import JSONFormatError

import unittest


class SeederLogicTest(unittest.TestCase):
  """Tests data seeder seeding logic.
  """

  def testSeedFromJSON(self):
    """Tests getting model data.
    FIXME: FAILURES
    """
    json = """[ {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "link_id": {
          "provider_name": "RandomWordProvider",
          "parameters": {}
        }
      }
    } ]"""
    seeder_logic.seedFromJSON(json)

    # Verify that 5 models were seeded
    """
    # Actual: 0
    self.assertEquals(Linkable.all().count(), 5)
    """

  def testValidateInvalidDataProvider(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "link_id": {
          "provider_name": "ThisIsNotProvider",
          "parameters": {}
        }
      }
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testValidateMissingDataProviderParameters(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "link_id": {
          "provider_name": "FixedStringProvider",
          "parameters": {}
        }
      }
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testValidateInvalidDataProviderParameters(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "link_id": {
          "provider_name": "FixedStringProvider",
          "parameters": {"kbla": "asdf"}
        }
      }
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testValidateInvalidModelProperty(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "asdf": {
          "provider_name": "RandomWordProvider",
          "parameters": {}
        }
      }
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testValidateInvalidNumber(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "xxx",
      "properties": {}
    }
    self.assertRaises(JSONFormatError,
                      seeder_logic.validateModel, data)

  def testValidateInvalidModel(self):
    data = {
      "name": "soc.models.linkable.Asdf",
      "number": "5",
      "properties": {}
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testValidateMissingRequiredModelProperty(self):
    data = {
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {}
    }
    self.assertRaises(ConfigurationValueError,
                      seeder_logic.validateModel, data)

  def testSeedNewModel(self):
    """ FIXME: ERROR
    """
    json = """[{
      "name": "soc.models.linkable.Linkable",
      "number": "5",
      "properties": {
        "scope": {
          "provider_name": "NewModel",
          "parameters": {
            "name": "soc.models.linkable.Linkable",
            "properties": {
              "link_id": {
                "provider_name": "FixedStringProvider",
                "parameters": {
                  "value": "linkable2"
                }
              }
            }
          }
        },
        "link_id": {
          "provider_name": "FixedStringProvider",
          "parameters": {
            "value": "linkable1"
          }
        }
      }
    }]"""
    seeder_logic.seedFromJSON(json)

    # IndexError: The query returned fewer than 1 results
    """
    linkable1 = Linkable.gql('where link_id = :1', 'linkable1')[0]
    linkable2 = Linkable.gql('where link_id = :1', 'linkable2')[0]

    self.assertEqual(linkable1.scope.link_id, linkable2.link_id)
    """

  def testSeedRelatedModles(self):
    """ FIXME: ERROR
    """
    json = """[{
      "name": "soc.models.linkable.Linkable",
      "number": "1",
      "properties": {
        "link_id": {
          "provider_name": "FixedStringProvider",
          "parameters": {
            "value": "linkable1"
          }
        },
        "links": {
          "provider_name": "RelatedModels",
          "parameters": {
            "name": "soc.models.linkable.Linkable",
            "number": "1",
            "properties": {
              "link_id": {
                "provider_name": "FixedStringProvider",
                "parameters": {
                  "value":"linkable2"
                }
              }
            }
          }
        }
      }
    }]"""
    seeder_logic.seedFromJSON(json)

    # IndexError: The query returned fewer than 1 results
    """
    linkable1 = Linkable.gql('where link_id = :1', 'linkable1')[0]
    linkable2 = Linkable.gql('where link_id = :1', 'linkable2')[0]

    self.assertEqual(linkable2.scope.link_id, linkable1.link_id)
    """

  def testSeedn(self):
    """Tests the seedn method.
    """
    from soc.models.student import Student
    # Test seeding multiple data and generating all properties randomly
    n = 3
    students = seeder_logic.seedn(Student, n)
    self.assertEqual(len(students), n)
    self.assertTrue(all(students))

  def testSeed(self):
    """Tests the seed method.
    """
    from soc.models.sponsor import Sponsor
    from soc.models.user import User
    from soc.modules.gsoc.models.organization import GSoCOrganization
    from soc.modules.seeder.logic.providers.integer \
        import RandomNormalDistributionIntegerProvider
    from soc.modules.seeder.logic.providers.integer \
        import RandomUniformDistributionIntegerProvider
    # Test specifying property values
    properties = {'name': "A User", 'is_developer': False}
    user = seeder_logic.seed(User, properties=properties)
    for key, value in properties.iteritems():
      self.assertEqual(user._entity[key], value)
    # Test specifying reference property values
    properties = {'founder': user}
    sponsor = seeder_logic.seed(Sponsor, properties=properties)
    for key, value in properties.iteritems():
      self.assertEqual(sponsor._entity[key], value.key())
    # Test specifying property providers
    min_slots, max_slots = 0, 20
    mean_slots_desired, std_slots_desired = 10, 5
    min_slots_desired, max_slots_desired = 1, 21
    properties = {
        'slots': RandomUniformDistributionIntegerProvider(min=min_slots,
                                                          max=max_slots),
        'slots_desired': RandomNormalDistributionIntegerProvider(
            mean=mean_slots_desired, stdev=std_slots_desired,
            min=min_slots_desired, max=max_slots_desired),
        }
    gsoc_organization = seeder_logic.seed(GSoCOrganization,
                                          properties=properties)
    self.assertTrue(min_slots<=gsoc_organization.slots<=max_slots)
    self.assertTrue(min_slots_desired<=gsoc_organization.slots_desired
                                                       <=max_slots_desired)

  def testSeedAGSoCProgram(self):
    """Tests seeding a GSoC program using both seedn and seed methods.
    """
    import random
    from soc.modules.gsoc.models.mentor import GSoCMentor
    from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin
    from soc.modules.gsoc.models.organization import GSoCOrganization
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.student import GSoCStudent
    from soc.modules.gsoc.models.student_proposal import StudentProposal
    # Seed 'GSoC2011'
    properties = {'name': 'Google Summer of Code 2011','short_name': 'GSoC2011'}
    gsoc2011 = seeder_logic.seed(GSoCProgram, properties=properties)
    # Seed num_gsoc_orgs GSoC orgs
    num_gsoc_orgs = 10
    properties = {'scope': gsoc2011}
    gsoc_orgs = seeder_logic.seedn(GSoCOrganization, num_gsoc_orgs, properties)
    self.assertEqual(len(gsoc_orgs), num_gsoc_orgs)
    self.assertTrue(all(gsoc_orgs))
    # Seed IntegerUniformDistribution(min_num_gsoc_org_admins,
    # max_num_gsoc_org_admins) admins and IntegerUniformDistribution(
    # min_num_gsoc_org_mentors, max_num_gsoc_org_mentors) mentors for GSoC orgs
    min_num_gsoc_org_admins = 1
    max_num_gsoc_org_admins = 5
    min_num_gsoc_org_mentors = 0
    max_num_gsoc_org_mentors = 10
    for gsoc_org in gsoc_orgs:
      properties = {'scope': gsoc_org, 'program': gsoc2011}
      num_gsoc_org_admins = random.randint(min_num_gsoc_org_admins,
                                           max_num_gsoc_org_admins)
      gsoc_org_admins = seeder_logic.seedn(GSoCOrgAdmin,
                                           num_gsoc_org_admins, properties)
      self.assertEqual(len(gsoc_org_admins), num_gsoc_org_admins)
      self.assertTrue(all(gsoc_org_admins))
      num_gsoc_org_mentors = random.randint(min_num_gsoc_org_mentors,
                                            max_num_gsoc_org_mentors)
      gsoc_org_mentors = seeder_logic.seedn(GSoCMentor,
                                            num_gsoc_org_mentors, properties)
      self.assertEqual(len(gsoc_org_mentors), num_gsoc_org_mentors)
      self.assertTrue(all(gsoc_org_mentors))
    # Seed num_gsoc_students GSoC students
    num_gsoc_students = 20
    properties = {'scope': gsoc2011}
    gsoc_students = seeder_logic.seedn(GSoCStudent,
                                       num_gsoc_students, properties)
    self.assertEqual(len(gsoc_students), num_gsoc_students)
    self.assertTrue(all(gsoc_students))
    # Seed IntegerUniformDistribution(min_num_gsoc_student_proposals,
    # max_num_gsoc_student_proposals) student proposals for each student,
    # org is chosen randomly from gsoc_orgs
    min_num_gsoc_student_proposals = 0
    max_num_gsoc_student_proposals = 2
    for gsoc_student in gsoc_students:
      properties = {'scope': gsoc_student,
                    'org':random.choice(gsoc_orgs),
                    'program': gsoc2011,
                    'mentor': None}
      num_gsoc_student_proposals = random.randint(
          min_num_gsoc_student_proposals, max_num_gsoc_student_proposals)
      gsoc_student_proposals = seeder_logic.seedn(
          StudentProposal, num_gsoc_student_proposals, properties)
      self.assertEqual(len(gsoc_student_proposals), num_gsoc_student_proposals)
      self.assertTrue(all(gsoc_student_proposals))

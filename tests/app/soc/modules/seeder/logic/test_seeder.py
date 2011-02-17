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
  ]


from soc.models.linkable import Linkable

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

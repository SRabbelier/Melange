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
"""Module containing string data provider tests.
"""


from soc.modules.seeder.logic.providers.date import FixedDateProvider
from soc.modules.seeder.logic.providers.date import RandomNormalDistributionDateProvider
from soc.modules.seeder.logic.providers.date import RandomUniformDistributionDateProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError
import datetime
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedDateProviderTest(unittest.TestCase):
  """Test class for FixedDateProvider.
  """

  def setUp(self):
    self.provider = FixedDateProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedDateProvider.getValue()
    """
    year = '1990'
    month = '11'
    day = '20'
    self.provider.param_values = {'year': year,
                                  'month': month,
                                  'day': day}
    expected = datetime.date(int(year), int(month), int(day))
    self.assertEquals(self.provider.getValue(), expected)

  def testGetCurrentTime(self):
    """Tests getting the current time.
    """
    value = self.provider.getValue()
    today = datetime.datetime.today()
    self.assertEquals(value.year, today.year)
    self.assertEquals(value.month, today.month)
    self.assertEquals(value.day, today.day)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with invalid year, month and day parameters.
    """
    year = 'asdf'
    month = '13'
    day = '37'

    self.provider.param_values = {'year': year}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'month': month}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'day': day}
    self.assertRaises(ParameterValueError, self.provider.getValue)


class RandomUniformDistributionDateProviderTest(unittest.TestCase):
  """Test class for RandomUniformDistributionDateProvider.
  """

  def setUp(self):
    self.provider = RandomUniformDistributionDateProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests RandomUniformDistributionDateProvider.getValue()
    """
    min_year = '2000'
    min_month = '5'
    min_day = '10'
    max_year = '2012'
    max_month = '12'
    max_day = '24'

    self.provider.param_values = {'min_year': min_year,
                                  'min_month': min_month,
                                  'min_day': min_day,
                                  'max_year': max_year,
                                  'max_month': max_month,
                                  'max_day': max_day}
    value = self.provider.getValue()
    min_date = datetime.date(int(min_year), int(min_month), int(min_day))
    max_date = datetime.date(int(max_year), int(max_month), int(max_day))
    self.assertTrue(min_date <= value <= max_date)

  def testGetValueWithInvalidParameters(self):
    """Tests RandomUniformDistributionDateProvider.getValue() with invalid
    parameters.
    """
    self.provider.param_values = {'min_year': 'asdf'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_year': '-1'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_year': '2000', 'max_year': '1990'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_month': '13'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_day': '32'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_month': '2', 'min_day': '31'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'min_month': '1', 'min_day': '31'}
    self.provider.getValue()


class RandomNormalDistributionDateProviderTest(unittest.TestCase):
  """Test class for RandomNormalDistributionDateProvider.
  """

  def setUp(self):
    self.provider = RandomNormalDistributionDateProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests RandomNormalDistributionDateProvider.getValue()
    """
    # Get a default value
    _ = self.provider.getValue()

    mean_year = '2000'
    mean_month = '6'
    mean_day = '15'
    stdev = '30'

    self.provider.param_values = {'mean_year': mean_year,
                                  'mean_month': mean_month,
                                  'mean_day': mean_day,
                                  'stdev': stdev}

    _ = self.provider.getValue()

  def testGetValueWithInvalidParameters(self):
    """Tests RandomNormalDistributionDateProvider.getValue() with invalid
    parameters.
    """
    self.provider.param_values = {'mean_year': 'asdf'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'mean_month': '13'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'mean_day': '32'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'mean_month': '1', 'mean_day': '31'}
    self.provider.getValue()

    self.provider.param_values = {'mean_month': '4', 'mean_day': '31'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'stdev': 'asdf'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'stdev': '-2'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

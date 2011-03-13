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
"""Module containing data providers for DateProperty.
"""


from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import DataProviderParameter
from soc.modules.seeder.logic.providers.provider import ParameterValueError
import datetime
import random
import time


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]

# pylint: disable=W0223
class DateProvider(BaseDataProvider):
  """Base class for all data providers that return a date.
  """

  pass


class FixedDateProvider(DateProvider):
  """Data provider that returns a fixed string.
  """

  @classmethod
  def getParametersList(cls):
    parameters = super(FixedDateProvider, cls).getParametersList()[:]
    parameters += [
      DataProviderParameter('year',
                            'Year',
                            'Defaults to the current year',
                            False),
      DataProviderParameter('month',
                            'Month',
                            'Defaults to the current month',
                            False),
      DataProviderParameter('day',
                            'Day',
                            'Defaults to the current day',
                            False)]
    return parameters

  def checkParameters(self):
    super(FixedDateProvider, self).checkParameters()
    date = datetime.datetime.today()

    year = self.param_values.get('year', None)
    month = self.param_values.get('month', None)
    day = self.param_values.get('day', None)

    try:
      if year:
        year = int(year)
      else:
        year = date.year
    except (TypeError, ValueError):
      raise ParameterValueError('Invalid value %s for year' % year)

    try:
      if month:
        month = int(month)
      else:
        month = date.month
    except (TypeError, ValueError):
      raise ParameterValueError('Invalid value %s for month' % month)

    try:
      if day:
        day = int(day)
      else:
        day = date.day
    except (TypeError, ValueError):
      raise ParameterValueError('Invalid value %s for day' % day)

    try:
      date = datetime.datetime(year, month, day)
    except ValueError:
      raise ParameterValueError('Invalid year, month or day')

  def getValue(self):
    self.checkParameters()
    date = datetime.datetime.today()

    year = self.param_values.get('year', None)
    month = self.param_values.get('month', None)
    day = self.param_values.get('day', None)

    if year:
      year = int(year)
    else:
      year = date.year

    if month:
      month = int(month)
    else:
      month = date.month

    if day:
      day = int(day)
    else:
      day = date.day

    date = datetime.date(year, month, day)

    return date


class RandomUniformDistributionDateProvider(DateProvider):
  """Returns a date sampled from an uniform distribution.
  """

  DEFAULT_MIN_YEAR = datetime.date.today().year
  DEFAULT_MAX_YEAR = datetime.date.today().year
  DEFAULT_MIN_MONTH = datetime.date.today().month
  DEFAULT_MAX_MONTH = datetime.date.today().month
  DEFAULT_MIN_DAY = datetime.date.today().day
  DEFAULT_MAX_DAY = datetime.date.today().day

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomUniformDistributionDateProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('min_year',
                            'Minimum year',
                            'Defaults to the current year',
                            False),
      DataProviderParameter('max_year',
                            'Maximum year',
                            'Defaults to the current year',
                            False),
      DataProviderParameter('min_month',
                            'Minimum month',
                            'Defaults to the current month',
                            False),
      DataProviderParameter('max_month',
                            'Maximum month',
                            'Defaults to the current month',
                            False),
      DataProviderParameter('min_day',
                            'Minimum day',
                            'Defaults to the current day',
                            False),
      DataProviderParameter('max_day',
                            'Maximum day',
                            'Defaults to the current day',
                            False)]
    return parameters

  def getParams(self):
    """Returns minimum and maximum year, month and date, either from
    param_values or a default value.
    """
    try:
      min_year = self.param_values.get('min_year', self.DEFAULT_MIN_YEAR)
      min_year = int(min_year)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for min_year is invalid!' %
                                min_year)

    try:
      max_year = self.param_values.get('max_year', self.DEFAULT_MAX_YEAR)
      max_year = int(max_year)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for max_year is invalid!' %
                                max_year)

    try:
      min_month = self.param_values.get('min_month', self.DEFAULT_MIN_MONTH)
      min_month = int(min_month)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for min_month is invalid!' %
                                min_month)

    try:
      max_month = self.param_values.get('max_month', self.DEFAULT_MAX_MONTH)
      max_month = int(max_month)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for max_month is invalid!' %
                                max_month)

    try:
      min_day = self.param_values.get('min_day', self.DEFAULT_MIN_DAY)
      min_day = int(min_day)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for min_day is invalid!' %
                                min_day)

    try:
      max_day = self.param_values.get('max_day', self.DEFAULT_MAX_DAY)
      max_day = int(max_day)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for max_day is invalid!' %
                                max_day)

    return min_year, max_year, min_month, max_month, min_day, max_day

  def checkParameters(self):
    super(RandomUniformDistributionDateProvider, self).checkParameters()


    min_year, max_year, min_month, max_month, min_day, max_day = (
        self.getParams())


    try:
      min_date = datetime.datetime(min_year, min_month, min_day)
      max_date = datetime.datetime(max_year, max_month, max_day)
    except ValueError, inst:
      raise ParameterValueError(inst.args[0])

    if max_date < min_date:
      raise ParameterValueError('Minimum date must be less than maximum date')

  def getValue(self):
    self.checkParameters()

    min_year, max_year, min_month, max_month, min_day, max_day = (
        self.getParams())

    min_date = datetime.datetime(min_year, min_month, min_day)
    max_date = datetime.datetime(max_year, max_month, max_day)

    # Generate integer timestamps for min_date and max_date
    min_ts = time.mktime(min_date.timetuple())
    max_ts = time.mktime(max_date.timetuple())

    # Generate a random timestamp between min and max and convert back to
    # datetime
    ts = random.randint(min_ts, max_ts)

    return datetime.date.fromtimestamp(ts)




class RandomNormalDistributionDateProvider(DateProvider):
  """Returns a date sampled from an normal distribution.
  """

  DEFAULT_MEAN_YEAR = datetime.date.today().year
  DEFAULT_MEAN_MONTH = datetime.date.today().month
  DEFAULT_MEAN_DAY = datetime.date.today().day
  DEFAULT_STDEV = str(6*30) # Aproximately 6 months

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomNormalDistributionDateProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('mean_year',
                            'Mean year',
                            'Defaults to the current year',
                            False),
      DataProviderParameter('mean_month',
                            'Mean month',
                            'Defaults to the current month',
                            False),
      DataProviderParameter('mean_day',
                            'Mean day',
                            'Defaults to the current day',
                            False),
      DataProviderParameter('stdev',
                            'Standard deviation',
                            'Standard deviation expressed in days. Defaults '
                            'to approximately 6 monhts',
                            False)]
    return parameters

  def getParams(self):
    """Returns the mean year, month and date from param_values or a default
    value.
    """
    try:
      mean_year = self.param_values.get('mean_year', self.DEFAULT_MEAN_YEAR)
      mean_year = int(mean_year)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for mean_year is invalid!' %
                                mean_year)

    try:
      mean_month = self.param_values.get('mean_month', self.DEFAULT_MEAN_MONTH)
      mean_month = int(mean_month)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for mean_month is invalid!' %
                                mean_month)

    try:
      mean_day = self.param_values.get('mean_day', self.DEFAULT_MEAN_DAY)
      mean_day = int(mean_day)
    except (TypeError, ValueError):
      raise ParameterValueError('Value "%s" for mean_day is invalid!' %
                                mean_day)

    return mean_year, mean_month, mean_day

  def getStdev(self):
    """Returns the standard deviation for the distribution, expressed in
    seconds (for use with a timestamp).
    """
    stdev = self.param_values.get('stdev', self.DEFAULT_STDEV)
    try:
      stdev = int(stdev)
      if stdev < 0:
        raise ValueError
    except (TypeError, ValueError):
      raise ParameterValueError('Invalid value for standard deviation')

    # 24 hors / day, 60 minutes / hour, 60 seconds / minutes
    return stdev * 24 * 60 * 60

  def checkParameters(self):
    super(RandomNormalDistributionDateProvider, self).checkParameters()

    mean_year, mean_month, mean_day = self.getParams()

    try:
      datetime.datetime(mean_year, mean_month, mean_day)
    except ValueError, inst:
      raise ParameterValueError(inst.args[0])

    self.getStdev()

  def getValue(self):
    self.checkParameters()

    mean_year, mean_month, mean_day = self.getParams()

    mean_date = datetime.datetime(mean_year, mean_month, mean_day)

    mean_ts = time.mktime(mean_date.timetuple())

    stdev = self.getStdev()

    ts = int(random.gauss(mean_ts, stdev))

    date = datetime.date.fromtimestamp(ts)

    return date

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
"""Module containing basic data provider classes.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]

class Error(Exception):
  """Error class for the data provider module.
  """

  pass


class MissingParameterError(Error):
  """Error raised when a required parameter is missing.
  """

  pass


class ParameterValueError(Error):
  """Error raised when a parameter is not of the expected type.
  """

  pass


# pylint: disable=R0903
class DataProviderParameter(object):
  """Holds information about a data provider parameters
  """

  def __init__(self, name, verbose_name, description, required=False):
    self.name = name
    self.verbose_name = verbose_name
    self.description = description
    self.required = required


# pylint: disable=R0922
class BaseDataProvider(object):
  """Base class for all data providers.
  """

  def __init__(self, **param_values):
    """Constructor for the base data provider.

    Args:
      param_values: a dictionary containing data provider parameter values
    """
    self.param_values = param_values

  def getValue(self):
    """Returns a value from the data provider.
    """
    raise NotImplementedError

  @classmethod
  def getParametersList(cls):
    """Returns a list of accepted parameters.
    """
    return []

  @classmethod
  def hasParameter(cls, param_name):
    """Checks whether this data provider has a parameter named param_name.
    """
    return param_name in (param.name for param in cls.getParametersList())

  def checkParameters(self):
    """Checks that all required parameters are supplied.
    """

    for param in self.getParametersList():
      if param.required and param.name not in self.param_values:
        raise MissingParameterError('Parameter "%s" is missing.' % param.name)


class FixedValueProvider(BaseDataProvider):
  """Data provider interface for providing a fixed value.
  """

  @classmethod
  def getParametersList(cls):
    params = super(FixedValueProvider, cls).getParametersList()[:]
    params += [
      DataProviderParameter("value",
                            "Value",
                            "The fixed value to return",
                            True)]
    return params

  def getValue(self):
    self.checkParameters()
    return self.param_values["value"]

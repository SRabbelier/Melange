# Copyright 2010 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Defines a Mapper API input reader for the data seeder.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from django.utils import simplejson

from google.appengine.ext.mapreduce.input_readers import InputReader, BadReaderParamsError

from soc.modules.seeder.models.configuration_sheet import DataSeederConfigurationSheet

from google.appengine.ext.db import Key


class JSONInputReader(InputReader):
  """Input reader for the Mapper API that parses a JSON data seeder
  configuration sheet.
  """

  # Mapreduce parameters.
  CONFIGURATION_SHEET_KEY_PARAM = "configuration_sheet_key"

  # Serialization parameters
  CURRENT_POSITION_PARAM = "initial_position"
  END_POSITION_PARAM = "end_position"

  def __init__(self, configuration_sheet_key, current_position, end_position):
    super(JSONInputReader, self).__init__()
    self.configuration_sheet_key = configuration_sheet_key
    self.current_position = current_position
    self.end_position = end_position

  def next(self):
    """Returns the next input from this input reader as a model data seeder
     configuration sheet.

    Returns:
      The next input from this input reader.
    """
    if self.current_position < self.end_position:
      self.current_position += 1
      return self.configuration_sheet_key
    else:
      raise StopIteration()

  @classmethod
  def from_json(cls, json):
    """Creates an instance of the InputReader for the given input shard state.

    Args:
      input_shard_state: The InputReader state as a dict-like object.

    Returns:
      An instance of the InputReader configured using the values of json.
    """
    return cls(json[cls.CONFIGURATION_SHEET_KEY_PARAM],
               json[cls.CURRENT_POSITION_PARAM],
               json[cls.END_POSITION_PARAM])

  def to_json(self):
    """Returns an input shard state for the remaining inputs.

    Returns:
      A json-izable version of the remaining InputReader.
    """
    return {self.CONFIGURATION_SHEET_KEY_PARAM: self.configuration_sheet_key,
            self.CURRENT_POSITION_PARAM: self.current_position,
            self.END_POSITION_PARAM: self.end_position}

  def __str__(self):
    return str(self.configuration_sheet_key)

  @classmethod
  def validate(cls, mapper_spec):
    pass
    
  @classmethod
  def split_input(cls, mapper_spec):
    """Returns a list of input readers for the input spec.

    Args:
      mapper_spec: The MapperSpec for this InputReader.

    Returns:
      A list of InputReaders.

    Raises:
      BadReaderParamsError: required parameters are missing or invalid.
    """
    if mapper_spec.input_reader_class() != cls:
      raise BadReaderParamsError("Input reader class mismatch")
    params = mapper_spec.params
    if cls.CONFIGURATION_SHEET_KEY_PARAM not in params:
      raise BadReaderParamsError("Missing mapper parameter '%s'" %
                                 cls.CONFIGURATION_SHEET_KEY_PARAM)

    params = mapper_spec.params
    configuration_sheet_key = params[cls.CONFIGURATION_SHEET_KEY_PARAM]

    configuration_sheet = DataSeederConfigurationSheet.get(
      Key(configuration_sheet_key))

    data = simplejson.loads(configuration_sheet.json)

    shards = []

    for model in data:
      json = simplejson.dumps(model)

      model_configuration_sheet = DataSeederConfigurationSheet(json=json)
      model_configuration_sheet.put()
      key = str(model_configuration_sheet.key())

      shards.append(cls(key, 0, int(model['number'])))

    return shards

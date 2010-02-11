#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""The module which contains functions to manage tags in Melange.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


class TagsService(object):
  """Helper class for tags corresponding to a model.
  """

  def __init__(self, tag_names):
    """Defines tag names.
    """

    self.tag_names = tag_names

  def prepareTagsForStoring(self, fields, scope):
    """For those fields which represent task values it prepares actual
    tag entries.

    Args:
      fields: a dict mapping tag names with values
      scope: scope for the tag that will be stored
    """

    for tag_name, tag_value in fields.iteritems():
      if tag_name in self.tag_names:
        fields[tag_name] = {'tags': tag_value, 'scope': scope}

  def setTagValuesForEntity(self, entity, fields):
    """Sets tag values for a particular entity based on fields dictionary.

    Args:
      entity: an entity which is to be tagged
      fields: a dict mapping tag names with values
    """

    if not entity:
      return None

    for tag_name, tag_value in fields.iteritems():
      if tag_name in self.tag_names:
        setattr(entity, tag_name, tag_value)

    return entity

  def removeAllTagsForEntity(self, entity):
    """Removes all tags defined for a particular entity.

    Args:
      entity: entity which the tags will be removed for
    """

    self.removeTagsForEntity(entity, self.tag_names)

  def removeTagsForEntity(self, entity, tag_names):
    """Removes all tags values for a particular entity based on tag_names
    list with name of the tags that are to be removed.

    Args:
      entity: entity which the tags will be removed for
      tag_names: list of tags to remove
    """

    if not entity:
      return

    for tag_name in tag_names:
      if tag_name in self.tag_names:
        cls = entity.tags_class(tag_name)
        tags = cls.get_tags_for_key(entity.key())
        for tag in tags:
          tag.remove_tagged(entity.key())

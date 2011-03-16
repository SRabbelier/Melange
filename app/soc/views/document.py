#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module containing the template for documents.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.views.template import Template


class Document(Template):
  def __init__(self, data, entity):
    assert(entity != None)
    self.data = data
    self.entity = entity

  def context(self):
    return {
        'content': self.entity.content,
        'title': self.entity.title,
        'modified_by': self.entity.modified_by.name,
        'modified_on': self.entity.modified,
    }

  def templatePath(self):
    return "v2/soc/_document.html"

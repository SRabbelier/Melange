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

"""This module contains the Score Model."""

__authors__ = [
  '"Daniel Hans <daniel.m.hans@gmail.com>',
]


from google.appengine.ext import db

import soc.models.base
import soc.modules.gsoc.models.profile


class GSoCScore(soc.models.base.ModelWithFieldAttributes):
  """Model of a Score.
  """

  #: the value associated with the score
  value = db.IntegerProperty(required=True,
                             validator=lambda v: v >= 1 and v <= 5)

  #: reference to the profile of a user who has given the score
  author = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.profile.GSoCProfile,
      required=True, collection_name="scored")

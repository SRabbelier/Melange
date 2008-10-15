#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""This module contains the Response Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


import polymodel

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.quiz
import soc.models.user


class Response(polymodel.PolyModel):
  """Model of a Response to a Quiz.

  A Response is the "collection point" for a set of specific Answers to the
  Questions that make up a Quiz.

  In addition to the explicit ReferenceProperties in the Response Model, a
  Response entity participates in these relationships:

    answers)  a 1:many relationship between Answer entities and this
      Response.  Each Answer points to the Response to which it is a part.
      The collection of Answers that make up a Response is implemented as
      the 'answers' back-reference Query of the Answer model 'response'
      reference.
  """

  #: a required many:1 relationship between Responses and a Quiz that
  #: defines what Questions for which each Response collects Answers
  #: (that is, there can be many Responses to the same Quiz)
  quiz = db.ReferenceProperty(reference_class=soc.models.quiz.Quiz,
                              required=True, collection_name="responses")

  #: a required many:1 relationship with a User that indicates which User
  #: submitted the Response (answered the Questions in the Quiz)
  respondent = db.ReferenceProperty(
      reference_class=soc.models.user.User, required=True,
      collection_name="responses")

  # TODO(tlarsen): should 'respondent' be a ReferenceProperty to some Role
  #   instead?

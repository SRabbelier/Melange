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

"""This module contains the Answer Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

from soc import models
from soc.models import base

import soc.models.question
import soc.models.review


class Answer(base.ModelWithFieldAttributes):
  """Model of a specific Answer to a Question in a specific Review."""

  #: A required many:1 relationship, where each of many Answers is
  #: a specific answer to a single Question.  An Answer must always
  #: be associated with a Question in order to be interpreted.
  #: It is currently unclear how useful this back-reference will be,
  #: since the same question could be used in multiple different
  #: Review "templates". Given this, 'answers' currently only exists
  #: for completeness.
  # TODO: Uncomment when Question model is committed
  #question = db.ReferenceProperty(reference_class=models.question.Question,
  #                                required=True, collection_name="answers")

  #: A required many:1 relationship, where each of many Answers to
  #: different Questions represents the answer set of a specific
  #: Review. The back-reference in the Review model is a Query named
  #: 'answers' which represents all of the specific answers to
  #: questions in that Review.
  review = db.ReferenceProperty(reference_class=models.review.Review,
                                required=True, collection_name="answers")

  #: db.StringProperty storing the "short" answer to the question;
  #: the interpretation of this value depends on the Question entity
  #: referred to by 'question'. Answers can be indexed, filtered, and
  #: sorted by their "short" answer. Depending on the Question type,
  #: some Answers will use only 'short', some only 'long', some both.
  short = db.StringProperty()

  #: db.TextProperty storing the "long" answer to the question;
  #: the interpretation of this value depends on the Question entity
  #: referred to by 'question'.
  long = db.TextProperty()

  #: db.ListProperty of short strings from the list of possible
  #: picks in the question.pick_choices list.
  picks = db.ListProperty(item_type=str)


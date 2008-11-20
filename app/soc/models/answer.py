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

"""This module contains the Answer Model"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


import polymodel

from google.appengine.ext import db

import soc.models.question
import soc.models.quiz
import soc.models.response


class Answer(polymodel.PolyModel):
  """Model of a specific Answer to a Question in a specific Response.

  The properties in this Model do not have verbose_name or help_text,
  because the dynamic nature of the forms required to create, edit, and
  use entities of this Model make them pretty useless.
  """

  #: A required many:1 relationship, where each of many Answers is
  #: a specific answer to a single Question.  An Answer must always
  #: be associated with a Question in order to be interpreted.
  #: It is currently unclear how useful this back-reference will be,
  #: since the same Question could be used in multiple different
  #: Quizzes. Given this, 'answers' currently only exists for
  #: completeness.
  question = db.ReferenceProperty(
    reference_class=soc.models.question.Question, required=True,
    collection_name="answers")

  #: A many:1 relationship, where each of many Answers to different
  #: Questions represents the answer set of a specific Response to a Quiz.
  #: The back-reference in the Response model is a Query named 'answers'
  #: which represents all of the specific Answers to Questions in that
  #: Response.
  #:
  #: One and only one of the response or quiz ReferenceProperties *must*
  #: be defined for an Answer entity.
  response = db.ReferenceProperty(
      reference_class=soc.models.response.Response, required=False,
      collection_name="answers")

  #: A many:1 relationship, where each of many Answers to different
  #: Questions represents the solution set for the Questions in a Quiz.
  #: The back-reference in the Quiz model is a Query named 'solutions'
  #: which represents all of the solutions to Questions in that Quiz.
  #:
  #: One and only one of the response or quiz ReferenceProperties *must*
  #: be defined for an Answer entity.
  quiz = db.ReferenceProperty(
      reference_class=soc.models.quiz.Quiz, required=False,
      collection_name="solutions")

  #: db.ListProperty of strings representing the answer value or values.
  #:
  #: For Questions that are not multiple-choice (see the choice_ids and
  #: choices properties of soc.models.question.Question), this list will
  #: contain a single string that is a free-form text answer.
  #:
  #: For Questions that *are* multiple-choice, this list will contain one
  #: or more short, plain-text, "link_id-like" strings representing the
  #: "encoded" answer choices (see the choice_ids property in
  #: soc.models.question.Question).  For such multiple-choice Questions,    
  #: how many strings are stored depends on the max_answers property of
  #: the soc.models.question.Question entity for which this is an Answer.
  #:
  #: If question.is_optional is True, 'answers' may even be None or an
  #: empty list if no answers were provided.
  #:
  #: Answers can be indexed, filtered, and sorted by this list, but only in
  #: the way that query operators work with a db.ListProperty.
  answers = db.ListProperty(item_type=str)

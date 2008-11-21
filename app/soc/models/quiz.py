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

"""This module contains the Quiz Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]

import reflistprop

import soc.models.answer
import soc.models.question
import soc.models.work


class Quiz(soc.models.work.Work):
  """Model of a Quiz, a collection of Questions to be asked.
  
  (named Quiz because Questionnaire was too much to type...)
  
  A Quiz collects a set of Questions to which Answers are given in the
  form of a separate Model called a Response.

  Quizzes can even be used as templates for comments and scoring
  annotations to various Works, such as Documents and Proposals.  A
  separate Review Model is derived from Quiz for these purposes.

  The specific way that the properties and relations inherited from
  Document, and also indirectly from Work, are used with a Quiz are
  described below.

    work.title:  the title of the Quiz

    work.author:  the author of the Work referred to by this relation
      is the author of the Quiz (but not necessarily the individual
      Questions themselves, see the Question Model)

    work.reviews:  even Quizzes can be "reviewed" (possibly commented
      on during creation or annotated once put into use).

    work.content:  the "preface" of the Quiz, displayed before any
      of the Questions, usually containing instructions for the Quiz

    linkable.scope/linkable.link_id: used to scope and uniquely
      identify a Quiz in the same way these properties are used with
      Documents, etc.

  In addition to any explicit ReferenceProperties in the Quiz Model and
  those inherited as described above, a Quiz entity participates in these
  relationships:

    responses)  a 1:many relationship where each Quiz can produce all of
      its many Response entities that indicate they contain specific
      Answers to each of the Questions contained in that Quiz. This relation
      is implemented as the 'responses' back-reference Query of the Response
      Model 'quiz' reference.
      
    solutions)  a 1:many relationship where some (or none, or all) of the
      Questions in the Quiz have "solutions" or "correct Answers".  The
      'solutions' back-reference Query of the Answer Model 'quiz' reference
      is used to point these "correct Answers" at the Quiz to which they
      apply.  One example of a Quiz having a "correct Answer" is a GSoC
      mentor survey that has a "pass" Question that gates if the student
      gets paid.  The desired Answer for this Question would be
      associated with the Quiz via the 'quiz' property and some controller
      logic could check if a survey "passed" by querying for these
      "solution" Answers and seeing if the survey Response had the "right"
      Answers (to the one Question that matters in this case...).

    proposals)  a 1:many relationship where each Quiz can produce all of
      the Proposals that make use of the Quiz as part of the Proposal.
      This relation is implemented as the 'proposals' back-reference Query
      of the Proposal Model 'quiz' reference.
  """
  
  #: a many:many relationship (many:many because a given Question can be
  #: reused in more than one Quiz, and each Quiz is made up of one or more
  #: Questions) between Question entities and, when combined, the Quiz they
  #: form.
  #:
  #: A ReferenceListProperty is used instead of a special many:many
  #; relation Model for a number of reasons:
  #:   1) the Questions in a Quiz need to be ordered
  #:   2) Quizzes will have relatively few Questions, so the performance
  #:      ReferenceListProperty is not a major concern
  #:   3) querying a Question for all of the Quizzes that contain it is
  #:      a rare occurrence, so the expense of a ListProperty query is
  #:      not a real concern
  questions = reflistprop.ReferenceListProperty(
    soc.models.question.Question, default=None) 

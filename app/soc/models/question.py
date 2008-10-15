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

"""This module contains the Question Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

import soc.models.work


class Question(soc.models.work.Work):
  """Model of a Question, which is a specialized form of Work.

  Specific types of Questions are actually implemented in subclasses.

  The specific way that the properties and relations inherited from
  Work are used with a Question are described below.

    work.title:  the title of the Question, used for finding the
      Question in a list of Questions

    work.abstract:  the Question text, asked to the respondent

    work.authors:  the Authors of the Work referred to by this relation
      are the authors of the Question

    work.reviews:  even Questions can be "reviewed" (possibly commented
      on during creation or annotated once put into use).

    work.partial_path: used to scope (and, when combined with
      work.link_name, uniquely identify) a Question in the same way the
      property are used with Documents, etc.

    work.link_name: used to identify (and, when combined with
      work.partial_path, *uniquely* identify) a Question in the same way
      these properties are used with Documents, etc.
      
  In addition to any explicit ReferenceProperties in the Question Model
  and those inherited as described above, a Question entity participates
  in these relationships:

    answers)  a 1:many relationship, where each Question has many different
      Answers associated with it as parts of Responses to Quizzes.  This is
      implemented as the 'answers' back-reference Query of the Answer model
      'question' reference.  It is currently unclear how useful this
      back-reference will be, since the same Question could be used in
      multiple different Quizzes. Given this, 'answers' currently only
      exists for completeness.
      
    quizzes)  a many:many relationship between Questions and the Quizzes
      that collect them into a set.  This relation is not explicitly
      implemented, but can be obtained via a query something like:
      
        quizzes_with_a_question = db.GqlQuery(
            "SELECT * FROM Quiz where questions = :1",
            a_question.key())

      Such queries are probably only needed when a Question might be
      altered, in order to find which Quizzes will be affected.

  The properties in this Model do not have verbose_name or help_text,
  because the dynamic nature of the forms required to create, edit, and
  use entities of this Model make them pretty useless.
  
  ######################################################################
  # TODO(tlarsen): the following verbose comments can be removed later,
    when these ideas are implemented in the views and controllers; they
    are here now so that the concepts will not be lost before that time.

  The recommended use for the combination of work.partial_path and
  work.link_name is to keep the *same* link_name when copying and
  modifying an existing Question for a new Program (or instance of a
  Group that is per-Program), while changing the work.partial_path to
  represent the Program and Group "ownership" of the Question.  For
  example, if a Question asking about prior GSoC participation needed
  to have an additional choice (see the choice_ids and choices properties
  below), it is desirable to keep the same work.link_name (and also
  simply append new choice_ids and choices to keep the old answer values
  compatible).  An existing Question in the above example might be identified
  as something like:
    Question:google/gsoc2009/gsoc_past_participation
    <type>:<Sponsor>/<Program>/<link_name> 
  To make it possible to query for gsoc_past_participation answers regardless
  of the Program, the next year, new values are added to choice_ids and
  choices in a new Question copied from the one above, which would then
  be named something (still unique) like:
    Question:google/gsoc2010/gsoc_past_participation
  Care just needs to be taken to keep the existing choice_ids and choices
  compatible.
  
  Other interesting possibilities also exist, such as asking about GSoC
  participation of the GHOP participants (some GHOP high school students
  have actually previously been GSoC mentors, for example).  To produce
  unique statistics for GHOP that could also be aggregated overall in
  combination with GSoC, the gsoc_past_participation Question would be
  duplicated (unaltered) to something like:
    Question:google/ghop2009/gsoc_past_participation
  To get the combined results, query on a link_name of
  gsoc_past_participation.  For more targeted results, include the
  partial_path to make the query more specific.

  Question creation to permit use cases like the one above is going to
  be a bit of an "advanced" skill, possibly.  "Doing it wrong" the first
  time a Question is created will make it difficult to implement stuff
  like multiple-choice Questions that "grow" new choices year-over-year.

  A dynamic form is most definitely going to be needed to implement the
  Question creation and editing for multiple-choice questions.
  """
  #: db.ListProperty of short, plain-text, "link_name-like" strings
  #: representing the "encoded" answer choices (must be strings compatible
  #: with being query arguments and being used in HTML controls and POST
  #: responses).
  #:
  #: If empty (None or an empty list), it is assumed that this Question
  #: is *not* a multiple choice question.  In that case, the UI should
  #: display the Question as a textarea in forms and accept any plain-text.
  #:
  #: If non-empty, max_answers helps determine how the UI should display
  #: the Question.  Also, controller logic needs to validate if the
  #: strings in the 'answers' property of the Answer entity come only
  #: from this list.
  #:
  #: Once Answers to this Question have been stored in the Datastore,
  #: choice_ids and choices should *not* be modified.  An existing
  #: Question can be duplicated and then modified (but, it will be a
  #: different question as a result).
  choice_ids = db.ListProperty(item_type=str)

  #: db.ListProperty of human-readable choice strings, in the same order
  #: as, and corresponding to, the "encoded" choices in the choice_ids
  #: db.ListProperty. 
  choices = db.ListProperty(item_type=str)

  #: db.IntegerProperty indicating the maximum number of answer values
  #: permitted for this question.  If 'choices' does not contain a list of
  #: choice strings, this value is ignored (but should still only be 1).
  #:
  #: If there are 'choices' and this value is 1, the UI should render the
  #: Question in forms as a single-choice control ("radio buttons").
  #:
  #: If there are 'choices' and this value is greater than 1, the UI should
  #: render the question as a list of check-boxes.
  #:
  #: max_answers greater than 1 combined with choices enables Questions
  #: like, for example, "...select the three most important...".
  max_answers = db.IntegerProperty(default=1)

  #: field storing whether the Answer to a Question is optional
  is_optional = db.BooleanProperty(default=False)

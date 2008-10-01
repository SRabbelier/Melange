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

"""This module contains the Review Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
import soc.models.survey
import soc.models.work
import soc.models.reviewer


class Review(db.Model):
  """Model of a review of a Proposal or a Task.

  A Review entity is a specific instance of a completed Survey, collecting
  the Answers to the Questions that are found in that Survey.

  Reviews are also used to implement comments and scoring annotations
  to Proposals and Tasks. For example, a commment attached to a
  Proposal is a Review with the Answer to a single "question" (with
  that answer being the comment itself).  A scoring  evaluation might
  be made up of Answers to two "questions", one containg the comment
  the other containing the score.

  A Review entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   answers) A 1:many relationship (but not required, since initially
     none of the Questions to be answered by a Review will have
     Answers) that relates the specific answers to the Survey
     questions for a specfic Review instance. This relation is
     implemented as a back-reference Query of the Answer model
     'review' reference.

     Some (zero or more) of the Questions answered by a Review may
     define an 'approval_style' string and one or more
     'approval_answers'. See the Question and Answer models for
     details. All Questions answered in the Review that provide
     non-empty 'approval_style' and 'approval_answers' must meet the
     described approval conditions for the Review to represent 
     "approval" (or a "positive outcome" or a "passing grade", so to
     speak). Most Reviews answer Questions in a Survey that contains
     only a single "approval" question (if they contain one at all).
  """

  #: A required many:1 relationship with a Survey which acts as a
  #: "template" for the Review, containing the Questions that are
  #: anwered by the Answers associated with the Review. The
  #: back-reference in the Survey model is a Query named 'reviews'
  #: which represents all of the Reviews that contains Answers to the
  #: Questions in that particular Survey.
  # TODO: Uncomment when Survey model is committed
  #survey = db.ReferenceProperty(reference_class=soc.models.survey.Survey,
  #                              required=True, collection_name="reviews")

  #: A required many:1 relationship with a Work, where the Review
  #: answers are attached to the Work as a comment, evaluation,
  #: review, report, acceptance, etc. Reviews are the mechanism by
  #: which non-authors of the Work make annotations to it. The
  #: back-reference in the Work model is a Query named 'reviews'
  #: which represents all of the annotations attached to that
  #: particular work.
  reviewed = db.ReferenceProperty(reference_class=soc.models.work.Work, 
                                  required=True, collection_name="reviews")
                                  
  #: A required many:1 relationship with a Reviewer entity indicating
  #: the "author" of the actual answers for a specific Review
  #: instance. The back-reference in the Reviewer model is a Query
  #: named 'reviews' which represents all of the Reviews by that
  #: particular Reviewer.
  reviewer = db.ReferenceProperty(reference_class=soc.models.reviewer.Reviewer,
                                  required=True, collection_name="reviews")


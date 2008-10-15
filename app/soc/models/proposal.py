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

"""This module contains the Proposal Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

import soc.models.document
import soc.models.quiz
import soc.models.response


class Proposal(soc.models.document.Document):
  """Model of a Proposal, which is a specific form of a Work.

  The specific way that the properties and relations inherited from Work
  are used with a Proposal are described below.

  work.title:  the title of the Proposal

  work.abstract:  publicly displayed as a proposal abstract or summary

  work.reviews:  reviews of the Proposal by Reviewers

  document.content:  the details of the Proposal; which, unlike work.abstract
    is considered "public" information, the contents of a Proposal are only
    displayed to Persons in Roles that have a "need to know" those details.

  A Proposal entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

  tasks)  an optional 1:many relationship of Task entities using the
    Proposal as their foundation.  This relation is implemented as the
    'tasks' back-reference Query of the Task model 'proposal' reference.
  """
  #: an optional many:1 relationship between Proposal and a Quiz that
  #: defines what Questions were added by the prospective Proposal Reviewer
  #: for the Proposal author to answer.
  quiz = db.ReferenceProperty(reference_class=soc.models.quiz.Quiz,
                              required=False, collection_name="proposals")

  #: an optional 1:1 relationship where a Proposal author's Answers to
  #: a Quiz attached to the Proposal template by the Proposal Reviewer
  #; are collected. 
  response = db.ReferenceProperty(
      reference_class=soc.models.response.Response, required=False,
      collection_name="proposal")

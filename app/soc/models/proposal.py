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

from soc import models
from soc.models import base
import soc.models.work

class Proposal(base.ModelWithFieldAttributes):
  """Model of a Proposal, which is a specific form of a Work.

  A Proposal entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

  tasks)  an optional 1:many relationship of Task entities using the
    Proposal as their foundation.  This relation is implemented as the
    'tasks' back-reference Query of the Task model 'proposal' reference.

  """

	#: Required 1:1 relationship with a Work entity that contains the
	#: general "work" properties of the Proposal.  The back-reference in the Work
	#: model is a Query named 'proposal'.
	#: 
	#: work.authors:  the Authors of the Work referred to by this relation
	#: are the authors of the Proposal.
	#: work.title:  the title of the Proposal.
	#: work.abstract:  publicly displayed as a proposal abstract or summary.
	#: work.reviews:  reviews of the Proposal by Reviewers.
  work = db.ReferenceProperty(reference_class=models.work.Work, required=True,
                              collection_name="proposal")

  #: Required db.TextProperty describing the proposal in detail.
  #: Unlike the work.abstract, which is considered "public" information,
	#: the contents of 'details' is only to be displayed to Persons in roles
  #: that have a "need to know" the details.
  details = db.TextProperty(required=True)

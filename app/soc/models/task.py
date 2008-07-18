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

"""This module contains the Task Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
import soc.models.proposal


class Task(db.Model):
  """Model of a Task, which is a Proposal to be completed by Contributors.

  A Task brings along a Proposal that was used to initiate the Task.  A Task
  may have a unique collection of Reviews, in addition to those attached to
  the original Proposal.

  A Task entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   contributors)  a required many:many relationship associating all of
     the Contributors to a Task to the specific Task.  See the
     TasksContributors model for details.
  """
 
  #: A required many:1 relationship with the Proposal on which the
  #: Task is based.  A Task may be based on only a single Proposal, 
  #: but a Proposal can be the foundation for multiple Tasks. The
  #: back-reference in the Proposal model is a Query named 'tasks'.  
  proposal = db.ReferenceProperty(reference_class=models.proposal.Proposal,
                                  required=True,
				  collection_name="tasks")


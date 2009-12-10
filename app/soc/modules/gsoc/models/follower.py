#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""This module contains the Follower Model."""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

import soc.models.linkable


class Follower(soc.models.linkable.Linkable):
  """Details specific to a Follower.

    A Follower is a generic model which indicates that a User is following
    some other Linkable entity in the application.

    Scope and scope_path should be set to the entity being followed.
    The link_id should be used to indicate which user is following.

    If more functionality is needed like for instance when following 
    either a public or private review for Student Proposals this model
    should be extended. As to make it possible to create different types
    of following.
  """

  #: Required property to tie a user to the entity it is following
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name='following')


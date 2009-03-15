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

"""This module contains the Review Follower Model."""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

import soc.models.follower


class ReviewFollower(soc.models.follower.Follower):
  """Details specific to a Review Follower.
  """

  #: Required property indicating if the public reviews should be followed
  subscribed_public = db.BooleanProperty(required=True, default=False)

  #: Required property indicating if the private reviews should be followed
  subscribed_private = db.BooleanProperty(required=True, default=False)

#!/usr/bin/python2.5
#
# Copyright 2010 the Melange authors.
# Copyright 2009 Jake McGuire.
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

"""Module containing a storage model for stats data.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.ext import db


class ProfileData(db.Model):
  """Profile data for one request.
  """

  #: the profile data in gzipped pickled string form
  profile = db.BlobProperty(required=True)

  #: the path of the request this profile data belongs to
  path = db.StringProperty(required=True)

  #: the user that made the request this profile data belongs to, if any
  user = db.UserProperty()

  #: the time at which the profile data was stored
  timestamp = db.DateTimeProperty(auto_now=True)

  #: the version off the app when profile data was collected
  version = db.StringProperty()


def from_key(key):
  """Returns profile data for the specified key.
  """

  return ProfileData.get_by_id(int(key))


def store(path, profile, user, version):
  """Stores the profile data with the specified attributes.
  """

  ProfileData(path=path, profile=profile, user=user, version=version).put()

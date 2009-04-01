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

"""This module supplies an interactive shell with remote api configured.

Usage is simple:

App Engine interactive console
>>> from soc.models.user import User
>>> gen = lambda: User.all()
>>> it = deepFetch(gen)
>>> result = [i for i in it]
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]



import code
import getpass
import os
import sys
import sys


def auth_func():
  """Returns a tuple with username and password.
  """

  return raw_input('Username:'), getpass.getpass('Password:')


def deepFetch(queryGen,key=None,batchSize = 100):
  """Iterator that yields an entity in batches.

  Args:
    queryGen: should return a Query object
    key: used to .filter() for __key__
    batchSize: how many entities to retrieve in one datastore call

  Retrieved from http://tinyurl.com/d887ll (AppEngine cookbook).
  """

   # AppEngine will not fetch more than 1000 results
  batchSize = min(batchSize,1000)

  query = None
  done = False
  count = 0

  if key:
    key = db.Key(key)

  while not done:
    query = queryGen()
    if key:
      query.filter("__key__ > ",key)
    results = query.fetch(batchSize)
    for result in results:
      count += 1
      yield result
    if batchSize > len(results):
      done = True
    else:
      key = results[-1].key()


def remote(args, context=None):
  """Starts a shell with the datastore as remote_api_stub.

  Args:
    args: arguments from the user
    context: locals that should be added to the shell
  """

  from google.appengine.ext import db
  from google.appengine.ext.remote_api import remote_api_stub

  if not context:
    context = {}

  app_id = args[0]

  if len(args) > 1:
    host = args[1]
  else:
    host = '%s.appspot.com' % app_id

  remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)

  context['deepFetch'] = deepFetch

  code.interact('App Engine interactive console for %s' % (app_id,), None, context)


def setup():
  """Sets up the sys.path and environment for development.
  """

  here = os.path.abspath(__file__)
  here = os.path.join(os.path.dirname(here), '..')
  here = os.path.normpath(here)

  appengine_location = os.path.join(here, 'thirdparty', 'google_appengine')

  extra_paths = [here,
                 os.path.join(appengine_location, 'lib', 'django'),
                 os.path.join(appengine_location, 'lib', 'webob'),
                 os.path.join(appengine_location, 'lib', 'yaml', 'lib'),
                 appengine_location,
                 os.path.join(here, 'app'),
                ]

  sys.path = extra_paths + sys.path

  os.environ['SERVER_SOFTWARE'] = 'Development Interactive Shell'

  import main as app_main

def main(args):
  """Convenience wrapper that calls setup and remote.
  """

  setup()
  remote(args)


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % (sys.argv[0],)
    sys.exit(1)

  main(sys.argv[1:])

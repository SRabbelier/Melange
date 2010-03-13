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

"""Module containing a profiler tuned for GAE requests.
"""

__authors__ = [
  '"Jake McGuire" <jaekmcguire@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import cProfile
import logging
import ppstats
import random
import string
import zlib

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.api.labs import taskqueue

from soc.profiling import storage


alphanumeric = string.letters + string.digits
mc_client = memcache.Client()


class GAEProfiler(object):
  """Profiler class that contains profiling data.
  """

  def __init__(self, path=None, key=None):
    """Constructs a new profiler for the given path.
    """

    self._profiler = cProfile.Profile()
    self.loaded = False
    self.task_url = '/profiler/store'

    data = storage.from_key(key) if key else None

    if data:
      self.profile_key = key
      self.pstats_obj = ppstats.from_gz(data.profile)
      self.path = data.path
      self.loaded = True
    else:
      key = [random.choice(alphanumeric) for x in range(6)]
      self.profile_key = ''.join(key)
      self.pstats_obj = None
      self.path = path

  def get_pstats(self):
    """Return a ppstats object from current profile data.
    """

    if self.pstats_obj:
        return self.pstats_obj

    gae_base_dir = '/'.join(webapp.__file__.split('/')[:-5])
    sys_base_dir = '/'.join(logging.__file__.split('/')[:-2])
    app_base_dir = '/'.join(storage.__file__.split('/')[:-3])
    logging.info(app_base_dir)

    stats = ppstats.Stats(self._profiler)
    stats.hide_directory(gae_base_dir, 'GAEHome')
    stats.hide_directory(sys_base_dir, 'SysHome')
    stats.hide_directory(app_base_dir, 'AppHome')
    stats.strip_dirs()

    self.pstats_obj = stats

    return stats

  def runcall(self, func, *args, **kwargs):
    """Profile one call, saving stats.
    """

    self.pstats_obj = None
    ret = self._profiler.runcall(func, *args, **kwargs)
    self.save_pstats_with_task()
    return ret

  def save_pstats_with_task(self):
    """Save stats from profiler object to memcache.
    """

    ps = self.get_pstats()
    output = ps.dump_stats_pickle()
    compressed_data = zlib.compress(output, 3)

    cache_key = cache_key_for_profile(self.profile_key)
    mc_client.set(cache_key, compressed_data)

    new_task = taskqueue.Task(url=self.task_url, params={
        'key': self.profile_key,
        'path': self.path,
        'user': users.get_current_user(),
    })
    new_task.add('profiler')

    logging.info("Queued pstats save with key '%s' on path '%s' of size %d" % (
        self.profile_key, self.path, len(compressed_data)))


def cache_key_for_profile(profile_key):
  """Returns a memcache key for the specified profile key.
  """

  return "ProfileData.%s" % profile_key

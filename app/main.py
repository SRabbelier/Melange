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

"""Main Melange module with profiling support.
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Augie Fackler" <durin42@gmail.com>',
  ]


import logging
import os
import sys

from google.appengine.ext.webapp import util


# Remove the standard version of Django.
for k in [k for k in sys.modules if k.startswith('django')]:
  del sys.modules[k]

# Force sys.path to have our own directory first, in case we want to import
# from it. This lets us replace the built-in Django
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

sys.path.insert(0, os.path.abspath('django.zip'))

ultimate_sys_path = None

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
import django.core.signals
import django.db

# Log errors.
def log_exception(*args, **kwds):
  """Function used for logging exceptions.
  """
  logging.exception('Exception in request:')

# Log all exceptions detected by Django.
django.core.signals.got_request_exception.connect(log_exception)

# Unregister the rollback event handler.
django.core.signals.got_request_exception.disconnect(
    django.db._rollback_on_exception)


def profile_main_as_html():
  """Main program for profiling. Profiling data added as HTML to the page.
  """
  import cProfile
  import pstats
  import StringIO

  prof = cProfile.Profile()
  prof = prof.runctx('real_main()', globals(), locals())
  stream = StringIO.StringIO()
  stats = pstats.Stats(prof, stream=stream)
  # stats.strip_dirs()  # Don't; too many modules are named __init__.py.
  
  # 'time', 'cumulative' or 'calls'
  stats.sort_stats('time')  
  
  # Optional arg: how many to print
  stats.print_stats() 
  # The rest is optional.
  # stats.print_callees()
  # stats.print_callers()
  print '\n<hr>'
  print '<h1>Profile data</h1>'
  print '<pre>'
  print stream.getvalue()[:1000000]
  print '</pre>'


def profile_main_as_logs():
  """Main program for profiling. Profiling data logged.
  """
  import cProfile
  import pstats
  import StringIO
  
  prof = cProfile.Profile()
  prof = prof.runctx("real_main()", globals(), locals())
  stream = StringIO.StringIO()
  stats = pstats.Stats(prof, stream=stream)
  stats.sort_stats('time')  # Or cumulative
  stats.print_stats(80)  # 80 = how many to print
  # The rest is optional.
  # stats.print_callees()
  # stats.print_callers()
  logging.info("Profile data:\n%s", stream.getvalue())


def real_main():
  """Main program without profiling.
  """
  global ultimate_sys_path
  if ultimate_sys_path is None:
    ultimate_sys_path = list(sys.path)
  else:
    sys.path[:] = ultimate_sys_path

  # Create a Django application for WSGI.
  application = django.core.handlers.wsgi.WSGIHandler()

  # Run the WSGI CGI handler with that application.
  util.run_wsgi_app(application)

main = real_main

if __name__ == '__main__':
  main()

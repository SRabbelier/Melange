#!/usr/bin/env python2.5
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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import logging

from google.appengine.ext.webapp import util

# pylint: disable=W0611
import gae_django


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
  import django.core.handlers.wsgi

  # Create a Django application for WSGI.
  application = django.core.handlers.wsgi.WSGIHandler()

  from soc.modules import callback
  from soc.modules import core

  import settings

  callback.registerCore(core.Core())
  callback.getCore().registerModuleCallbacks(settings.MODULES,
                                             settings.MODULE_FMT)
  callback.getCore().initialize()

  # Run the WSGI CGI handler with that application.
  util.run_wsgi_app(application)

main = real_main

if __name__ == '__main__':
  main()

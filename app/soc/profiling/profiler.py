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


import cProfile
import ppstats

from google.appengine.ext import webapp
from google.appengine.api import memcache
import google.appengine.ext.webapp.util

from email.MIMEMultipart import MIMEMultipart
from email.Message import Message

import httplib
import logging
import os.path
import random
import re
import string
import zlib

mc_client = memcache.Client()

alphanumeric = string.letters + string.digits

global_profiler = None

class GAEProfiler(object):
    _save_every = 10

    def __init__(self):
        self.is_profiling = False
        self._profiler = None
        self.num_requests = 0
        self.requests_profiled = 0
        self.request_regex = None
        self.profile_key = ''.join([random.choice(alphanumeric) for x in range(4)])
        self.pstats_obj = None

    def start_profiling(self, request_regex=None, num_requests=0):
        "start profiling with this object, setting # of requests and filter"
        if self.is_profiling:
            return

        self.is_profiling = True
        if self._profiler is None:
            self._profiler = cProfile.Profile()
        self.num_requests = num_requests
        if request_regex:
            self.request_regex = re.compile(request_regex)

    def stop_profiling(self):
        self.is_profiling = False

    def resume_profiling(self):
        self.is_profiling = True

    def has_profiler(self):
        return self.pstats_obj or (self._profiler is not None)

    def get_pstats(self):
        "return a ppstats object from current profile data"
        if self.pstats_obj:
            return self.pstats_obj

        if not self._profiler:
            return None

        gae_base_dir = '/'.join(webapp.__file__.split('/')[:-5])
        sys_base_dir = '/'.join(logging.__file__.split('/')[:-2])

        stats = ppstats.Stats(self._profiler)
        stats.hide_directory(gae_base_dir, 'GAEHome')
        stats.hide_directory(sys_base_dir, 'SysHome')
        stats.strip_dirs()

        self.pstats_obj = stats

        return stats

    def runcall(self, func, *args, **kwargs):
        "profile one call, incrementing requests_profiled and maybe saving stats"
        self.requests_profiled += 1
        self.pstats_obj = None
        if self._profiler:
            ret = self._profiler.runcall(func, *args, **kwargs)
        else:
            ret = func(*args, **kwargs)

#        if (self.requests_profiled % self._save_every) == 0 or \
#                self.requests_profiled == self.num_requests:
#            self.save_pstats_to_memcache()
        self.save_pstats_to_memcache()
        return ret

    def should_profile_request(self):
        "check for # of requests profiled and that SCRIPT_NAME matches regex"
        env = dict(os.environ)
        script_name = env.get('SCRIPT_NAME', '')
        logging.info(script_name)

        if self.num_requests and self.requests_profiled >= self.num_requests:
            return False

        if self.request_regex and not self.request_regex.search(script_name):
            return False

        return True

    def save_pstats_to_memcache(self):
        "save stats from profiler object to memcache"
        ps = self.get_pstats()
        output = ps.dump_stats_pickle()
        compressed_data = zlib.compress(output, 3)
        cache_key = cache_key_for_profile(self.profile_key)
        mc_client.set(cache_key, compressed_data)
        logging.info("Saved pstats to memcache with key %s" % cache_key)

def get_global_profiler():
    global global_profiler
    if not global_profiler:
        global_profiler = GAEProfiler()

    return global_profiler

def new_global_profiler():
    global global_profiler
    global_profiler = GAEProfiler()
    return global_profiler

def cache_key_for_profile(profile_key):
    "generate a memcache key"
    return "ProfileData.%s" % profile_key

def load_pstats_from_memcache(profile_key):
    "retrieve ppstats object"
    mc_data = mc_client.get(cache_key_for_profile(profile_key))
    if not mc_data:
        return None

    return ppstats.from_gz(mc_data)

def get_stats_from_global_or_request(request_obj):
    "get pstats for a key, or the global pstats"
    key = request_obj.get('key', '')
    if key:
        gp = GAEProfiler()
        gp.pstats_obj = load_pstats_from_memcache(key)
        if not gp.pstats_obj:
            return None
        gp.profile_key = key
        return gp
    else:
        gp = get_global_profiler()
        gp.get_pstats()
        return gp

def mime_upload_data_as_file(field_name, filename, body):
    part = Message()
    part['Content-Disposition'] = 'form-data; name="%s"; filename="%s"' % (field_name, filename)
    part['Content-Transfer-Encoding'] = 'binary'
    part['Content-Type'] = 'application/octet-stream'
    part['Content-Length'] = str(len(body))
    part.set_payload(body)
    return part

def mime_form_value(name, value):
    part = Message()
    part['Content-Disposition'] = 'form-data; name="%s"' % name
    part.set_payload(value)
    return part

class show_profile(webapp.RequestHandler):
    def get(self):
        ps = get_stats_from_global_or_request(self.request)
        if not ps or not ps.has_profiler():
            self.response.out.write("<body><html><h3>No profiler.</h3><html></body>")
            return

        ps.pstats_obj.set_output(self.response.out)
        sort = self.request.get('sort', 'time')
        ps.pstats_obj.sort_stats(sort)
        self.response.out.write("<body><html><pre>\n")
        ps.pstats_obj.print_stats(30)
        self.response.out.write("</pre></html></body>")

class download_profile_data(webapp.RequestHandler):
    def get(self):
        ps = get_stats_from_global_or_request(self.request)
        if not ps:
            self.response.out.write("<body><html><h3>No profiler.</h3><html></body>")
            return

        output = ps.pstats_obj.dump_stats_pickle()

        self.response.headers['Content-Type'] = 'application/octet-stream'

        self.response.out.write(output)

class send_profile_data(webapp.RequestHandler):
    def get(self):
        ps = get_stats_from_global_or_request(self.request)
        if not ps:
            self.response.out.write("<body><html><h3>No profiler.</h3><html></body>")
            return

        dest = self.request.get('dest', '')
        if not dest:
            self.response.out.write("<body><html>No destination</html></body>")

        upload_form = MIMEMultipart('form-data')

        upload_filename =  'profile.%s.pstats' % ps.profile_key
        upload_field_name = 'profile_file'

        upload_form.attach(mime_upload_data_as_file('profile_file',
                                                    upload_field_name,
                                                    zlib.compress(ps.pstats_obj.dump_stats_pickle())))
        upload_form.attach(mime_form_value('key_only', '1'))

        http_conn = httplib.HTTPConnection(dest)
        http_conn.connect()
        http_conn.request('POST', '/upload_profile', upload_form.as_string(),
                          {'Content-Type': 'multipart/form-data; boundary=%s' % upload_form.get_boundary()})

        http_resp = http_conn.getresponse()
        remote_data = http_resp.read()
        if http_resp.status == 200:
            remote_url = "http://%s/view_profile?key=%s" % (dest, remote_data)
            self.response.out.write("<html><body>Success! <a href='%s'>%s</a></body></html>" % (remote_url, remote_url))
        else:
            self.response.out.write("Failure!\n%s: %s\n%s" % (http_resp.status, http_resp.reason, remote_data))

class show_profiler_status(webapp.RequestHandler):
    def get(self):
        gp = get_global_profiler()
        if not gp.has_profiler():
            self.response.out.write("<body><html><h3>No profiler.</h3><html></body>")
            return

        self.response.out.write("<html><body>")
        self.response.out.write("<b>Currently profiling:</b> %s<br>" % gp.is_profiling)
        self.response.out.write("<b>Profile Key</b>: %s<br>" % gp.profile_key)
        self.response.out.write("<b>Requests profiled so far:</b> %s<br>" % gp.requests_profiled)
        self.response.out.write("<b>Requests to profile:</b> %s<br>" % gp.num_requests)
        self.response.out.write("<b>Request regex:</b> %s<br>" % gp.request_regex)
        self.response.out.write("</body></html>")

class start_profiler(webapp.RequestHandler):
    def get(self):
        gp = new_global_profiler()
        gp.start_profiling()
        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write("Started profiling (key: %s).\n" % gp.profile_key)
        self.response.out.write("Retrieve saved results at <a href='/profiler/show?key=%(key)s'>/profiler/show?key=%(key)s).\n" % {'key':gp.profile_key})
        logging.info("Started profiler %s", gp.profile_key)

class stop_profiler(webapp.RequestHandler):
    def get(self):
        gp = get_global_profiler()
        gp.stop_profiling()
        self.request.out.write("Content-Type: text/plain\n\n")
        self.request.out.write("done.")

class save_profile_data(webapp.RequestHandler):
    def get(self):
        gp = get_global_profiler()


def _add_our_endpoints(application):
    "insert our URLs into the application map"
    url_mapping = [(regex.pattern, handler) for (regex, handler) in application._url_mapping]
    return webapp.WSGIApplication(url_mapping, debug=True)

#
#  wrapper to for webapp applications
#
def run_wsgi_app(application):
    "proxy webapp.util's call to profile when needed"
    gp = get_global_profiler()
    if gp.is_profiling and gp.should_profile_request():
        return gp.runcall(google.appengine.ext.webapp.util.run_wsgi_app, *(application,))
    else:
        return google.appengine.ext.webapp.util.run_wsgi_app(application)

#
# middleware for django applications
#

class ProfileMiddleware(object):
    def __init__(self):
        self.profiler = None

    def process_request(self, request):
        self.profiler = get_global_profiler()

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.profiler.is_profiling:
            return self.profiler.runcall(callback, request, *callback_args, **callback_kwargs)

application = webapp.WSGIApplication(
    [('/profiler/start', start_profiler),
     ('/profiler/stop', stop_profiler),
     ('/profiler/show', show_profile),
     ('/profiler/download', download_profile_data),
     ('/profiler/status', show_profiler_status),
     ('/profiler/send', send_profile_data),
     ],
    debug=True)


def main():
    google.appengine.ext.webapp.util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

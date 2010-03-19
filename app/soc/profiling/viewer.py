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


import httplib
import logging
import zlib

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp

import google.appengine.ext.webapp.util

from email.MIMEMultipart import MIMEMultipart
from email.Message import Message

from soc.profiling import storage
from soc.profiling import profiler


mc_client = memcache.Client()


def get_stats_from_request(request_obj):
  """Get pstats for a key, or the global pstats.
  """
  key = request_obj.get('key', '')

  if not key:
    return None

  gp = profiler.GAEProfiler(key=key)

  return gp if gp.loaded else None


def mime_upload_data_as_file(field_name, filename, body):
  """Returns a mime formatted email message.

  Args:
    field_name: the 'name' field of the Content-Disposition
    filename: the 'filename' field of the Content-Disposition
    body: the payload of the message
  """

  part = Message()
  part['Content-Disposition'] = 'form-data; name="%s"; filename="%s"' % (field_name, filename)
  part['Content-Transfer-Encoding'] = 'binary'
  part['Content-Type'] = 'application/octet-stream'
  part['Content-Length'] = str(len(body))
  part.set_payload(body)
  return part


def mime_form_value(name, value):
  """Returns a mime form value.

  Args:
    name: the name of the value
    value: the value
  """

  part = Message()
  part['Content-Disposition'] = 'form-data; name="%s"' % name
  part.set_payload(value)
  return part


class SimpleHandler(webapp.RequestHandler):
  """Simple web app handler.
  """

  def write_header(self):
    """Writes a simple header.
    """

    key = self.request.get('key')

    self.response.out.write("<html><body>\n")
    self.response.out.write('<a href="/profiler/show?key=%s">Show</a> |' % key)
    self.response.out.write('<a href="/profiler/download?key=%s">Download</a> |' % key)
    self.response.out.write('<a href="/profiler/send?key=%s&dest=profileagg.appspot.com">Send</a>' % key)
    self.response.out.write('<br />\n')

  def write_footer(self):
    """Writes a simple footer.
    """

    self.response.out.write("</body></html>\n")

  def write_tagged(self, data, tag=None):
    """Returns a message wrapped in html and body tags.

    Args:
      message: the message that should be wrapped
      tag: optional additional tag that should wrap the message
    """

    msg = "<%s>%s</%s>" % (tag, data, tag)

    self.write_header()
    self.response.out.write(msg)
    self.write_footer()

  def no_profiler(self):
    """Writes a message saying there is no profiler.
    """

    self.write_tagged("No profile data with the specified key.", "h3")

class show_profile(SimpleHandler):
  """View that displays specific stats data.
  """

  def get(self):
    """Get handler for the show profile view.
    """

    ps = get_stats_from_request(self.request)

    if not ps:
      self.no_profiler()
      return

    ps.pstats_obj.set_output(self.response.out)
    sort = self.request.get('sort', 'time')
    ps.pstats_obj.sort_stats(sort)

    self.write_header()
    self.response.out.write("\n<pre>\n")
    ps.pstats_obj.print_stats(30)
    self.response.out.write("\n</pre>\n")
    self.write_footer()


class download_profile_data(SimpleHandler):
  """View that provies allows downloading a stats object.
  """

  def get(self):
    """Get handler for the download view.
    """

    ps = get_stats_from_request(self.request)

    if not ps:
      self.no_profiler()
      return

    output = ps.pstats_obj.dump_stats_pickle()

    self.response.headers['Content-Type'] = 'application/octet-stream'
    self.response.out.write(output)


class send_profile_data(SimpleHandler):
  """View that allows sending a stats url to a remote url.
  """

  def get(self):
    """Get handler for the send view.
    """

    ps = get_stats_from_request(self.request)

    if not ps:
      self.no_profiler()
      return

    dest = self.request.get('dest', '')

    if not dest:
      self.write_tagged("No destination specified.", "h3")
      return

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
      self.write_tagged("Success! <a href='%s'>%s</a>" % (remote_url, remote_url))
    else:
      self.write_tagged("Failure!\n%s: %s\n%s" % (http_resp.status, http_resp.reason, remote_data))


class store_profile_data(SimpleHandler):
  """View that stores profile data.
  """

  def post(self):
    """Get handler for the store view.
    """

    profile_key = self.request.get('key')
    path = self.request.get('path')
    email = self.request.get('user')
    version = self.request.get('version')

    status = "key='%s', path='%s', email='%s', version='%s'" % (
        profile_key, path, email, version)

    if not (profile_key and path and email and version):
      message = "Missing task parameters " + status
      logging.error(message)
      self.response.out.write(message)
      return

    cache_key = profiler.cache_key_for_profile(profile_key)
    data = mc_client.get(cache_key) if cache_key else None

    if not data:
      message = "Data removed from memcache " + status
      logging.debug(message)
      self.response.out.write(message)
      return

    user = users.User(email=email)

    storage.store(path, data, user, version)
    mc_client.delete(cache_key)

    self.response.out.write("Stored successfully")


application = webapp.WSGIApplication([
    ('/profiler/show', show_profile),
    ('/profiler/download', download_profile_data),
    ('/profiler/send', send_profile_data),
    ('/profiler/store', store_profile_data),
    ],
    debug=True)


def main():
    google.appengine.ext.webapp.util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

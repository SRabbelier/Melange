#!/usr/bin/env python
import sys
import os

HERE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..'))
appengine_location = os.path.join(HERE, 'thirdparty', 'google_appengine')
extra_paths = [HERE,
               os.path.join(appengine_location, 'lib', 'django'),
               os.path.join(appengine_location, 'lib', 'webob'),
               os.path.join(appengine_location, 'lib', 'yaml', 'lib'),
               appengine_location,
               os.path.join(HERE, 'app'),
               os.path.join(HERE, 'thirdparty', 'coverage'),
              ]

import nose
from nose import plugins

class AppEngineDatastoreClearPlugin(plugins.Plugin):
  """Nose plugin to clear the AppEngine datastore between tests.
  """
  name = 'AppEngineDatastoreClearPlugin'
  enabled = True
  def options(self, parser, env):
    return plugins.Plugin.options(self, parser, env)

  def configure(self, parser, env):
    plugins.Plugin.configure(self, parser, env)
    self.enabled = True

  def afterTest(self, test):
    from google.appengine.api import apiproxy_stub_map
    datastore = apiproxy_stub_map.apiproxy.GetStub('datastore')
    datastore.Clear()


def main():
  sys.path = extra_paths + sys.path
  os.environ['SERVER_SOFTWARE'] = 'Development via nose'
  os.environ['SERVER_NAME'] = 'Foo'
  os.environ['SERVER_PORT'] = '8080'
  os.environ['APPLICATION_ID'] = 'test-app-run'
  os.environ['USER_EMAIL'] = 'test@example.com'
  import main as app_main
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api import datastore_file_stub
  from google.appengine.api import mail_stub
  from google.appengine.api import user_service_stub
  from google.appengine.api import urlfetch_stub
  from google.appengine.api.memcache import memcache_stub
  apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
  apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',
                                          urlfetch_stub.URLFetchServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('user',
                                          user_service_stub.UserServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('datastore',
    datastore_file_stub.DatastoreFileStub('your_app_id', None, None))
  apiproxy_stub_map.apiproxy.RegisterStub('memcache',
    memcache_stub.MemcacheServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())
  import django.test.utils
  django.test.utils.setup_test_environment()
  nose.main(plugins=[AppEngineDatastoreClearPlugin(), ])


if __name__ == '__main__':
  main()

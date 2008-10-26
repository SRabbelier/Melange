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
              ]

import nose
import nosegae
from nose import config
from nose.plugins import manager

def main():
  sys.path = extra_paths + sys.path
  os.environ['SERVER_SOFTWARE'] = 'Development via nose'
  os.environ['SERVER_NAME'] = 'Foo'
  os.environ['SERVER_PORT'] = '8080'
  os.environ['APPLICATION_ID'] = 'test-app-run'
  import main as app_main
  from google.appengine.api import apiproxy_stub_map
  from google.appengine.api import datastore_file_stub
  from google.appengine.api import mail_stub
  from google.appengine.api import user_service_stub
  from google.appengine.api import urlfetch_stub
  apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
  apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',
                                          urlfetch_stub.URLFetchServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('user',
                                          user_service_stub.UserServiceStub())
  apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3',
    datastore_file_stub.DatastoreFileStub('your_app_id', '/dev/null',
                                          '/dev/null'))
  apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())
  nose.main(config=config.Config(files=config.all_config_files()))


if __name__ == '__main__':
  main()

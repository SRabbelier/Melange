#!/usr/bin/env python

#Copyright 2008 Adam A. Crossland
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import sys
import os.path

APPENGINE_PATH = '../../../../google/google_appengine'

# Add app-engine related libraries to your path
paths = [
    APPENGINE_PATH,
    os.path.join(APPENGINE_PATH, 'lib', 'django'),
    os.path.join(APPENGINE_PATH, 'lib', 'webob'),
    os.path.join(APPENGINE_PATH, 'lib', 'yaml', 'lib')
]
for path in paths:
  if not os.path.exists(path): 
    raise 'Path does not exist: %s' % path
sys.path = paths + sys.path

import unittest
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import user_service_stub
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api.memcache import memcache_stub
from taggable import *

APP_ID = u'taggable'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'me@example.com'  # set to '' for no logged in user

BLOG_NAME='test_blog'

class BlogIndex(db.Model):
    "A global counter used to provide the index of the next blog post."
    index = db.IntegerProperty(required=True, default=0)
    "The next available index for a Post."

class Post(Taggable, db.Model):
    index = db.IntegerProperty(required=True, default=0)
    body = db.TextProperty(required = True)
    title = db.StringProperty()
    added = db.DateTimeProperty(auto_now_add=True)
    added_month = db.IntegerProperty()
    added_year = db.IntegerProperty()
    edited = db.DateTimeProperty()
        
    def __init__(self, parent=None, key_name=None, app=None, **entity_values):
        db.Model.__init__(self, parent, key_name, app, **entity_values)
        Taggable.__init__(self)
        
    def get_all_posts():
        return db.GqlQuery("SELECT * from Post ORDER BY added DESC")
    Get_All_Posts = staticmethod(get_all_posts)
        
    @classmethod        
    def get_posts(cls, start_index=0, count=10):
        start_index = int(start_index) # Just make sure that we have an int
        posts = Post.gql('WHERE index <= :1 ORDER BY index DESC', start_index).fetch(count + 1)
        if len(posts) > count:
            posts = posts[:count]
            
        return posts

    @classmethod
    def new_post(cls, new_title=None, new_body=None, new_tags=[]):
        new_post = None
        if new_title is not None and new_body is not None:
            def txn():
                blog_index = BlogIndex.get_by_key_name(BLOG_NAME)
                if blog_index is None:
                    blog_index = BlogIndex(key_name=BLOG_NAME)
                new_index = blog_index.index
                blog_index.index += 1
                blog_index.put()
            
                new_post_key_name = BLOG_NAME + str(new_index)
                new_post = Post(key_name=new_post_key_name, parent=blog_index,
                               index = new_index, title = new_title,
                               body = new_body)
                new_post.put()
                
                return new_post
            new_post = db.run_in_transaction(txn)
        
            new_post.tags = new_tags
            new_post.put()
        else:
            raise Exception("Must supply both new_title and new_body when creating a new Post.")
        
        return new_post
    
    def delete(self):
        # Perform any actions that are required to maintain data integrity
        # when this Post is delete.
        # Disassociate this Post from any Tag
        self.set_tags([])
        
        # Finally, call the real delete
        db.Model.delete(self)

class MyTest(unittest.TestCase):

    def setUp(self):
      # Start with a fresh api proxy.
      apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

      # Use a fresh stub datastore.
      stub = datastore_file_stub.DatastoreFileStub(APP_ID, '/dev/null', '/dev/null')
      apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

      # Use a fresh memcache stub.
      apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())
        
      # Use a fresh stub UserService.
      apiproxy_stub_map.apiproxy.RegisterStub(
          'user', user_service_stub.UserServiceStub())
      os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
      os.environ['USER_EMAIL'] = LOGGED_IN_USER
      os.environ['APPLICATION_ID'] = APP_ID

    def testSimpleTagAdding(self):
      new_post = Post.new_post(new_title='test post 1', new_body='This is a test post.  Please ignore.')
      assert new_post is not None
        
      new_post.tags = "test, testing, tests"
      self.assertEqual(len(new_post.tags), 3)

    def testComplexTagAdding(self):
      new_post = Post.new_post(new_title='test post 1', new_body='This is a test post.  Please ignore.')
      assert new_post is not None
        
      new_post.tags = "  test, testing, tests,,,tag with spaces"
      self.assertEqual(len(new_post.tags), 4)

      tag = new_post.tags[3]
      assert tag is not None
      self.assertEqual(tag.tag, 'tag with spaces')
      self.assertEqual(tag.tagged_count, 1)

      tag2 = Tag.get_by_name('tag with spaces')
      assert tag2 is not None
      self.assertEqual(tag.tag, 'tag with spaces')
      self.assertEqual(tag.tagged_count, 1)

    def testTagDeletion(self):
      new_post = Post.new_post(new_title='test post 2', new_body='This is a test post.  Please continue to ignore.')
      assert new_post is not None
        
      new_post.tags = "test, testing, tests"
      self.assertEqual(len(new_post.tags), 3)

      new_post.tags = "test"
      self.assertEqual(len(new_post.tags), 1)

    def testTagCounts(self):
      new_post3 = Post.new_post(new_title='test post 3', new_body='This is a test post.  Please continue to ignore.')
      assert new_post3 is not None
      new_post3.tags = "foo, bar, baz"
      new_post4 = Post.new_post(new_title='test post 4', new_body='This is a test post.  Please continue to ignore.')
      assert new_post4 is not None
      new_post4.tags = "bar, baz, bletch"
      new_post5 = Post.new_post(new_title='test post 5', new_body='This is a test post.  Please continue to ignore.')
      assert new_post5 is not None
      new_post5.tags = "baz, bletch, quux"
      
      foo_tag = Tag.get_by_name('foo')
      assert foo_tag is not None
      self.assertEqual(foo_tag.tagged_count, 1)
      
      bar_tag = Tag.get_by_name('bar')
      assert bar_tag is not None
      self.assertEqual(bar_tag.tagged_count, 2)
      
      baz_tag = Tag.get_by_name('baz')
      assert baz_tag is not None
      self.assertEqual(baz_tag.tagged_count, 3)
      
      bletch_tag = Tag.get_by_name('bletch')
      assert bletch_tag is not None
      self.assertEqual(bletch_tag.tagged_count, 2)
      
      quux_tag = Tag.get_by_name('quux')
      assert quux_tag is not None
      self.assertEqual(quux_tag.tagged_count, 1)
      
      new_post3.tags = 'bar, baz'
      foo_tag = Tag.get_by_name('foo')
      assert foo_tag is not None
      self.assertEqual(len(new_post3.tags), 2)
      self.assertEqual(foo_tag.tagged_count, 0)
      
    def testTagGetTagsForKey(self):
      new_post = Post.new_post(new_title='test post 6', new_body='This is a test post.  Please continue to ignore.', new_tags='foo,bar,bletch,quux')
      assert new_post is not None

      tags = Tag.get_tags_for_key(new_post.key())
      assert tags is not None
      self.assertEqual(type(tags), type([]))
      self.assertEqual(len(tags), 4)
    
    def testTagGetByName(self):
      new_post = Post.new_post(new_title='test post 6', new_body='This is a test post.  Please continue to ignore.', new_tags='foo,bar,bletch,quux')
      assert new_post is not None

      quux_tag = Tag.get_by_name('quux')
      assert quux_tag is not None
      
      zizzle_tag = Tag.get_by_name('zizzle')
      assert zizzle_tag is None
      
    def testTagsString(self):
      new_post = Post.new_post(new_title='test post 6', new_body='This is a test post.  Please continue to ignore.', new_tags='  pal,poll ,,pip,pony')
      assert new_post is not None
      self.assertEqual(new_post.tags_string(), "pal,poll,pip,pony")
      new_post.tag_separator = "|"
      self.assertEqual(new_post.tags_string(), "pal|poll|pip|pony")
      new_post.tag_separator = " , "
      self.assertEqual(new_post.tags_string(), "pal , poll , pip , pony")
      
      new_post.tag_separator = ", "
      new_post.tags = "pal, pill, pip"
      self.assertEqual(len(new_post.tags), 3)
      self.assertEqual(new_post.tags_string(), "pal, pill, pip")
      
if __name__ == '__main__':
    unittest.main()

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

"""A script which produces a UML diagram from the data model found in the
models directory.

The output can be found in a file called model-map.png in the same directory as
this file.
"""

__authors__ = [
  '"Tim \'mithro\' Ansell" <mithro@mithis.com>',
]

import os
import os.path

from types import TypeType

import pygraphviz

import sys
# App Engine
sys.path.append(os.path.join("..", "thirdparty", "google_appengine"))
# Our app
sys.path.append(os.path.join("..", "app"))

def main(argv):
  import google.appengine.ext.db

  G = pygraphviz.AGraph()
  G.graph_attr['label'] = '-'

  import soc.models as models
  for file in os.listdir(os.path.dirname(models.__file__)):
    if not file.endswith(".py"):
      continue
    if "__init__" in file:
      continue

    modelname = os.path.basename(file)[:-3]
    try:
      #model = __import__("app.soc.models.%s" % modelname, fromlist=[modelname])
      exec("import soc.models.%s as model" % modelname)

      # Add the module to the graph
      for klassname in dir(model):
        klass = getattr(model, klassname)
        if not isinstance(klass, TypeType):
          continue

        # Create arrows to the parent classes
        for parent in klass.__bases__:
          G.add_edge(klassname, parent.__name__)
          edge = G.get_edge(klassname, parent.__name__)
          edge.attr['arrowhead'] = "empty"

        refs = ""
        attrs = ""
        for attrname in dir(klass):
          attr = getattr(klass, attrname)

          # Is it an appengine datastore type?
          if type(attr) in google.appengine.ext.db.__dict__.values():
            # References get arrows to the other class
            if isinstance(attr, google.appengine.ext.db.ReferenceProperty):
              hasa = attr.reference_class.__name__
              G.add_edge(hasa, klassname)
              edge = G.get_edge(hasa, klassname)
              edge.attr['arrowhead'] = 'inv'

              refs += "+ %s: %s\l" % (attrname, type(attr).__name__[:-8])
            
            # Ignore back references
            elif isinstance(attr, google.appengine.ext.db._ReverseReferenceProperty):
              pass
            else:
              # Check that the property is not inherited for a parent class
              local = True
              for parent in klass.__bases__:
                if hasattr(parent, attrname):
                  local = False

              if local:
                attrs += "+ %s: %s\l" % (attrname, type(attr).__name__[:-8])
        label = "{%s|%s|%s}" % (klassname, attrs, refs)

        G.add_node(klassname)
        node = G.get_node(klassname)
        node.attr['label'] = label
        node.attr['shape'] = "record"

    except Exception, e:
      import traceback
      print "Was unable to import %s: %s" % (modelname, e)
      traceback.print_exc()

  G.layout(prog='dot')
  G.draw('model-map.png')

if __name__ == "__main__":
  main(sys.argv)

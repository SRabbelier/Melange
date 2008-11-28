#!/usr/bin/env python
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

"""TODO(SRabbelier) Update __doc__ string
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import sys

import cPickle
import os
import graph


ROOTDIR = "soc"


def parseFile(file_name):
  if os.path.exists("imports.dat"):
    log = open("imports.dat", "r")
    all_imports = cPickle.load(log)
    log.close()
  else:
    all_imports = {}

  if file_name in all_imports:
    print "Overwriting previous data on '%s'." % file_name

  imports = []

  file = open(file_name)

  for line in file:
    if line.lstrip().startswith('import soc'):
      splitline = line[:-1].split(' ')
      mod = splitline[1]
      imports.append(mod)

    if line.lstrip().startswith('from soc'):
      splitline = line[:-1].split(' ')
      mod = splitline[1] + '.' + splitline[3]
      imports.append(mod)

  for idx, imp in enumerate(imports):
    if imp in set(imports[idx+1:]):
      sys.stderr.write("Warning: file '%s' has a redundant import: '%s'.\n" % (file_name, imp))

  if file_name.endswith("__init__.py"):
    normalized = file_name[:-12].replace('/', '.')
  else:
    normalized = file_name[:-3].replace('/', '.')

  print "Writing imports for file %s (%s)." % (file_name, normalized)
  all_imports[normalized] = imports

  log = open("imports.dat", "w")
  cPickle.dump(all_imports, log)
  log.close()

  return 0


def buildGraph():
  if not os.path.exists("imports.dat"):
    sys.stderr.write("Missing imports.dat file, run 'build' first\n")
    return

  log = open("imports.dat", "r")
  all_imports = cPickle.load(log)

  gr = graph.digraph()

  gr.add_nodes(all_imports.keys())

  for file_name, imports in all_imports.iteritems():
    for imp in imports:
      gr.add_edge(file_name, imp)

  return gr


def showGraph(gr):
  for node in gr:
    print "%s: " % node
    for edge in gr[node]:
      print "\t%s" % edge

  return 0


def getParents(gst, target):
  parents = []
  current = target

  while True:
    for node in gst:
      if current in gst[node]:
        parents.append(node)
        current = node
        break
    else:
      break

  return parents


def pathFrom(parents, first, target):
  idx = parents.index(first)
  path = parents[idx::-1]
  return [target] + path + [target]


def findCycle(gr, gst, target):
  parents = getParents(gst, target)
  cycles = []

  for node in gr[target]:
    if node in parents:
      cycles.append(pathFrom(parents, node, target))

  return cycles


def findCycles(gr):
  st, pre, post = gr.depth_first_search()
  gst = graph.digraph()
  gst.add_spanning_tree(st)

  cycles = []

  for node in gr:
    cycles += findCycle(gr, gst, node)

  return cycles


def drawGraph(gr):
  st, pre, post = gr.depth_first_search()
  gst = graph.digraph()
  gst.add_spanning_tree(st)

  sys.path.append('/usr/lib/graphviz/python/')
  import gv
  dot = gst.write(fmt='dot')
  gvv = gv.readstring(dot)
  gv.layout(gvv,'dot')
  gv.render(gvv,'png','imports.png')


def accumulate(arg, dirname, fnames):
  for fname in fnames:
    if not fname.endswith(".py"):
      continue

    arg.append(os.path.join(dirname, fname))


def main(args):
  if len(args) != 1:
    print "Supported options: 'print', 'build', 'find', and 'draw'."
    return -1

  action = args[0]

  if action == "build":
    fnames = []
    os.path.walk(ROOTDIR, accumulate, fnames)

    for fname in fnames:
      parseFile(fname)

    print "Done parsing."
    return 0

  gr = buildGraph()
  if not gr:
    return 1

  if action == "show":
    return showGraph(gr)

  if action == "draw":
    return drawGraph(gr)

  if action == "find":
    cycles = findCycles(gr)
    for cycle in cycles:
      print cycle
    return 0

  print "Unknown option."
  return -1


if __name__ == '__main__':
  import sys
  os.chdir("../app")
  res = main(sys.argv[1:])
  sys.exit(0)

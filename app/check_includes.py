#!/usr/bin/env python

import sys

import cPickle
import os
import graph

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
      print "Warning: file '%s' has a redundant import: '%s'." % (file_name, imp)

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
  import graph

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


def main(args):
  if len(args) == 1 and args[0].startswith("."):
    gr = buildGraph()
    if args[0] == '.':
      return showGraph(gr)

    if args[0] == '..':
      return drawGraph(gr)

    if args[0] == '...':
      cycles = findCycles(gr)
      for cycle in cycles:
        print cycle
      return 0

  if not args:
    print "Please specify a filename to parse, or '.' to list the parsed imports"
    return -1

  res = 0

  for file_name in args:
    res += parseFile(file_name)

  print "Done parsing."

  return res

if __name__ == '__main__':
  import sys
  res = main(sys.argv[1:])
  sys.exit(res)


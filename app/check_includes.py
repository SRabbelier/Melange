#!/usr/bin/env python

import sys
sys.path.append('/usr/lib/graphviz/python/')

import cPickle
import os
import graph
import gv

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

  normalized = "soc.%s" % file_name[:-3].replace('/', '.')

  print "Writing imports for file %s (%s)." % (file_name, normalized)
  all_imports[normalized] = imports

  log = open("imports.dat", "w")
  cPickle.dump(all_imports, log)
  log.close()

  return 0


def buildGraph():
  log = open("imports.dat", "r")
  all_imports = cPickle.load(log)

  gr = graph.graph()

  gr.add_nodes(all_imports.keys())

  for file_name, imports in all_imports.iteritems():
    for imp in imports:
      if imp not in gr:
        gr.add_node(imp)
      gr.add_edge(file_name, imp)

  return gr


def showGraph():
  gr = buildGraph()
  for node in gr:
    print "%s: " % node
    for edge in gr[node]:
      print "\t%s" % edge


def drawGraph():
  gr = buildGraph()
  dot = gr.write(fmt='dot')
  gvv = gv.readstring(dot)
  gv.layout(gvv,'dot')
  gv.render(gvv,'png','imports.png')


def main(args):
  if len(args) == 1:
    if args[0] == '.':
      return showGraph()

    if args[0] == '..':
      return drawGraph()

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


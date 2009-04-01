#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Starts an interactive shell with statistic helpers.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


import cPickle
import operator
import sys

import interactive


def addKey(target, fieldname):
  """Adds the key of the specified field.
  """

  result = target.copy()
  result['%s_key' % fieldname] = target[fieldname].key().name()
  return result

def getOrgs():
  """Returns all orgs as dictionary.
  """

  from soc.models.organization import Organization

  gen = lambda: Organization.all()
  it = interactive.deepFetch(gen)

  orgs = [(i.key().name(), i) for i in it]
  return dict(orgs)


def getProps():
  """Returns all proposals as a list of dictionaries.
  """

  key_order = [
      'link_id', 'scope_path', 'title', 'abstract', 'content',
      'additional_info', 'mentor', 'possible_mentors', 'score',
      'status', 'org']

  from soc.models.student_proposal import StudentProposal

  gen = lambda: StudentProposal.all()
  it = interactive.deepFetch(gen)

  proposals = [i.toDict(key_order) for i in it]

  return proposals


def orgstats(target):
  """Retrieves org stats.
  """

  from soc.logic import dicts

  target = [addKey(i, 'org') for i in target]
  grouped = dicts.groupby(target, 'org_key')
  popularity = [(k, len(v)) for k,v in grouped.iteritems()]

  return grouped, dict(popularity)


def printPopularity(popularity):
  """Prints the popularity for the specified proposals.
  """

  g = operator.itemgetter(1)

  for item in sorted(popularity.iteritems(), key=g, reverse=True):
    print "%s: %d" % item


def savePopularity(popularities):
  """Saves the specified popularities.
  """

  import logging
  from google.appengine.ext import db

  from soc.models.organization import Organization

  def txn(key_name, popularity):
    org = Organization.get_by_key_name(key_name)
    org.nr_applications = popularity
    org.put()

  for key, value in sorted(popularities.iteritems()):
    print key
    db.run_in_transaction_custom_retries(10, txn, key, value)

  print "done"


def loadPickle(name):
  """Loads a pickle.
  """

  f = open(name + '.dat')
  return cPickle.load(f)


def dumpPickle(target, name):
  """Dumps a pickle"
  """

  f = open("%s.dat" % name, 'w')
  cPickle.dump(target, f)


def main(args):
  """Main routine.
  """

  interactive.setup()

  context = {
      'load': loadPickle,
      'dump': dumpPickle,
      'orgstats': orgstats,
      'printPopularity': printPopularity,
      'savePopularity': savePopularity,
      'getOrgs': getOrgs,
      'getProps': getProps,
  }

  interactive.remote(args, context)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % (sys.argv[0],)
    sys.exit(1)

  main(sys.argv[1:])


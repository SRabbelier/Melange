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


def dateFetch(queryGen, last=None, batchSize=100):
  """Iterator that yields an entity in batches.

  Args:
    queryGen: should return a Query object
    last: used to .filter() for last_modified_on
    batchSize: how many entities to retrieve in one datastore call

  Retrieved from http://tinyurl.com/d887ll (AppEngine cookbook).
  """

  from google.appengine.ext import db

   # AppEngine will not fetch more than 1000 results
  batchSize = min(batchSize,1000)

  query = None
  done = False
  count = 0

  while not done:
    print count
    query = queryGen()
    query.order('last_modified_on')
    if last:
      query.filter("last_modified_on > ", last)
    results = query.fetch(batchSize)
    for result in results:
      count += 1
      yield result
    if batchSize > len(results):
      done = True
    else:
      last = results[-1].last_modified_on


def addKey(target, fieldname):
  """Adds the key of the specified field.
  """

  result = target.copy()
  result['%s_key' % fieldname] = target[fieldname].key().name()
  return result


def getEntities(model):
  """Returns all users as dictionary.
  """

  def wrapped():
    gen = lambda: model.all()
    it = interactive.deepFetch(gen)

    entities = [(i.key().name(), i) for i in it]
    return dict(entities)

  return wrapped


def getProps(last=None):
  """Returns all proposals as a list of dictionaries.
  """

  key_order = [
      'link_id', 'scope_path', 'title', 'abstract', 'content',
      'additional_info', '_mentor', 'possible_mentors', 'score',
      'status', '_org', 'created_on', 'last_modified_on']

  from soc.models.student_proposal import StudentProposal

  gen = lambda: StudentProposal.all()

  it = dateFetch(gen, last)

  proposals = [(i.key().name(), i.toDict(key_order)) for i in it]

  return dict(proposals)


def orgStats(target):
  """Retrieves org stats.
  """

  from soc.logic import dicts

  grouped = dicts.groupby(target.values(), '_org')
  popularity = [(k, len(v)) for k,v in grouped.iteritems()]

  return grouped, dict(popularity)


def countStudentsWithProposals():
  """Retrieves number of Students who have submitted at least one Student Proposal.
  """

  proposals = getStudentProposals()
  students = {}

  for proposal_key in proposals.keys():
    students[proposals[proposal_key].scope_path] = True

  return len(students)


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
  """Dumps a pickle.
  """

  f = open("%s.dat" % name, 'w')
  cPickle.dump(target, f)


def main(args):
  """Main routine.
  """

  interactive.setup()

  from soc.models.organization import Organization
  from soc.models.user import User
  from soc.models.student import Student
  from soc.models.mentor import Mentor
  from soc.models.org_admin import OrgAdmin

  context = {
      'load': loadPickle,
      'dump': dumpPickle,
      'orgStats': orgStats,
      'printPopularity': printPopularity,
      'savePopularity': savePopularity,
      'getOrgs': getEntities(Organization),
      'getUsers': getEntities(User),
      'getStudents': getEntities(Student),
      'getMentors': getEntities(Mentor),
      'getOrgAdmins': getEntities(OrgAdmin),
      'getProps': getProps,
      'countStudentsWithProposals': countStudentsWithProposals,
  }

  interactive.remote(args, context)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % (sys.argv[0],)
    sys.exit(1)

  main(sys.argv[1:])


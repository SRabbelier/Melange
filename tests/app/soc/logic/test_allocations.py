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


__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from soc.logic import allocations


class Student(object):
  """Mocker for Student object.
  """

  def __init__(self, id):
    """Simple init that stores id for later use.
    """

    self.id = id

  def __eq__(self, other):
    """Simple eq that compares ids.
    """

    return self.id == other.id

  def __str__(self):
    """Simple str that returns str(id).
    """

    return str(self.id)

  def __repr__(self):
    """Simple repr that returns repr(id).
    """

    return repr(self.id)


class AllocationsTest(unittest.TestCase):
  """Tests related to the slot allocation algorithm.
  """

  def setUp(self):
    """Set up required for the slot allocation tests.
    """

    self.slots = 60
    self.max_slots_per_org = 40
    self.min_slots_per_org = 2
    self.allocated = 0
    self.algorithm = 2

    apps = {
        'asf': (20, 20),
        'gcc': (15, 50),
        'git': (6, 6),
        'google': (3, 10),
        'melange': (100, 3),
        }

    self.popularity = dict([(k,a) for k, (a, m) in apps.iteritems()])
    self.mentors = dict([(k,m) for k, (a, m) in apps.iteritems()])

    self.orgs = self.popularity.keys()

    self.allocater = allocations.Allocator(
        self.orgs, self.popularity, self.mentors, self.slots,
        self.max_slots_per_org, self.min_slots_per_org, self.algorithm)

  def testInitialAllocation(self):
    """Test that an allocation with no arguments does not crash.
    """

    locked_slots = {}
    adjusted_slots = {}
    self.allocater.allocate(locked_slots)

  def testLockedSlotsAllocation(self):
    """Test that an allocation with an org locked does not crash.
    """

    locked_slots = {'melange': 3}
    self.allocater.allocate(locked_slots)

  def testNonExistantOrgAllocation(self):
    """Test that locking a non-existing org errors out.
    """

    locked_slots = {'gnome': 1}
    self.failUnlessRaises(allocations.Error, self.allocater.allocate,
                          locked_slots)

  def testInitialAllocationBelowMaxSlots(self):
    """Test that the initial allocation is below the max slot count.
    """

    locked_slots = {}

    result = self.allocater.allocate(locked_slots)
    self.failIf(sum(result.values()) > self.slots)

  def testLockedAllocationCorrect(self):
    """Test that locking an allocation assigns the org the allocation.
    """

    locked_slots = {'git': 6}

    result = self.allocater.allocate(locked_slots)

    expected = 6
    actual = result['git']

    self.failUnlessEqual(expected, actual)

  def testOverassignedAllocationCorrect(self):
    """Test that over-assigned allocation are cut down.
    """

    locked_slots = {'git': 20}

    result = self.allocater.allocate(locked_slots)

    expected = 6
    actual = result['git']

    self.failUnlessEqual(expected, actual)

  def testAllOrgsLocked(self):
    """Test that when all orgs are locked the correct result is given.
    """

    locked_slots = {
        'asf': 20,
        'gcc': 15,
        'git': 6,
        'google': 3,
        'melange': 3,
        }

    result = self.allocater.allocate(locked_slots)
    self.failUnlessEqual(locked_slots, result)

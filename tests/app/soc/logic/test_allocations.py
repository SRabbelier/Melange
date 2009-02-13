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
    self.allocated = 0

    self.applications = {
        'asf': self.allocate(20),
        'gcc': self.allocate(15),
        'git': self.allocate(6),
        'google': self.allocate(3),
        'melange': self.allocate(100),
        }

    self.orgs = self.applications.keys()

    self.allocater = allocations.Allocator(self.orgs, self.applications,
                                           self.slots, self.max_slots_per_org)

  def allocate(self, count):
    """Returns a list with count new student objects.
    """

    i = self.allocated
    j = i + count
    self.allocated += count

    return [Student(i) for i in range(i,j)]

  def testAllocate(self):
    """Test that the allocate helper works properly.

    A meta-test, it never hurts to be certain.
    """

    stash = self.allocated
    self.allocated = 0

    expected = [Student(0), Student(1), Student(2)]
    actual = self.allocate(3)
    self.failUnlessEqual(expected, actual)

    expected = []
    actual = self.allocate(0)
    self.failUnlessEqual(expected, actual)

    expected = [Student(3)]
    actual = self.allocate(1)
    self.failUnlessEqual(expected, actual)

    self.allocated = stash

  def testInitialAllocation(self):
    """Test that an allocation with no arguments does not crash.
    """

    locked_slots = {}
    adjusted_slots = {}
    self.allocater.allocate(locked_slots, adjusted_slots)

  def testLockedSlotsAllocation(self):
    """Test that an allocation with an org locked does not crash.
    """

    locked_slots = {'melange': 3}
    adjusted_slots = {}
    self.allocater.allocate(locked_slots, adjusted_slots)

  def testAdjustedSlotsAllocation(self):
    """Test that an allocation with an org adjusted does not crash.
    """

    locked_slots = {}
    adjusted_slots = {'google': -1}
    self.allocater.allocate(locked_slots, adjusted_slots)

  def testInvalidSlotsAllocation(self):
    """Test that an allocation with an org locked and adjusted errors out.
    """

    locked_slots = {'git': 1}
    adjusted_slots = {'git': 1}
    self.failUnlessRaises(allocations.Error, self.allocater.allocate,
                          locked_slots, adjusted_slots)

  def testNonExistantOrgAllocation1(self):
    """Test that locking a non-existing org errors out.
    """

    locked_slots = {'gnome': 1}
    adjusted_slots = {}
    self.failUnlessRaises(allocations.Error, self.allocater.allocate,
                          locked_slots, adjusted_slots)

  def testNonExistantOrgAllocation2(self):
    """Test that adjusting a non-existing org errors out.
    """

    locked_slots = {}
    adjusted_slots = {'gnome': 1}
    self.failUnlessRaises(allocations.Error, self.allocater.allocate,
                          locked_slots, adjusted_slots)

  def testInitialAllocationBelowMaxSlots(self):
    """Test that the initial allocation is below the max slot count.
    """

    locked_slots = {}
    adjusted_slots = {}

    result = self.allocater.allocate(locked_slots, adjusted_slots)
    self.failIf(sum(result.values()) > self.slots)

  def testLockedAllocationCorrect(self):
    """Test that locking an allocation assigns the org the allocation.
    """

    locked_slots = {'git': 6}
    adjusted_slots = {}

    result = self.allocater.allocate(locked_slots, adjusted_slots)

    expected = 6
    actual = result['git']

    self.failUnlessEqual(expected, actual)

  def testOverassignedAllocationCorrect(self):
    """Test that over-assigned allocation are cut down.
    """

    locked_slots = {'git': 20}
    adjusted_slots = {}

    result = self.allocater.allocate(locked_slots, adjusted_slots)

    expected = 6
    actual = result['git']

    self.failUnlessEqual(expected, actual)

  def testAdjustedAllocationCorrect(self):
    """Test that locking an allocation assigns the org the allocation.
    """

    locked_slots = {}
    adjusted_slots = {'google': 1}

    with_adjusting = self.allocater.allocate(locked_slots, adjusted_slots)
    without_adjusting = self.allocater.allocate(locked_slots, {})

    expected = without_adjusting['google'] + 1
    actual = with_adjusting['google']

    self.failUnlessEqual(expected, actual)

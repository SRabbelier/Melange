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

"""Slot allocation logic.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import itertools
import math


class Error(Exception):
  """Error class for the Allocation module.
  """

  pass


class Allocator(object):
  """A simple student slots allocator.

  The buildSets method is used to validate the allocation data as well as
  construct the sets that the algorithm then uses to distribute the slots.
  By separating these steps it is possible to write a different allocation
  algorithm but re-use the sets and validation logic.
  """

  # I tried to write explicit code that does not require any
  # additional comments (with the exception of the set notation for
  # the convenience of any mathematicians that happen to read this
  # piece of code ;).

  def __init__(self, orgs, applications, mentors, slots,
               max_slots_per_org, min_slots_per_org, iterative):
    """Initializes the allocator.

    Args:
      orgs: a list of all the orgs that need to be allocated
      applications: a dictionary with for each org a list of applicants
      mentors: the amount of assigned mentors per org
      slots: the total amount of available slots
      max_slots_per_org: how many slots an org should get at most
      min_slots_per_org: how many slots an org should at least get
    """

    all_applications = []

    for _, value in applications.iteritems():
      all_applications += value
    
    self.locked_slots = {}
    self.adjusted_slots = {}
    self.adjusted_orgs = []
    self.locked_orgs = []
    self.unlocked_applications = []
    self.slots = slots
    self.max_slots_per_org = max_slots_per_org
    self.min_slots_per_org = min_slots_per_org
    self.orgs = set(orgs)
    self.applications = applications
    self.mentors = mentors
    self.all_applications = set(all_applications)
    self.iterative = iterative

  def allocate(self, locked_slots, adjusted_slots):
    """Allocates the slots and returns the result.

    Args:
      locked_slots: a dict with orgs and the number of slots they get
      adjusted_slots: a dict with orgs and the number of extra slots they get
    """

    self.locked_slots = locked_slots
    self.adjusted_slots = adjusted_slots

    self.buildSets()

    return self.iterativeAllocation()

  def buildSets(self):
    """Allocates slots with the specified constraints
    """

    # set s
    all_applications = self.all_applications
    locked_slots = self.locked_slots
    adjusted_slots = self.adjusted_slots

    # set a and b
    locked_orgs = set(locked_slots.keys())
    adjusted_orgs = set(adjusted_slots.keys())

    # set a' and b'
    unlocked_orgs = self.orgs.difference(locked_orgs)
    # unadjusted_orgs = self.orgs.difference(adjusted_orgs)

    # set a*b and a'*b'
    locked_and_adjusted_orgs = locked_orgs.intersection(adjusted_orgs)
    
    # unlocked_and_unadjusted_orgs = unlocked_orgs.intersection(unadjusted_orgs)

    # a+o and b+o should be o
    locked_orgs_or_orgs = self.orgs.union(locked_orgs)
    adjusted_orgs_or_orgs = self.orgs.union(adjusted_orgs)

    # an item can be only a or b, so a*b should be empty
    if locked_and_adjusted_orgs:
      raise Error("Cannot have an org locked and adjusted")

    # a+o should be o, testing length is enough though
    if len(locked_orgs_or_orgs) != len(self.orgs):
      raise Error("Unknown org as locked slot")

    # same for b+o
    if len(adjusted_orgs_or_orgs) != len(self.orgs):
      raise Error("Unknown org as adjusted slot")

    # set l and l'
    locked_applications = set(itertools.chain(*locked_slots.keys()))
    unlocked_applications = all_applications.difference(locked_applications)

    self.adjusted_orgs = adjusted_orgs
    self.unlocked_orgs = unlocked_orgs
    self.locked_orgs = locked_orgs
    self.unlocked_applications = unlocked_applications

    popularity = ((k, len(v)) for k, v in self.applications.iteritems())
    self.popularity = dict(popularity)

  def iterativeAllocation(self):
    """A simple iterative algorithm.
    """

    adjusted_orgs = self.adjusted_orgs
    adjusted_slots = self.adjusted_slots
    locked_orgs = self.locked_orgs
    locked_slots = self.locked_slots
    unlocked_applications = self.unlocked_applications

    unlocked_applications_count = len(unlocked_applications)
    unallocated_applications_count = unlocked_applications_count

    available_slots = self.slots
    allocations = {}

    for org in self.orgs:
      org_applications = self.applications[org]
      org_applications_count = len(org_applications)
      mentors = self.mentors[org]

      if org in locked_orgs:
        slots = locked_slots[org]
      else:
        weight = float(org_applications_count) / unallocated_applications_count
        slots = int(math.floor(weight*available_slots))

      if org in adjusted_orgs:
        slots += adjusted_slots[org]

      slots = min(slots, self.max_slots_per_org)
      slots = min(slots, mentors)
      slots = min(slots, available_slots)

      allocations[org] = slots
      available_slots -= slots
      unallocated_applications_count -= org_applications_count

    return allocations

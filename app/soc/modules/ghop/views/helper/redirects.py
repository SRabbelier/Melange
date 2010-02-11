#!/usr/bin/env python2.5
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

"""Redirect related methods.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


def getAssignTaskQuotasRedirect(entity, params):
  """Returns the assign task quotas redirect for the specified entity.
  """

  return'/%s/assign_task_quotas/%s' % (
      params['url_name'], entity.key().id_or_name())


def getSuggestTaskRedirect(entity, params):
  """Returns the suggest task redirect for the task for mentors.
  """

  return '/%s/suggest_task/%s' % (
      params['url_name'], entity.key().id_or_name())


def getListTasksRedirect(entity, params):
  """Returns the redirect for the List of tasks page for
  the given Org entity and Org View params.
  """

  result = '/%s/list_org_tasks/%s' % (
      params['url_name'], entity.key().id_or_name())

  return result


def getListStudentTasksRedirect(entity, params):
  """Returns the redirect for the List Student Tasks page for the given entity.
  """

  result = '/%s/list_student_tasks/%s' % (
      params['url_name'], entity.key().id_or_name())

  return result


def getDifficultyEditRedirect(entity, params):
  """Returns the task difficulty levels edit redirect for the specified entity.
  """

  return'/%s/task_difficulty/%s' % (
      params['url_name'], entity.key().id_or_name())


def getTaskTypeEditRedirect(entity, params):
  """Returns the task type tags edit redirect for the specified entity.
  """

  return'/%s/task_type/%s' % (
      params['url_name'], entity.key().id_or_name())

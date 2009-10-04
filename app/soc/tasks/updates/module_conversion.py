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

"""The module conversion updates are defined in this module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django.http import HttpResponse

from soc.logic.models.mentor import logic as mentor_logic
from soc.logic.models.org_admin import logic as org_admin_logic
from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.review import logic as review_logic
from soc.logic.models.student import logic as student_logic
from soc.logic.models.student_project import logic as student_project_logic
from soc.tasks.helper import decorators
from soc.tasks.helper import error_handler


# batch size to use when going through the entities
DEF_BATCH_SIZE = 10


def startUpdateWithUrl(request, task_url):
  """Spawns an update task for the given task URL.

  Args:
    request: Django Request object
    task_url: The URL used to run this update task

  Returns:
    True iff the new task is successfully added to the Task Queue API
  """

  new_task = taskqueue.Task(url=task_url)
  new_task.add()

  return True


@decorators.iterative_task(program_logic)
def runProgramConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts Programs into GSoCPrograms.

  Args:
    request: Django Request object
    entities: list of Program entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.models.program import GSoCProgram

  # get all the properties that are part of each Programs
  program_model = program_logic.getModel()
  program_properties = program_model.properties().keys()

  # use this to store all the new GSoCPrograms
  gsoc_programs = []

  for entity in entities:
    gsoc_properties = {}

    for program_property in program_properties:
      # copy over all the information from the program entity
      gsoc_properties[program_property] = getattr(entity, program_property)

    # create the new GSoCProgram entity and prepare it to be stored
    gsoc_program_entity = GSoCProgram(key_name=entity.key().name(),
                                      **gsoc_properties)
    gsoc_programs.append(gsoc_program_entity)

  # store all the new GSoCPrograms
  db.put(gsoc_programs)

  # task completed, return
  return


@decorators.iterative_task(org_logic)
def runOrgConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts Organizations into GSoCOrganizations.

  Args:
    request: Django Request object
    entities: list of Organization entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
  from soc.modules.gsoc.models.organization import GSoCOrganization

  # get all the properties that are part of each Organization
  org_model = org_logic.getModel()
  org_properties = org_model.properties().keys()

  # use this to store all the new GSoCOrganization
  gsoc_orgs = []

  for entity in entities:
    gsoc_properties = {}

    for org_property in org_properties:
      # copy over all the information from the Organization entity
      gsoc_properties[org_property] = getattr(entity, org_property)

    # get the Program key belonging to the old Organization
    program_key = entity.scope.key().id_or_name()
    # get the new GSoCProgram and set it as scope for the GSoCOrganzation
    gsoc_program = gsoc_program_logic.getFromKeyName(program_key)
    gsoc_properties['scope'] = gsoc_program

    # create the new GSoCOrganization entity and prepare it to be stored
    gsoc_org_entity = GSoCOrganization(key_name=entity.key().name(),
                                       **gsoc_properties)
    gsoc_orgs.append(gsoc_org_entity)

  # store all the new GSoCOrganizations
  db.put(gsoc_orgs)

  # task completed, return
  return


@decorators.iterative_task(org_admin_logic)
def runOrgAdminConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts OrgAdmins into GSoCOrgAdmins.

  Args:
    request: Django Request object
    entities: list of OrgAdmin entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin

  return _runOrgRoleConversionUpdate(entities, org_admin_logic, GSoCOrgAdmin)


@decorators.iterative_task(mentor_logic)
def runMentorConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts Mentors into GSoCMentors.

  Args:
    request: Django Request object
    entities: list of Mentor entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.models.mentor import GSoCMentor

  return _runOrgRoleConversionUpdate(entities, mentor_logic, GSoCMentor)


def _runOrgRoleConversionUpdate(entities, from_role_logic, to_role_model):
  """AppEngine Task that converts a normal Organization Role into a
  GSoCOrganization Role.

  Args:
    entities: Role entities to convert
    from_role_logic: the Role Logic instance where to convert from
    to_role_model: the role Model class where to convert to
  """

  from soc.modules.gsoc.logic.models.organization import logic as \
      gsoc_org_logic
  from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic

  # get all the properties that are part of each Organization's Role
  role_model = from_role_logic.getModel()
  role_properties = role_model.properties().keys()

  # use this to store all the new Roles
  gsoc_roles = []

  for entity in entities:
    gsoc_properties = {}

    for role_property in role_properties:
      # copy over all the information from the Role entity
      gsoc_properties[role_property] = getattr(entity, role_property)

    # get the Program key belonging to the old Role
    program_key = entity.program.key().id_or_name()
    # get the new GSoCProgram and set it for the Role
    gsoc_program = gsoc_program_logic.getFromKeyName(program_key)
    gsoc_properties['program'] = gsoc_program

    # get the Organization key belonging to the old Role
    org_key = entity.scope.key().id_or_name()
    # get the new GSoCOrganization and set it as scope for the Role
    gsoc_org = gsoc_org_logic.getFromKeyName(org_key)
    gsoc_properties['scope'] = gsoc_org

    # create the new GSoC Role entity and prepare it to be stored
    gsoc_role_entity = to_role_model(key_name=entity.key().name(),
                                        **gsoc_properties)
    gsoc_roles.append(gsoc_role_entity)

  # store all the new GSoC Roles
  db.put(gsoc_roles)

  # task completed, return
  return


@decorators.iterative_task(student_logic)
def runStudentConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts Students into GSoCStudents.

  Args:
    request: Django Request object
    entities: list of Student entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
  from soc.modules.gsoc.models.student import GSoCStudent

  # get all the properties that are part of each Student
  student_model = student_logic.getModel()
  student_properties = student_model.properties().keys()

  # use this to store all the new GSoCStudents
  gsoc_students = []

  for entity in entities:
    gsoc_properties = {}

    for student_property in student_properties:
      # copy over all the information from the Student entity
      gsoc_properties[student_property] = getattr(entity, student_property)

    # get the Program key belonging to the old Student
    program_key = entity.scope.key().id_or_name()
    # get the new GSoCProgram and set it as scope for the GSoCStudent
    gsoc_program = gsoc_program_logic.getFromKeyName(program_key)
    gsoc_properties['scope'] = gsoc_program

    # create the new GSoCStudent entity and prepare it to be stored
    gsoc_student_entity = GSoCStudent(key_name=entity.key().name(),
                                      **gsoc_properties)
    gsoc_students.append(gsoc_student_entity)

  # store all the new GSoCStudents
  db.put(gsoc_students)

  # task completed, return
  return


@decorators.iterative_task(review_logic)
def runReviewUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates Review entities.

  Args:
    request: Django Request object
    entities: list of Review entities to update
    context: the context of this task
  """

  for entity in entities:
    entity.reviewer = None

  # store all Reviews
  db.put(entities)

  # task completed, return
  return


@decorators.iterative_task(student_project_logic)
def runStudentProjectUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates StudentProject entities.

  Args:
    request: Django Request object
    entities: list of StudentProject entities to update
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
  from soc.modules.gsoc.logic.models.organization import logic as org_logic
  from soc.modules.gsoc.logic.models.program import logic as program_logic
  from soc.modules.gsoc.logic.models.student import logic as student_logic

  for entity in entities:
    entity.scope = org_logic.getFromKeyName(entity.scope.key().id_or_name())
    entity.mentor = mentor_logic.getFromKeyName(
        entity.mentor.key().id_or_name())
    entity.student = student_logic.getFromKeyName(
        entity.student.key().id_or_name())
    entity.program = program_logic.getFromKeyName(
        entity.program.key().id_or_name())

    old_mentors = entity.additional_mentors
    new_mentors = []

    for old_mentor in old_mentors:
      new_mentors.append(
        mentor_logic.getFromKeyName(old_mentor.id_or_name()))

    entity.additional_mentors = new_mentors

  # store all StudentProjects
  db.put(entities)

  # task completed, return
  return

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

"""The module conversion updates are defined in this module.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django.http import HttpResponse

from soc.logic.models.survey import logic as survey_logic
from soc.logic.models.survey_record import logic as record_logic
from soc.logic.models.document import logic as document_logic
from soc.logic.models.mentor import logic as mentor_logic
from soc.logic.models.org_admin import logic as org_admin_logic
from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.student import logic as student_logic
from soc.logic.models.timeline import logic as timeline_logic

from soc.tasks.helper import decorators
from soc.tasks.helper import error_handler

from soc.modules.gsoc.logic.models.survey import grading_logic as \
    grading_survey_logic
from soc.modules.gsoc.logic.models.survey import project_logic as \
    project_survey_logic
from soc.modules.gsoc.logic.models.survey_record import grading_logic as \
    grading_record_logic
from soc.modules.gsoc.logic.models.survey_record import project_logic as \
    project_record_logic
from soc.modules.gsoc.logic.models.grading_survey_group import logic as \
    grading_survey_group_logic
from soc.modules.gsoc.logic.models.review import logic as review_logic
from soc.modules.gsoc.logic.models.student_project import logic as \
    student_project_logic
from soc.modules.gsoc.logic.models.student_proposal import logic as \
    student_proposal_logic

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

  Also updates the RankerRoots that are associated with the Organization.

  Args:
    request: Django Request object
    entities: list of Organization entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
  from soc.modules.gsoc.logic.models.ranker_root import logic as \
      ranker_root_logic
  from soc.modules.gsoc.models.organization import GSoCOrganization

  # get all the properties that are part of each Organization
  org_model = org_logic.getModel()
  org_properties = org_model.properties().keys()

  # use this to store all the new GSoCOrganization
  gsoc_orgs = []
  gsoc_rankers = []

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

    # retrieve the RankerRoots belonging to the Organization
    fields = {'scope': entity}
    rankers = ranker_root_logic.getForFields(fields)

    for ranker in rankers:
      ranker.scope = gsoc_org_entity
      # append the adjusted ranker
      gsoc_rankers.append(ranker)

  # store all the new GSoCOrganizations
  db.put(gsoc_orgs)
  # store all the new rankers
  db.put(gsoc_rankers)

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


@decorators.iterative_task(student_proposal_logic)
def runStudentProposalUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates StudentProposal entities.

  Args:
    request: Django Request object
    entities: list of StudentProposal entities to update
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
  from soc.modules.gsoc.logic.models.organization import logic as org_logic
  from soc.modules.gsoc.logic.models.program import logic as program_logic
  from soc.modules.gsoc.logic.models.student import logic as student_logic

  for entity in entities:
    entity.scope = student_logic.getFromKeyName(
        entity.scope.key().id_or_name())
    entity.org = org_logic.getFromKeyName(entity.org.key().id_or_name())
    entity.program = program_logic.getFromKeyName(
        entity.program.key().id_or_name())

    if entity.mentor:
      entity.mentor = mentor_logic.getFromKeyName(
          entity.mentor.key().id_or_name())

    old_mentors = entity.possible_mentors
    new_mentors = []

    for old_mentor in old_mentors:
      new_mentor = mentor_logic.getFromKeyName(old_mentor.id_or_name())
      new_mentors.append(new_mentor.key())

    entity.possible_mentors = new_mentors

  # store all StudentProposal
  db.put(entities)

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
      new_mentor = mentor_logic.getFromKeyName(old_mentor.id_or_name())
      new_mentors.append(new_mentor.key())

    entity.additional_mentors = new_mentors

  # store all StudentProjects
  db.put(entities)

  # task completed, return
  return


@decorators.iterative_task(survey_logic)
def runSurveyUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates Survey entities.

  Args:
    request: Django Request object
    entities: list of Survey entities to update
    context: the context of this task
  """

  return _runSurveyUpdate(entities, survey_logic)


@decorators.iterative_task(project_survey_logic)
def runProjectSurveyUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates ProjectSurvey entities.

  Args:
    request: Django Request object
    entities: list of ProjectSurvey entities to update
    context: the context of this task
  """

  return _runSurveyUpdate(entities, project_survey_logic)


@decorators.iterative_task(grading_survey_logic)
def runGradingProjectSurveyUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates GradingProjectSurvey entities.

  Args:
    request: Django Request object
    entities: list of GradingProjectSurvey entities to update
    context: the context of this task
  """

  return _runSurveyUpdate(entities, grading_survey_logic)


def _runSurveyUpdate(entities, logic):
  """AppEngine Task that updates Survey entities.

  Args:
    entities: list of Survey entities to update
    logic: concrete logic instance which the surveys are to be updated for

  Returns:
    A list of pairs that maps the old surveys with the corresponding new ones.
  """

  from soc.modules.gsoc.logic.models.program import logic as program_logic

  # get all the properties that are part of each Document
  survey_model = logic.getModel()
  survey_properties = survey_model.properties().keys()

  new_surveys = []

  for entity in entities:
    new_survey_properties = {}

    for survey_property in survey_properties:
      # copy over all the information from the Survey entity
      new_survey_properties[survey_property] = getattr(entity,
                                                       survey_property)

    new_survey_properties['prefix'] = 'gsoc_program'
    new_survey_properties['scope'] = program_logic.getFromKeyName(
        entity.scope.key().id_or_name())

    new_survey_key = logic.getKeyNameFromFields(new_survey_properties)
    new_survey = survey_model(key_name=new_survey_key, **new_survey_properties)

    # force the prefix to gsoc_program before saving it for storage
    new_survey.prefix = 'gsoc_program'

    new_surveys.append(new_survey)

  # batch put the new Surveys
  db.put(new_surveys)

  # task completed, return
  return


@decorators.iterative_task(record_logic)
def runSurveyRecordUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates ProjectSurveyRecord entities.

  Args:
    request: Django Request object
    entities: list of SurveyRecord entities to update
    context: the context of this task
  """

  return _runSurveyRecordUpdate(entities, survey_logic)


@decorators.iterative_task(project_record_logic)
def runProjectSurveyRecordUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates ProjectSurveyRecord entities.

  Args:
    request: Django Request object
    entities: list of ProjectSurveyRecord entities to update
    context: the context of this task
  """

  entities = _runSurveyRecordUpdate(entities, project_survey_logic)

  return _runOrgSurveyRecordUpdate(entities)


@decorators.iterative_task(grading_record_logic)
def runGradingProjectSurveyRecordUpdate(request, entities, context, *args, 
                                        **kwargs):
  """AppEngine Task that updates GradingProjectSurveyRecord entities.

  Args:
    request: Django Request object
    entities: list of GradingProjectSurveyRecord entities to update
    context: the context of this task
  """

  entities = _runSurveyRecordUpdate(entities, grading_survey_logic)

  return _runOrgSurveyRecordUpdate(entities)


def _runSurveyRecordUpdate(entities, survey_logic):
  """AppEngine Task that updates SurveyRecord entities.

  Args:
    entities: list of SurveyRecord entities to update
    survey_logic: survey specific logic to get a new survey reference
  """

  cached_surveys = {}

  for entity in entities:

    # update only the entities which has 'program' prefix
    if not entity.survey.prefix == 'program':
      continue

    survey_key_name = 'gsoc_' + entity.survey.key().id_or_name()
    survey_entity = cached_surveys.get(survey_key_name)

    if not survey_entity:
      survey_entity = survey_logic.getFromKeyName(survey_key_name)
      cached_surveys[survey_key_name] = survey_entity

    entity.survey = survey_entity

  db.put(entities)

  # task completed, return
  return entities


def _runOrgSurveyRecordUpdate(entities):
  """AppEngine Task that updates SurveyRecord entities which refer to
  an organization. In particular, these are GradingProjectSurvey and
  ProjectSurvey records.

  Args:
    entities: list of SurveyRecord entities to update
  """

  from soc.modules.gsoc.logic.models.organization import logic as org_logic

  cached_orgs = {}

  for entity in entities:
    org_key_name = entity.org.key().id_or_name()
    org_entity = cached_orgs.get(org_key_name)

    if not org_entity:
      org_entity = org_logic.getFromKeyName(org_key_name)
      cached_orgs[org_key_name] = org_entity

    entity.org = org_entity

  db.put(entities)

  # task completed, return
  return entities


@decorators.iterative_task(grading_survey_group_logic)
def runGradingSurveyGroupUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates GradingSurveyGroup entities.

  Args:
    request: Django Request object
    entities: list of Document entities to update
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.program import logic as program_logic

  for entity in entities:
    entity.scope = program_logic.getFromKeyName(
        entity.scope.key().id_or_name())

    survey_attrs = ['grading_survey', 'student_survey']
    for survey_attr in survey_attrs:
      survey = getattr(entity, survey_attr)

      # update if the survey field is defined and its prefix is 'program'
      if not survey or not survey.prefix == 'program':
        continue

      survey_key_name = 'gsoc_' + survey.key().id_or_name()

      if survey_attr == 'student_survey':
        logic = project_survey_logic
      else:
        logic = grading_survey_logic

      new_survey = logic.getFromKeyName(survey_key_name)
      setattr(entity, survey_attr, new_survey)

  db.put(entities)

  # task completed, return
  return


@decorators.iterative_task(document_logic)
def runDocumentUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that updates Document entities.

  Args:
    request: Django Request object
    entities: list of Document entities to update
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.organization import logic as org_logic
  from soc.modules.gsoc.logic.models.program import logic as program_logic

  # get all the properties that are part of each Document
  document_model = document_logic.getModel()
  document_properties = document_model.properties().keys()

  # use this to store all the new Documents and Presences
  documents = []
  presences = []

  for entity in entities:

    if entity.prefix not in ['org', 'program']:
      # we do not want to convert this Document
      continue

    new_document_properties = {}

    for document_property in document_properties:
      # copy over all the information from the Document entity
      new_document_properties[document_property] = getattr(entity,
                                                           document_property)

    if entity.prefix == 'org':
      new_document_prefix = 'gsoc_org'
      presence_entity = org_logic.getFromKeyName(entity.scope_path)
    elif entity.prefix == 'program':
      new_document_prefix = 'gsoc_program'
      presence_entity = program_logic.getFromKeyName(entity.scope_path)

    new_document_properties['prefix'] = new_document_prefix
    new_document_properties['scope'] = presence_entity
    new_document_properties['home_for'] = presence_entity if entity.home_for else None

    # create the new Document entity and prepare it to be stored
    new_document_entity = document_model(
        key_name=document_logic.getKeyNameFromFields(new_document_properties),
        **new_document_properties)
    documents.append(new_document_entity)

    if entity.home_for:
      # update the presence for which this document was the home page
      presence_entity.home = new_document_entity
      presences.append(presence_entity)

  # store all the new Documents and updated Presences
  db.put(documents)
  db.put(presences)

  # task completed, return
  return


@decorators.iterative_task(timeline_logic)
def runTimelineConversionUpdate(request, entities, context, *args, **kwargs):
  """AppEngine Task that converts Timelines into GSoCTimelines.

  It also updates all GSoCPrograms with a reference to the new GSoCTimeline.

  Args:
    request: Django Request object
    entities: list of Timeline entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.models.timeline import GSoCTimeline
  from soc.modules.gsoc.logic.models.program import logic as program_logic

  # get all the properties that are part of each Timeline
  timeline_model = timeline_logic.getModel()
  timeline_properties = timeline_model.properties().keys()

  # use this to store all the new GSoCTimelines and GSoCPrograms
  gsoc_timelines = []
  gsoc_programs = []

  for entity in entities:
    gsoc_properties = {}

    for timeline_property in timeline_properties:
      # copy over all the information from the timeline entity
      gsoc_properties[timeline_property] = getattr(entity, timeline_property)

    gsoc_program = program_logic.getFromKeyName(entity.key().id_or_name())
    gsoc_properties['scope'] = gsoc_program.scope

    # create the new GSoCTimeline entity and prepare it to be stored
    gsoc_timeline_entity = GSoCTimeline(key_name=entity.key().name(),
                                        **gsoc_properties)
    gsoc_timelines.append(gsoc_timeline_entity)

    # set the timeline for the GSoCProgram entity and prepare it for storage
    gsoc_program.timeline = gsoc_timeline_entity
    gsoc_programs.append(gsoc_program)

  # store all the new GSoCTimelines and GSoCPrograms
  db.put(gsoc_timelines)
  db.put(gsoc_programs)

  # task completed, return
  return

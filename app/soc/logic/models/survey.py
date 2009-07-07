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

"""Survey (Model) query functions.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging

from google.appengine.ext import db

from soc.cache import sidebar
from soc.logic.models import linkable as linkable_logic
from soc.logic.models import survey_record as survey_record_logic
from soc.logic.models.user import logic as user_logic
from soc.logic.models import work
from soc.models.program import Program
from soc.models import student_project
from soc.models.survey import Survey
from soc.models.grading_project_survey import GradingProjectSurvey
from soc.models.grading_record import GradingRecord
from soc.models.project_survey import ProjectSurvey
from soc.models.survey import SurveyContent
from soc.models.survey_record import SurveyRecord
from soc.models.work import Work

#TODO(James): Ensure this facilitates variable # of surveys 
GRADES = {'pass': True, 'fail': False}
PROJECT_STATUSES = {
'accepted': {True: 'mid_term_passed', False: 'mid_term_failed'},
'mid_term_passed': {True: 'passed', False: 'final_failed'}
}

class Logic(work.Logic):
  """Logic methods for the Survey model.
  """

  def __init__(self, model=Survey, base_model=Work,
               scope_logic=linkable_logic,
               record_logic=survey_record_logic.logic):
    """Defines the name, key_name and model for this entity.

    params:
      record_logic: SurveyRecordLogic (or subclass) instance for this Survey
    """

    self.record_logic = record_logic

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def createSurvey(self, survey_fields, schema, survey_content=False):
    """Create a new survey from prototype.

    params:
      survey_fields = dict of survey field items (see SurveyContent model)
      schema = metadata about survey fields (SurveyContent.schema)
      survey_content = existing SurveyContent entity
    """

    if not survey_content:
      survey_content = SurveyContent()
    else:
      # wipe clean existing dynamic properties if they exist
      for prop in survey_content.dynamic_properties():
        delattr(survey_content, prop)

    for name, value in survey_fields.items():
      setattr(survey_content, name, value)

    survey_content.schema = str(schema)

    db.put(survey_content)

    return survey_content

  def getSurveyForContent(self, survey_content):
    """Returns the Survey belonging to the given SurveyContent.

    params:
      survey_content: the SurveyContent to retrieve the Survey for.

    returns:
      Survey or subclass if possible else None.
    """

    fields = {'survey_content': survey_content}

    return self.getForFields(fields, unique=True)

  def getRecordLogic(self):
    """Returns SurveyRecordLogic that belongs to this SurveyLogic.
    """

    return self.record_logic

  def getUserRole(self, user, survey, project):
    """Gets the role of a user for a project, used for SurveyRecordGroup.

    params:
      user: user taking survey
      survey: survey entity
      project: student project for this user
    """

    if survey.taking_access == 'mentor evaluation':
      mentors = self.getMentorforProject(user, project)

      if len(mentors) < 1 or len(mentors) > 1:
        logging.warning('Unable to determine mentor for \
        user %s. Results returned: %s ' % (
        user.key().name(), str(mentors)) )
        return False

      this_mentor = mentors[0]

    if survey.taking_access == 'student evaluation':
      students = self.getStudentforProject(user, project)

      if len(students) < 1 or len(students) > 1:
        logging.warning('Unable to determine student for \
        user %s. Results returned: %s ' % (
        user.key().name(), str(students)) )
        return False

  def getStudentforProject(self, user, project):
    """Get student projects for a given User.

    params:
      user = survey taking user
      project = survey taker's student project
    """
    from soc.logic.models.student import logic as student_logic
    import soc.models.student

    # TODO this should be done per Student or Program
    # TODO filter for accepted, midterm_passed, etc?
    user_students = student_logic.getForFields({'user': user}) 
    if not user_students: return []
    return set([project.student for project in sum(
    (list(s.student_projects.run())
    for s in user_students), []) if project.key() == project.key()])

  def getMentorforProject(self, user, project):
    """Get Student Projects that are being mentored by the given User.

    params:
      user = survey taking user
      project = survey taker's student project
    """

    from soc.logic.models.mentor import logic as mentor_logic
    import soc.models.mentor

    # TODO filter for accepted, midterm_passed, etc?
    # TODO this should be done a program basis not user

    user_mentors = mentor_logic.getForFields({'user': user}) 

    if not user_mentors:
      return []

    return set([project.mentor for project in sum(
            (list(mentor.student_projects.run())
             for mentor in user_mentors), [])
        if project.key() == project.key()])

  def activateGrades(self, survey):
    """Activates the grades on a Grading Survey.

    TODO(James) Fix this Docstring

    params:
      survey = survey entity
    """
    if survey.taking_access != "mentor evaluation":
      logging.error("Cannot grade survey %s with taking access %s"
      % (survey.key().name(), survey.taking_access))
      return False

    program = survey.scope or Program.get_by_key_name(survey.scope_path)

    for project in program.student_projects.fetch(1000):
      this_record_group = GradingRecord.all().filter(
      "project = ", project).filter(
      "initial_status = ", project.status).get()

      if not this_record_group:
         logging.warning('neither mentor nor student has \
         taken the survey for project %s' % project.key().name() )
         continue

      if not this_record_group.mentor_record:
        # student has taken survey, but not mentor
        logging.warning('not continuing without mentor record...')
        continue

      status_options = PROJECT_STATUSES.get(project.status)

      if not status_options:
        logging.warning('unable to find status options for project \
        status %s' % project.status)
        continue

      new_project_grade = this_record_group.mentor_record.grade
      new_project_status = status_options.get(new_project_grade)

      if getattr(this_record_group, 'final_status'):
         logging.warning('project %s record group should not \
         yet have a final status %s' % (
         project.key().name(), this_record_group.final_status ) )
         continue

      # assign the new status to the project and surveyrecordgroup
      project.status = new_project_status
      this_record_group.final_status = new_project_status

  def getKeyNameFromPath(self, path):
    """Gets survey key name from a request path.

    params:
      path = path of the current request
    """

    # TODO determine if kwargs in the request contains this information
    return '/'.join(path.split('/')[-4:]).split('?')[0]

  def getProjects(self, survey, user):
    """Get projects linking user to a program.

    Serves as access handler (since no projects == no access).
    And retrieves projects to choose from (if mentors have >1 projects).

    params:
      survey = survey entity
      user = survey taking user
    """

    this_program = survey.scope or Program.get_by_key_name(survey.scope_path)


    if 'mentor' in survey.taking_access:
      these_projects = self.getMentorProjects(user, this_program)

    elif 'student' in survey.taking_access:
      these_projects = self.getStudentProjects(user, this_program)

    logging.info(these_projects)

    if len(these_projects) == 0:
      return False

    return these_projects

  def getDebugUser(self, survey, this_program):
    """Debugging method impersonates other roles.

    Tests taking survey, saving response, and grading.

    params:
      survey = survey entity
      this_program = program scope of survey
    """

    if 'mentor' in survey.taking_access:
      from soc.models.mentor import Mentor
      role = Mentor.get_by_key_name(
      this_program.key().name() + "/org_1/test")

    if 'student' in survey.taking_access:
      from soc.models.student import Student
      role = Student.get_by_key_name(
      this_program.key().name() + "/test")

    if role: return role.user

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.prefix, entity.scope_path, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['prefix'], fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['prefix', 'scope_path', 'link_id']

  def getScope(self, entity):
    """Gets Scope for entity.

    params:
      entity = Survey entity
    """

    if getattr(entity, 'scope', None):
      return entity.scope

    import soc.models.program
    import soc.models.organization
    import soc.models.user
    import soc.models.site

    # use prefix to generate dict key
    scope_types = {"program": soc.models.program.Program,
    "org": soc.models.organization.Organization,
    "user": soc.models.user.User,
    "site": soc.models.site.Site}

    # determine the type of the scope
    scope_type = scope_types.get(entity.prefix)

    if not scope_type:
      # no matching scope type found
      raise AttributeError('No Matching Scope type found for %s' % entity.prefix)

    # set the scope and update the entity
    entity.scope = scope_type.get_by_key_name(entity.scope_path)
    entity.put()

    # return the scope
    return entity.scope

  def _onCreate(self, entity):
    """Set the scope of the survey.
    """

    self.getScope(entity)
    super(Logic, self)._onCreate(entity)


class ProjectLogic(Logic):
  """Logic class for ProjectSurvey.
  """

  def __init__(self, model=ProjectSurvey,
               base_model=Survey, scope_logic=linkable_logic,
               record_logic=survey_record_logic.project_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(ProjectLogic, self).__init__(model=model, base_model=base_model,
                                       scope_logic=scope_logic,
                                       record_logic=record_logic)


class GradingProjectLogic(ProjectLogic):
  """Logic class for GradingProjectSurvey
  """

  def __init__(self, model=GradingProjectSurvey,
               base_model=ProjectSurvey, scope_logic=linkable_logic,
               record_logic=survey_record_logic.grading_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(GradingProjectLogic, self).__init__(model=model,
                                              base_model=base_model,
                                              scope_logic=scope_logic,
                                              record_logic=record_logic)


logic = Logic()
project_logic = ProjectLogic()
grading_logic = GradingProjectLogic()

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

"""The script which generates KML file for Google Summer of Code 2009 program.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


import sys
import codecs
import interactive


from xml.dom.minidom import Document


def _getMentoredProjects(mentor):
  """Returns a list of projects which are mentored by a given mentor.
  """

  from soc.logic.models.student_project import logic as project_logic

  filter = {
      'mentor': mentor
      }

  return project_logic.getForFields(filter=filter)


def _getAcceptedOrgs():
  """Returns a list of organizations which got accepted.
  """

  from soc.logic.models.organization import logic as org_logic

  filter = {
      'status': 'active'
      }

  entities = org_logic.getForFields(filter=filter)

  filter = {
      'status': 'new'
      }

  entities += org_logic.getForFields(filter=filter)

  return entities


def _getStudentProject(entity):
  """Returns a project for a given student.
  """

  from soc.logic.models.student_project import logic as project_logic

  filter = {
      'student': entity,
      'status': 'accepted',
      }

  return project_logic.getForFields(filter=filter, unique=True)


def _getAllUsers():
  """Returns a list of all valid users.
  """

  from soc.models.user import User

  gen = lambda: User.all().filter('status =', 'valid')
  return interactive.deepFetch(gen)


def _getAllOrgAdmins():
  """Returns a generator of all active mentors.
  """

  from soc.models.org_admin import OrgAdmin

  gen = lambda: OrgAdmin.all().filter('status = ', 'active')
  return interactive.deepFetch(gen)


def _getAllMentors():
  """Returns a generator of all active mentors.
  """

  from soc.models.mentor import Mentor

  gen = lambda: Mentor.all().filter('status = ', 'active')
  return interactive.deepFetch(gen)


def _getAllStudents():
  """Returns a generator of all active students.
  """

  from soc.models.student import Student

  gen = lambda: Student.all().filter('status = ', 'active')
  return interactive.deepFetch(gen)


def _getPersonStyle(doc, type):
  """Returns <Style> element for a particular person.
  """

  if type == 'org_admin':
    x_text, y_text = '0', '0'
  elif type == 'mentor':
    x_text, y_text = '128', '96'
  elif type == 'student':
    x_text, y_text = '64', '160'

  style = doc.createElement('Style')

  icon_style = doc.createElement('IconStyle')
  style.appendChild(icon_style)

  icon = doc.createElement('Icon')
  icon_style.appendChild(icon)

  href = doc.createElement('href')
  icon.appendChild(href)

  text = doc.createTextNode('root://icons/palette-5.png')
  href.appendChild(text)

  x = doc.createElement('x')
  icon.appendChild(x)

  text = doc.createTextNode(x_text)
  x.appendChild(text)

  y = doc.createElement('y')
  icon.appendChild(y)

  text = doc.createTextNode(y_text)
  y.appendChild(text)

  w = doc.createElement('w')
  icon.appendChild(w)

  text = doc.createTextNode('32')
  w.appendChild(text)

  h = doc.createElement('h')
  icon.appendChild(h)

  text = doc.createTextNode('32')
  h.appendChild(text)

  return style


def _getLineStringStyle(doc):
   """Returns <Style> element for a line string placemark.
   """

   style = doc.createElement('Style')

   line_style = doc.createElement('LineStyle')
   style.appendChild(line_style)

   color = doc.createElement('color')
   line_style.appendChild(color)

   text = doc.createTextNode('ff00ff00')
   color.appendChild(text)

   width = doc.createElement('width')
   line_style.appendChild(width)

   text = doc.createTextNode('1')
   width.appendChild(text)

   return style


def _getDescriptionForStudent(doc, student, project):
  """Returns <description> element for a given student.
  """

  description = doc.createElement('description')

  text = doc.createTextNode('Working on...')
  description.appendChild(text)

  description.appendChild(doc.createElement('br'))

  i = doc.createElement('i')
  description.appendChild(i)

  title = doc.createTextNode(project.title)
  i.appendChild(title)
  description.appendChild(doc.createElement('br'))

  mentor = doc.createTextNode(
      'mentored by ' + _getName(project.mentor))
  description.appendChild(mentor)
  description.appendChild(doc.createElement('br'))

  org = doc.createTextNode(project.scope.name)
  description.appendChild(org)
  description.appendChild(doc.createElement('br'))
  description.appendChild(doc.createElement('br'))

  description = _appendHomePageAndBlogContent(doc, description, student)

  description = _appendStateAndCountryContnent(doc, description, student)

  return description


def _appendStateAndCountryContnent(doc, description, state, country):
  """Appends state and country info to the description of a placemark.
  """

  if state:
    description.appendChild(doc.createTextNode(state + ', '))

  description.appendChild(doc.createTextNode(country))

  return description


def _appendHomePageAndBlogContent(doc, description, home_pages, blogs):
  """Appends home page and blog info to the description of a placemark.
  """

  if home_pages:
    text = doc.createTextNode('Home page:')
    description.appendChild(text)
    description.appendChild(doc.createElement('br'))

  for home_page in home_pages:
    description.appendChild(doc.createTextNode(home_page))
    description.appendChild(doc.createElement('br'))

  if home_pages:
    description.appendChild(doc.createElement('br'))

  if blogs:
    text = doc.createTextNode('Blog:')
    description.appendChild(text)
    description.appendChild(doc.createElement('br'))

  for blog in blogs:
    description.appendChild(doc.createTextNode(blog))
    description.appendChild(doc.createElement('br'))

  if blogs:
    description.appendChild(doc.createElement('br'))

  return description


def _getName(entity):
  """For a given entity returns a name to be displayed.
  """

  return entity.name()


def _getMentorDescription(doc, content):
  """Returns <description> element for a mentor / org admin based on content.
  """

  description = doc.createElement('description')

  admin = content['admin']
  if admin:
    text = doc.createTextNode('Organization admin for ' + admin)
    description.appendChild(text)
    description.appendChild(doc.createElement('br'))

  projects = content['projects']
  if projects:
    text = doc.createTextNode('Mentoring...')
    description.appendChild(text)
    description.appendChild(doc.createElement('br'))

  for project in projects:
    i = doc.createElement('i')
    description.appendChild(i)

    title = doc.createTextNode(project['title'])
    i.appendChild(title)
    description.appendChild(doc.createElement('br'))

    student = doc.createTextNode('by ' + project['student'])
    description.appendChild(student)
    description.appendChild(doc.createElement('br'))

    organization = doc.createTextNode(project['org'])
    description.appendChild(organization)
    description.appendChild(doc.createElement('br'))

  consults = content['consults']
  for consult in consults:
    text = doc.createTextNode(consult)
    description.appendChild(text)
    description.appendChild(doc.createElement('br'))

  description.appendChild(doc.createElement('br'))

  home_pages = content['home_pages']
  blogs = content['blogs']
  description = _appendHomePageAndBlogContent(doc, description,
      home_pages, blogs)

  state = content['state']
  country = content['country']
  description = _appendStateAndCountryContnent(doc, description, state,
      country)

  return description


def _getStudentDescription(doc, content):
  """Returns <description> element for a student based on content.
  """

  description = doc.createElement('description')

  text = doc.createTextNode('Working on...')
  description.appendChild(text)

  description.appendChild(doc.createElement('br'))

  project = content['project']
  i = doc.createElement('i')
  description.appendChild(i)

  title = doc.createTextNode(project.title)
  i.appendChild(title)
  description.appendChild(doc.createElement('br'))

  mentor = doc.createTextNode('mentored by ' + project.mentor.name())
  description.appendChild(mentor)
  description.appendChild(doc.createElement('br'))

  org = doc.createTextNode(project.scope.name)
  description.appendChild(org)
  description.appendChild(doc.createElement('br'))
  description.appendChild(doc.createElement('br'))

  home_pages = content['home_pages']
  blogs = content['blogs']
  description = _appendHomePageAndBlogContent(doc, description,
      home_pages, blogs)

  state = content['state']
  country = content['country']
  description = _appendStateAndCountryContnent(doc, description, state,
      country)

  return description


def _createFolderForMentorsAndOrgAdmins(doc):
  """
  """

  folder = doc.createElement("Folder")

  name = doc.createElement("name")
  folder.appendChild(name)

  nametext = doc.createTextNode("Mentors")
  name.appendChild(nametext)

  return folder


def _createLineString(doc, student, mentor):
  """Generates line string between a given student and mentor.
  """

  line_string = doc.createElement('LineString')

  coordinates = doc.createElement('coordinates')
  line_string.appendChild(coordinates)

  text = doc.createTextNode(str(student[0]) + ',' + str(student[1]) + ' ' +
      str(mentor[0]) + ',' + str(mentor[1]))
  coordinates.appendChild(text)

  altitude_mode = doc.createElement('altitudeMode')
  line_string.appendChild(altitude_mode)

  text = doc.createTextNode('clampToGround')
  altitude_mode.appendChild(text)

  extrude = doc.createElement('extrude')
  line_string.appendChild(extrude)

  text = doc.createTextNode('1')
  extrude.appendChild(text)

  tessellate = doc.createElement('tessellate')
  line_string.appendChild(tessellate)

  text = doc.createTextNode('1')
  tessellate.appendChild(text)

  return line_string


def _createPoint(doc, longitude, latitude):
  """Generates <Point> subtree with coordinates for a given entity.
  """

  point = doc.createElement('Point')

  coordinates = doc.createElement('coordinates')
  point.appendChild(coordinates)

  text = doc.createTextNode(str(longitude) + ',' + str(latitude))
  coordinates.appendChild(text)

  return point


def _createStudentPlacemark(doc, coordinates, content):
  """Creates <Placemark> element for a student based on a given content.
  """

  placemark = doc.createElement('Placemark')

  style = _getPersonStyle(doc, 'student')
  placemark.appendChild(style)

  name = doc.createElement('name')
  placemark.appendChild(name)

  text = doc.createTextNode(content['name'])
  name.appendChild(text)

  description = _getStudentDescription(doc, content)
  placemark.appendChild(description)

  point = _createPoint(doc, coordinates[0], coordinates[1])
  placemark.appendChild(point)

  return placemark


def _createMentorPlacemark(doc, coordinates, content):
  """Creates <Placemark> element for a mentor based on a given content.
  """

  placemark = doc.createElement('Placemark')

  type = 'org_admin' if content['admin'] is not None else 'mentor'
  style = _getPersonStyle(doc, type)
  placemark.appendChild(style)

  name = doc.createElement('name')
  placemark.appendChild(name)

  text = doc.createTextNode(content['name'])
  name.appendChild(text)

  description = _getMentorDescription(doc, content)
  placemark.appendChild(description)

  point = _createPoint(doc, coordinates[0], coordinates[1])
  placemark.appendChild(point)

  return placemark


def _createLineStringPlacemark(doc, student_coordinates, mentor_coordinates):
  """Creates <Placemark> element for a line string between given student
     coordinates and mentor coordinates.
  """

  placemark = doc.createElement('Placemark')

  line_string = _createLineString(doc, student_coordinates, mentor_coordinates)
  placemark.appendChild(line_string)

  style = _getLineStringStyle(doc)
  placemark.appendChild(style)

  return placemark


def _processMentor(doc, org_admin, mentors, folder):
  """Processes a student and adds information to a folder.
  """

  projects = []
  placemarks = {}
  longitude = None
  latitude = None

  for entity in mentors:
    if not entity.publish_location:
      continue

    longitude, latitude = (entity.longitude, entity.latitude)

    if not placemarks.get((longitude, latitude)):
      placemarks[(longitude, latitude)] = {
          'admin': None,
          'projects': [],
          'consults': [],
          'name': entity.name(),
          'country': entity.res_country,
          'state': entity.res_state,
          'home_pages': set(),
          'blogs': set()
          }

    projects = _getMentoredProjects(entity)
    if not projects:
      placemarks[(longitude, latitude)]['consults'].append(
          'Mentor for ' + entity.scope.name)
    else:
      for project in projects:
        placemarks[(longitude, latitude)]['projects'].append({
            'title': project.title,
            'org': project.scope.name,
            'student': project.student.name()
            })

    if entity.home_page:
      placemarks[(longitude, latitude)]['home_pages'].add(entity.home_page)
    if entity.blog:
      placemarks[(longitude, latitude)]['blogs'].add(entity.blog)

  if org_admin and org_admin.publish_location:

    if not (longitude, latitude):
      longitude, latitude = (org_admin.longitude, org_admin.latitude)

    if not placemarks.get((longitude, latitude)):
      placemarks[(longitude, latitude)] = {
          'admin': None,
          'projects': [],
          'consults': [],
          'name': org_admin.name(),
          'country': org_admin.res_country,
          'state': org_admin.res_state,
          'home_pages': set(),
          'blogs': set()
          }

    placemarks[(longitude, latitude)]['admin'] = org_admin.scope.name

    if org_admin.home_page:
      placemarks[(longitude, latitude)]['home_pages'].add(org_admin.home_page)
    if org_admin.blog:
      placemarks[(longitude, latitude)]['blogs'].add(org_admin.blog)

  for coordinates, content in placemarks.iteritems():
    placemark = _createMentorPlacemark(doc, coordinates, content)
    folder.appendChild(placemark)


def _processStudent(doc, student, orgs_folder):
  """Processes a student and adds information to a folder.
  """

  if not student.publish_location:
    return

  project = _getStudentProject(student)

  if not project:
    return

  folder = doc.createElement('Folder')

  name = doc.createElement('name')
  folder.appendChild(name)

  name.appendChild(doc.createTextNode(student.name()))

  content = {
      'name': student.name(),
      'project': project,
      'country': student.res_country,
      'state': student.res_state,
      'home_pages': [student.home_page] if student.home_page else [],
      'blogs': [student.blog] if student.blog else []
      }

  coordinates = student.longitude, student.latitude

  placemark = _createStudentPlacemark(doc, coordinates, content)
  folder.appendChild(placemark)

  mentor = project.mentor

  if mentor.publish_location:
    mentor_coordinates = mentor.longitude, mentor.latitude
    line_string = _createLineStringPlacemark(doc, coordinates,
        mentor_coordinates)
    folder.appendChild(line_string)

  org = project.scope
  org_folder = orgs_folder[org.name]
  org_folder.appendChild(folder)


def _processAllUsers(doc, mentors_folder, orgs_folder):
  """Processes all users and fills folders with information based on roles.
  """

  from soc.logic.models.mentor import logic as mentor_logic
  from soc.logic.models.org_admin import logic as org_admin_logic
  from soc.logic.models.student import logic as student_logic

  it = _getAllOrgAdmins()
  org_admins = dict()
  for org_admin in it:
    org_admins[org_admin.link_id] = org_admin

  it = _getAllMentors()
  mentors = dict()
  for mentor in it:
    link_id = mentor.link_id
    if link_id not in mentors:
      mentors[link_id] = []
    mentors[link_id].append(mentor)

  it = _getAllStudents()
  students = dict()
  for student in it:
    students[student.link_id] = student

  link_ids = set(mentors.keys() + org_admins.keys())

  for link_id in link_ids:
    entity = org_admins.get(link_id)
    entities = mentors.get(link_id, [])

    if entity or entities:
      _processMentor(doc, entity, entities, mentors_folder)
      continue

  link_ids = students.keys()
  for link_id in link_ids:
    entity = students.get(link_id)
    if entity:
      _processStudent(doc, entity, orgs_folder)


def _createFolderForStudentsAndOrgs(doc):
  """Creates <Folder> elements for all students and for all accepted
     organizations.

  Returns:
    A tuple whose first element is a folder for students and the second
    one is a dictionary mapping organization names with their folders.
  """

  folder = doc.createElement('Folder')

  name = doc.createElement('name')
  folder.appendChild(name)

  text = doc.createTextNode('Students')
  name.appendChild(text)

  orgs = _getAcceptedOrgs()
  org_folders = {}

  for org in orgs:
    org_folder = doc.createElement('Folder')
    folder.appendChild(org_folder)

    name = doc.createElement('name')
    org_folder.appendChild(name)

    text = doc.createTextNode(org.name)
    name.appendChild(text)

    org_folders[org.name] = org_folder

  return folder, org_folders


def generateCompleteKML():
  """Generates complete KML file for Google Summer of Code 2009.
  """

  doc = Document()

  kml = doc.createElement('kml')
  doc.appendChild(kml)

  document = doc.createElement('Document')
  kml.appendChild(document)

  mentor_folder = _createFolderForMentorsAndOrgAdmins(doc)
  document.appendChild(mentor_folder)

  student_folder, org_folders = _createFolderForStudentsAndOrgs(doc)
  document.appendChild(student_folder)

  _processAllUsers(doc, mentor_folder, org_folders)

  out = codecs.open('soc_map2009.kml', 'w', 'utf-8')
  out.write(doc.toprettyxml(indent='  '))
  out.close()


def main(args):

  context = {
      'export': generateCompleteKML,
      }
  interactive.setup()
  interactive.remote(args, context)


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % (sys.argv[0],)
    sys.exit(1)

  main(sys.argv[1:])

#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing data sets test fixtures.
"""


__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import users

from fixture import DataSet


class UserData(DataSet):
  class all_admin:
    key_name = 'test@example.com'
    link_id = 'super_admin'
    account = users.User(email='test@example.com')
    name = 'Super Admin'
    is_developer = True

  class site_admin:
    key_name = 'site_admin'
    link_id = 'site_admin'
    account = users.User(email='site_admin@example.com')
    name = 'Site Admin'

  class melange_admin_0001:
    key_name = 'melange_admin_0001'
    link_id = 'melange_admin_0001'
    account = users.User(email='melange_admin_0001@example.com')
    name = 'Melange Admin 0001'

  class melange_admin_0002:
    key_name = 'melange_admin_0002'
    link_id = 'melange_admin_0002'
    account = users.User(email='melange_admin_0002@example.com')
    name = 'Melange Admin 0002'

  class asf_admin_0001:
    key_name = 'asf_admin_0001'
    link_id = 'asf_admin_0001'
    account = users.User(email='asf_admin_0001@example.com')
    name = 'ASF Admin 0001'

  class melange_mentor_0001:
    key_name = 'melange_mentor_0001'
    link_id = 'melange_mentor_0001'
    account = users.User(email='melange_mentor_0001@example.com')
    name = 'Melange Mentor 0001'

  class melange_mentor_0002:
    key_name = 'melange_mentor_0002'
    link_id = 'melange_mentor_0002'
    account = users.User(email='melange_mentor_0002@example.com')
    name = 'Melange Mentor 0002'

  class asf_mentor_0001:
    key_name = 'asf_mentor_0001'
    link_id = 'asf_mentor_0001'
    account = users.User(email='asf_mentor_0001@example.com')
    name = 'ASF Mentor 001'

  class melange_student_0001:
    key_name = 'melange_student_0001'
    link_id = 'melange_student_0001'
    account = users.User(email='melange_student_0001@example.com')
    name = 'Melange Student 0001'

  class melange_student_0002:
    key_name = 'melange_student_0002'
    link_id = 'melange_student_0002'
    account = users.User(email='melange_student_0002@example.com')
    name = 'Melange Student 0002'

  class asf_student_0001:
    key_name = 'asf_student_0001'
    link_id = 'asf_student_0001'
    account = users.User(email='asf_student_0001@example.com')
    name = 'ASF Student 0001'

  class public:
    key_name = 'public'
    link_id = 'public'
    account = users.User(email='public@example.com')
    name = 'Public'

class SiteData(DataSet):
  class site:
    key_name = 'site'
    link_id = 'site'


class SponsorData(DataSet):
  class google:
    key_name = 'google'
    link_id = 'google'
    name = 'Google Inc.'
    short_name = 'Google'
    founder = UserData.site_admin
    home_page = 'http://www.google.com'
    email = 'ospo@google.com'
    description = 'This is the profile for Google.'
    contact_street = 'Some Street'
    contact_city = 'Some City'
    contact_country = 'United States'
    contact_postalcode = '12345'
    phone = '1-555-BANANA'
    status = 'active'


class HostData(DataSet):
  class google:
    key_name = 'google/test'
    link_id = 'test'
    scope = SponsorData.google
    scope_path = 'google'
    user = UserData.site_admin
    given_name = 'Test'
    surname = 'Example'
    name_on_documents = 'Test Example'
    email = 'test@example.com'
    res_street = 'Some Street'
    res_city = 'Some City'
    res_state = 'Some State'
    res_country = 'United States'
    res_postalcode = '12345'
    phone = '1-555-BANANA'
    birth_date = db.DateProperty.now()
    agreed_to_tos = True


class TimelineData(DataSet):
  class gsoc2009:
    key_name = 'google/gsoc2009'
    link_id = 'gsoc2009'
    scope_path = 'google'
    scope = SponsorData.google


class GHOPTimelineData(DataSet):
  class ghop2009:
    key_name = 'google/ghop2009'
    link_id = 'ghop2009'
    scope_path = 'google'
    scope = SponsorData.google
    program_start = datetime(2009, 9, 11)
    program_end = datetime(2010, 2, 10)
    org_signup_start = datetime(2009, 9, 18)
    org_signup_end = datetime(2010, 2, 01)


class ProgramData(DataSet):
  class gsoc2009:
    key_name = 'google/gsoc2009'
    link_id = 'gsoc2009'
    scope_path ='google'
    scope = SponsorData.google
    name = 'Google Summer of Code 2009'
    short_name = 'GSoC 2009'
    group_label = 'GSOC'
    description = 'This is the program for GSoC 2009.'
    apps_tasks_limit = 42
    slots = 42
    timeline = TimelineData.gsoc2009
    status = 'visible'


class GHOPProgramData(DataSet):
  class ghop2009:
    key_name = 'google/ghop2009'
    link_id = 'ghop2009'
    scope_path ='google'
    scope = SponsorData.google
    name = 'Google Highly Open Participation Contest 2009'
    short_name = 'GHOP 2009'
    group_label = 'GHOP'
    description = 'This is the program for GHOP 2009.'
    apps_tasks_limit = 42
    slots = 42
    timeline = GHOPTimelineData.ghop2009
    status = 'visible'


class OrgData(DataSet):
  class melange_gsoc:
    key_name = 'google/ghop2009/melange'
    link_id = 'melange'
    name = 'Melange Development Team'
    short_name = 'Melange'
    scope_path = 'google/gsoc2009'
    scope = ProgramData.gsoc2009
    home_page = 'http://code.google.com/p/soc'
    description = 'Melange, share the love!'
    license_name = 'Apache License'
    ideas = 'http://code.google.com/p/soc/issues'
    founder = UserData.melange_admin_0001
    email = 'ospo@google.com'
    contact_street = 'Some Street'
    contact_city = 'Some City'
    contact_country = 'United States'
    contact_postalcode = '12345'
    phone = '1-555-BANANA'
    status = 'active'


class GHOPOrganizationData(DataSet):
  class melange_ghop:
    key_name = 'google/ghop2009/melange'
    link_id = 'melange'
    name = 'Melange Development Team'
    short_name = 'Melange'
    scope_path = 'google/ghop2009'
    scope = GHOPProgramData.ghop2009
    home_page = 'http://code.google.com/p/soc'
    description = 'Melange, share the love!'
    license_name = 'Apache License'
    ideas = 'http://code.google.com/p/soc/issues'
    founder = UserData.melange_admin_0001
    email = 'ospo@google.com'
    contact_street = 'Some Street'
    contact_city = 'Some City'
    contact_country = 'United States'
    contact_postalcode = '12345'
    phone = '1-555-BANANA'
    status = 'active'
    task_quota_limit = 100

  class asf_ghop:
    key_name = 'google/ghop2009/asf'
    link_id = 'asf'
    name = 'ASF Development Team'
    short_name = 'ASF'
    scope_path = 'google/ghop2009'
    scope = GHOPProgramData.ghop2009
    home_page = 'http://apache.org'
    description = 'Apache Software Foundation'
    license_name = 'Apache License'
    ideas = 'http://apache.org/ideas'
    founder = UserData.asf_admin_0001
    email = 'mail@asf.org'
    contact_street = 'Some Street'
    contact_city = 'Some City'
    contact_country = 'United States'
    contact_postalcode = '12345'
    phone = '1-555-BANANA'
    status = 'active'


class GHOPOrgAdminData(DataSet):
  class melange:
    key_name = 'google/ghop2009/melange/test'
    link_id = 'test'
    scope_path = 'google/ghop2009/melange'
    scope = GHOPOrganizationData.melange_ghop
    program = GHOPProgramData.ghop2009
    user = UserData.melange_admin_0001
    given_name = 'Test'
    surname = 'Example'
    name_on_documents = 'Test Example'
    email = 'test@example.com'
    res_street = 'Some Street'
    res_city = 'Some City'
    res_state = 'Some State'
    res_country = 'United States'
    res_postalcode = '12345'
    phone = '1-555-BANANA'
    birth_date = db.DateProperty.now()
    agreed_to_tos = True


class GHOPMentorData(DataSet):
  class melange:
    key_name = 'google/ghop2009/melange/test'
    link_id = 'test'
    scope_path = 'google/ghop2009/melange'
    scope = GHOPOrganizationData.melange_ghop
    program = GHOPProgramData.ghop2009
    user = UserData.melange_mentor_0001
    given_name = 'Test'
    surname = 'Example'
    name_on_documents = 'Test Example'
    email = 'test@example.com'
    res_street = 'Some Street'
    res_city = 'Some City'
    res_state = 'Some State'
    res_country = 'United States'
    res_postalcode = '12345'
    phone = '1-555-BANANA'
    birth_date = db.DateProperty.now()
    agreed_to_tos = True


class GHOPStudentData(DataSet):
  class melange_student_0001:
    student_id = 'melange_student_0001'
    key_name = GHOPProgramData.ghop2009.key_name + "/" + student_id
    link_id = student_id
    scope_path = GHOPProgramData.ghop2009.key_name
    scope = GHOPProgramData.ghop2009
    program = GHOPProgramData.ghop2009
    user = UserData.melange_student_0001
    given_name = 'Melange_Student'
    surname = 'Melfam'
    birth_date = db.DateProperty.now()
    email = 'melange_student_0001@email.com'
    im_handle = 'melange_student_0001'
    major = 'Aerospace Engineering'
    name_on_documents = 'melstud0001'
    res_country = 'United States'
    res_city = 'Minnesota'
    res_street = 'Good Street'
    res_postalcode = '12345'
    publish_location = True
    blog = 'http://www.blog.com/'
    home_page = 'http://www.homepage.com/'
    photo_url = 'http://www.photosite.com/thumbnail.png'
    ship_state = None
    expected_graduation = 2009
    school_country = 'United States'
    school_name = 'St.Joseph School'
    tshirt_size = 'XS'
    tshirt_style = 'male'
    degree = 'Undergraduate'
    phone = '1650253000'
    can_we_contact_you = True
    program_knowledge = 'I heard about this program through a friend.'

  class asf_student_0001:
    student_id = 'asf_student_0001'
    key_name = GHOPProgramData.ghop2009.key_name + "/" + student_id
    link_id = student_id
    scope_path = GHOPProgramData.ghop2009.key_name
    scope = GHOPProgramData.ghop2009
    program = GHOPProgramData.ghop2009
    user = UserData.melange_student_0001
    given_name = 'ASF_Student'
    surname = 'Asffam'
    birth_date = db.DateProperty.now()
    email = 'asf_student_0001@email.com'
    im_handle = 'asf_student_0001'
    major = 'Chemical Engineering'
    name_on_documents = 'asfstud0001'
    res_country = 'United States'
    res_city = 'New York'
    res_street = 'Jam Street'
    res_postalcode = '452543'
    publish_location = True
    blog = 'http://www.hasblog.com/'
    home_page = 'http://www.merahomepage.com/'
    photo_url = 'http://www.clickphoto.com/thumbnail.png'
    ship_state = None
    expected_graduation = 2009
    school_country = 'United States'
    school_name = 'Benedict School'
    tshirt_size = 'XXL'
    tshirt_style = 'male'
    degree = 'Undergraduate'
    phone = '1650253000'
    can_we_contact_you = True
    program_knowledge = 'From slashdot.org post last year.'

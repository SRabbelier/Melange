# Copyright 2008 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing Melange Django settings.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Augie Fackler" <durin42@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]

import os

# Debug flag True only on App Engine development environment (dev_appserver.py)
# dev_appserver sets SERVER_SOFTWARE to 'Development/1.0'
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_ENGINE = 'dummy'
# None of the following are used with appengine
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
# Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = ''
# Set to empty string for default. Not used with sqlite3.
DATABASE_PORT = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# The order of the middleware is as follows because:
# - The ValueStore middleware should be before any other middleware
#   so that the value store is available to it.
# - The ExceptionHandler should be the outermost handler (after the
#   ValueStore) so as to catch as many errors as possible.
# - The Profile middleware should be as outmost as possible, so that
#   as many function calls as possible, but it cannot be before the
#   ExceptionHandler (so as to catch exceptions thrown by it).
# - The MaintenanceMiddleware should be after the Profiler, since we
#   do want it's actions profiled.
MIDDLEWARE_CLASSES = (
    'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware',
    'soc.middleware.value_store.ValueStoreMiddleware',
#    'soc.middleware.exception_handler.ExceptionHandlerMiddleware',
#    'soc.middleware.profiler.ProfileMiddleware',
    'soc.middleware.maintenance.MaintenanceMiddleware',
    'soc.middleware.blobstore.BlobStoreMiddleware',
    'soc.middleware.xsrf.XsrfMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'urls'

ROOT_PATH = os.path.dirname(__file__)
TEMPLATE_DIRS = (
    # TODO(proto): customize the template search directories
    os.path.join(ROOT_PATH, 'soc', 'templates'),
    os.path.join(ROOT_PATH, 'shell', 'templates'),
)

INSTALLED_APPS = (
    'soc.views.helper',
    'soc.modules.gsoc.views.helper',
    'soc.modules.gci.views.helper',
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
)

GCI_TASK_QUOTA_LIMIT_ENABLED = False

MODULE_FMT = 'soc.modules.%s.callback'
MODULES = ['gsoc', 'statistic', 'gci']

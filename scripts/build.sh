#!/bin/bash

# Script to create a "build" subdirectory.  This is a subdirectory
# containing a bunch of symlinks, from which the app can be updated.
# The main reason for this is to import Django from a zipfile, which
# saves dramatically in upload time: statting and computing the SHA1
# for 1000s of files is slow.  Even if most of those files don't
# actually need to be uploaded, they still add to the work done for
# each update.

DEFAULT_APP_BUILD=../build
DEFAULT_APP_FOLDER="../app"
DEFAULT_APP_FILES="app.yaml cron.yaml index.yaml main.py settings.py urls.py"
DEFAULT_APP_DIRS="soc ghop gsoc feedparser python25src reflistprop jquery ranklist json"
DEFAULT_ZIP_FILES="tiny_mce.zip"

APP_BUILD=${APP_BUILD:-"${DEFAULT_APP_BUILD}"}
APP_FOLDER=${APP_FOLDER:-"${DEFAULT_APP_FOLDER}"}
APP_FILES=${APP_FILES:-"${DEFAULT_APP_FILES}"}
APP_DIRS=${APP_DIRS:-"${DEFAULT_APP_DIRS}"}
ZIP_FILES=${ZIP_FILES:-"${DEFAULT_ZIP_FILES}"}

if [ -e $APP_FOLDER ] ; then
    cd $APP_FOLDER
else
    echo 'This script must be run from within the scripts directory!'
    exit 1
fi

# Remove old zip files (and django.zip in its old location)
rm -rf $ZIP_FILES django.zip

# Remove old $APP_BUILD directory.
rm -rf $APP_BUILD

# Create new $APP_BUILD directory.
mkdir $APP_BUILD

# Create new django.zip file, but directly in the $APP_BUILD directory,
# rather than in $APP_FOLDER and creating a symlink in $APP_BUILD.  This
# keeps the presence of a django.zip file in the app/ folder from breaking
# debugging into app/django.
#
# We prune:
# - .svn subdirectories for obvious reasons.
# - contrib/gis/ and related files because it's huge and unneeded.
# - *.po and *.mo files because they are bulky and unneeded.
# - *.pyc and *.pyo because they aren't used by App Engine anyway.

zip -q "$APP_BUILD/django.zip" `find django \
    -name .svn -prune -o \
    -name gis -prune -o \
    -name admin -prune -o \
    -name localflavor -prune -o \
    -name mysql -prune -o \
    -name mysql_old -prune -o \
    -name oracle -prune -o \
    -name postgresql-prune -o \
    -name postgresql_psycopg2 -prune -o \
    -name sqlite3 -prune -o \
    -name test -prune -o \
    -type f ! -name \*.py[co] ! -name *.[pm]o -print`

# Create new tiny_mce.zip file.
#
# We prune:
# - .svn subdirectories for obvious reasons.

# zipserve requires tiny_mce/* to be in root of zip file
pushd tiny_mce > /dev/null
zip -q ../tiny_mce.zip `find . \
    -name .svn -prune -o \
    -type f -print`
popd > /dev/null

# Create symbolic links.
for x in $APP_FILES $APP_DIRS $ZIP_FILES
do
    ln -s $APP_FOLDER/$x $APP_BUILD/$x
done

echo "Build results in $APP_BUILD."

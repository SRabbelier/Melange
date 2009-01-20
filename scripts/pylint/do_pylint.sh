#!/bin/bash
# Copyright 2008 the Melange authors.
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

# Set some environmental variables for pylint and run it on Melange code
# To disable some of the checks use options listed below:
# disable unused imports: --disable-msg=W0611
# disable TODO: --disable-msg=W0511
# disable report: --reports=no
# disable similarity check: --disable-checker=similarities
#
# Checks listed above are disabled in silent mode 
# which can be run using --silent argument

SILENT_ARGS=""
ARGS=( "$@" )

if [ "$1" == "--silent" ]; then
  SILENT_ARGS="--disable-msg=W0611 --disable-msg=W0511 --reports=no --disable-checker=similarities"
  ARGS[0]=""
fi

PROJ_DIR=$(dirname "$0")/../..
PROJ_DIR=$(cd "$PROJ_DIR"; pwd)
APP_DIR="${PROJ_DIR}/app"

# Note: We will add ghop and gsoc modules once there something in there
CHECK_MODULES="soc reflistprop settings.py urls.py main.py"

PYLINTRC=$(dirname "$0")/pylintrc
PYTHONPATH="${PYTHONPATH}:${PROJ_DIR}/app/:${PROJ_DIR}/thirdparty/google_appengine/"

export PYTHONPATH
export PYLINTRC

PYLINT_PATH=$(which pylint)

if [ "$PYLINT_PATH" = "" ]; then
  echo >&2 "Cannot find pylint. Make sure pylint is in your PATH variable."
  exit 1
fi

CHECK_MODULES_PATHS=""

for x in $CHECK_MODULES
do
    CHECK_MODULES_PATHS="${CHECK_MODULES_PATHS} ${APP_DIR}/${x}"
done

pylint $SILENT_ARGS $ARGS $CHECK_MODULES_PATHS

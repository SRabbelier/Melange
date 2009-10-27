#!/bin/bash
#Requires java installed

echo "JSLINT: running jslint"

JS_DIRECTORY="../app/soc/content/js"
JSLINT="../thirdparty/jslint/jslint.js"
RHINO="../thirdparty/shrinksafe/js.jar"

for dir in $(find $JS_DIRECTORY -type d); do
  for i in $(find $dir/*.js -type f); do
    echo "JSLINT: Processing $i"
    java -jar $RHINO $JSLINT $i
  done
done

echo "JSLINT: process finished"

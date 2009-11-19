#!/bin/bash
<<JSDOCTOOLKIT
Script to run JSDocToolkit over our JS files.

It creates a documentation directory under app/soc/content/js
with the output for private and public docs, with or without
undocumented functions.

Requires Java installed.
JSDOCTOOLKIT

jsdoc_dir="../thirdparty/jsdoctoolkit"

js_dir="../app/soc/content/js"
doc_dir="$js_dir/documentation"
private_doc_dir="$doc_dir/private"
public_doc_dir="$doc_dir/public"
private_all_doc_dir="$doc_dir/private_all"
public_all_doc_dir="$doc_dir/public_all"

echo "*** JSDOCTOOLKIT: cleaning out former documentation dir ***"
rm -fr $doc_dir

echo "*** JSDOCTOOLKIT: creating private documentation ***"
java -jar $jsdoc_dir/jsrun.jar $jsdoc_dir/app/run.js $js_dir/*.js -r -p -t=$jsdoc_dir/templates/jsdoc -d=$private_doc_dir

echo "*** JSDOCTOOLKIT: creating private documentation for all functions ***"
java -jar $jsdoc_dir/jsrun.jar $jsdoc_dir/app/run.js $js_dir/*.js -r -a -p -t=$jsdoc_dir/templates/jsdoc -d=$private_all_doc_dir

echo "*** JSDOCTOOLKIT: creating public documentation ***"
java -jar $jsdoc_dir/jsrun.jar $jsdoc_dir/app/run.js $js_dir/*.js -r -t=$jsdoc_dir/templates/jsdoc -d=$public_doc_dir

echo "*** JSDOCTOOLKIT: creating public documentation for all functions ***"
java -jar $jsdoc_dir/jsrun.jar $jsdoc_dir/app/run.js $js_dir/*.js -r -a -t=$jsdoc_dir/templates/jsdoc -d=$public_all_doc_dir

echo "*** JSDOCTOOLKIT: processing finished, documentation available in app/soc/content/js/documentation ***"


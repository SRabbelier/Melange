#!/bin/bash
<<JSLINT
Script to run JSLint over JS files to check JS code quality.

This script will run JSLint over all files in app/soc/content/js
directory and subdirectories to check JS code guidelines compliance.

Requires Java installed.
JSLINT

echo "JSLINT: skipping jslint"

exit 0

# TODO(dbentley): use some sort of javascript linter/compiler.


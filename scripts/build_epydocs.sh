#!/bin/bash
# Generates epydoc for $target to $outdir, while ignoring $exclude
# WARNING: The contents of $outdir are -deleted- before the running epydoc
# This way there are no 'stale files' when the script finishes.

 outdir="../../wiki/html/epydoc"
 target="../app ../tests"
exclude="django"

echo "Cleaning out $outdir..."
rm -f $outdir/*
echo "Done."
echo

echo "Running epydoc..."
echo "$target -> $outdir"
echo "================="

epydoc --html -v --show-private --inheritance=included --graph=all \
  --parse-only --exclude=$exclude -o $outdir $target

echo "================="
echo "Done."
echo

echo "Goodbye."


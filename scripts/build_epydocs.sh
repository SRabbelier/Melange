#!/bin/bash

echo "Running epydoc..."
echo $1

epydoc --html -v --show-private --inheritance=included --graph=all \
  -o ../../wiki/html/epydoc $1

echo "Done."


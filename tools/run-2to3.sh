#!/bin/bash

ROOTDIR="$( dirname "$BASH_SOURCE" )/.."
cd "$ROOTDIR"

DESTINATION="../smartrpyc-py3k"

2to3 -W -o "$DESTINATION"/ -n .
cp -t "$DESTINATION" .gitignore README.rst LICENSE MANIFEST.in

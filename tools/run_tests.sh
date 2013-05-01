#!/bin/bash

ROOTDIR="$( dirname "$BASH_SOURCE" )/.."
cd "$ROOTDIR"

if [ $# == 0 ]; then

    ## Discover & run all the tests
    unit2 discover -v

else

    ## If --list was passed, list the tests
    if [ "$1" == "--list" ]; then
	find smartrpyc/tests/ -name 'test_*.py' | sed 's@/@.@g;s#\.py$##' | sort
	exit
    fi

    ## Run the selected tests
    unit2 -v "$@"

fi

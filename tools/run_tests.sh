#!/bin/bash

ROOTDIR="$( dirname "$BASH_SOURCE" )/.."
cd "$ROOTDIR"

if which unit2 &>/dev/null; then
    UNITTEST=unit2
else
    UNITTEST="python -m unittest"
fi


if [ $# == 0 ]; then

    ## Discover & run all the tests
    $UNITTEST discover -v

else

    ## If --list was passed, list the tests
    if [ "$1" == "--list" ]; then
	find smartrpyc/tests/ -name 'test_*.py' | sed 's@/@.@g;s#\.py$##' | sort
	exit
    fi

    ## Run the selected tests
    $UNITTEST -v "$@"

fi

#!/bin/bash

TEMPDIR="$( mktemp -d )"
cd "$TEMPDIR"

git clone git@github.com:xk0/SmartRPyC.git -b feature/python-3.2 --depth 0 smartrpyc
virtualenv -p /usr/bin/python3.2 --distribute venv
. venv/bin/activate

cd smartrpyc/
python setup.py install

cd build/lib/
python -m unittest discover -v smartrpyc.tests

echo "--------------------"
echo "Tests run. Now you can remove $TEMPDIR"

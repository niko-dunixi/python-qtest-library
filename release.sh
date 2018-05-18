#!/usr/bin/env bash
set -e
#python3 setup.py sdist
python3 setup.py bdist_wheel 
twine upload dist/*


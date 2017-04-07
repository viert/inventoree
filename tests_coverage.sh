#!/bin/sh

coverage run --source="." --omit="tests/*,commands/*" --branch ./micro.py test "$@"

echo
echo
echo Test coverage:
echo

coverage report -m

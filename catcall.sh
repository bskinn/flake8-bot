#! /bin/bash

# This is a not-especially-great general-purpose caller helper.
# Do NOT use blindly in other circumstances.

if [ "$1" = "" ]
then
  echo "No argument. Exiting..."
  exit 1
fi

echo Command: "$*"
echo

echo Script contents:
cat "$1"
echo

sleep 2

echo "Execution:"
"$@"

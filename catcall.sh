#! /bin/bash

# This is a not-especially-great general-purpose caller helper.
# Do NOT use blindly in other circumstances.

#####################################################################
# Per https://sharats.me/posts/shell-script-best-practices/ (partial)
set -o errexit
set -o nounset
set -o pipefail

if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi
#####################################################################

if [[ "$1" = "" ]]
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

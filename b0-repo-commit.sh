#! /bin/bash

#####################################################################
# Per https://sharats.me/posts/shell-script-best-practices/ (partial)
set -o errexit
set -o nounset
set -o pipefail

if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi
#####################################################################

BRANCH=$( git branch | grep '*' | sed -r 's/^\s*\*\s+(\S+)$/\1/' )

if [[ $BRANCH = "master" ]]
then
  git config user.name "Brian Skinn"
  git config user.email "brian.skinn@gmail.com"

  git add . && git commit -m "Update content - $( date -uIs )"
  if [[ $? -eq 0 ]]
  then
    git push https://bskinn@github.com/bskinn/flake8-bot
  fi
else
  echo "Not on master branch; skipping repo commit."
fi

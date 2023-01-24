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
  python create_tweets.py --post
else
  python create_tweets.py
fi

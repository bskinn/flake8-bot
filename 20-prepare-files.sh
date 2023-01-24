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

rm -f mdbuild/*
cd data
mv f8.list f8.list.old
unzip eps.json.zip
rm eps.json.zip
cp eps_ext.json eps_ext.json.old
cp eps_rep.json eps_rep.json.old
unzip rss.json.zip

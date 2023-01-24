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

python f8_list.py
cat data/f8_active.list | tr '\n' '  '

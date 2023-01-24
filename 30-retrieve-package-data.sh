#! /bin/bash

python f8_list.py
cat data/f8_active.list | tr '\n' '  '

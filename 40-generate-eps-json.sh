#! /bin/bash

./generate_eps_json || ( cat data/gen.log; exit 1 )
head -c80 data/*.json

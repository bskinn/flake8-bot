#! /bin/bash

rm -f mdbuild/*
cd data
mv f8.list f8.list.old
unzip eps.json.zip
rm eps.json.zip
cp eps_ext.json eps_ext.json.old
cp eps_rep.json eps_rep.json.old
unzip rss.json.zip

#!/usr/bin/env bash

#init ssh
eval $(ssh-agent)
chmod 600 /ssh/id_rsa
ssh-add /ssh/id_rsa
sleep 1 #Make sure ssh server has a chance to start
ssh -oStrictHostKeyChecking=no git@git-server date

#Run tests
coverage run /test_commit_report.py
coverage report -m --include /commit_report.py

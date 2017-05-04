#!/usr/bin/env bash

mkdir /var/run/sshd

exec /usr/sbin/sshd -D
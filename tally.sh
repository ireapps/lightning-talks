#!/bin/sh
while [ 1 ]; do
    . ~/.bash_profile && fab tally
    sleep 5
done
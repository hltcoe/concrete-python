#!/bin/bash
set -e
! egrep -r 'TODO|FIXME|HACK' concrete/util concrete/*.py \
                             scripts examples \
                             tests integration-tests

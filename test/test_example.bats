#!/usr/bin/env bash

# fixme: turn this into a bats test

export POCHOIR_STORE=$(mktemp -d /tmp/pochoir-example-XXXX)

set -e

pochoir example caps
pochoir fdm -n 10 --epoch=10 --precision 1 \
        -b caps-boundary \
        -i caps-initial \
        -e per,per \
        caps-solution caps-error

pochoir plot-image caps-initial caps-initial.pdf
pochoir plot-image caps-error caps-error.pdf
pochoir plot-image caps-solution caps-solution.pdf
pochoir plot-image caps-error caps-error.pdf
pochoir domain -o caps-domain -l caps-solution -- '-2.5:2.5' '0:1.67'
pochoir grad caps-solution caps-efield
pochoir plot-quiver caps-efield caps-efield.pdf

echo $POCHOIR_STORE


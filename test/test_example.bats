#!/usr/bin/env bash

# fixme: turn this into a bats test

pochoir example caps

pochoir fdm -n 10 --epoch=10 --precision 1 \
        -b caps-boundary \
        -i caps-initial \
        -e per,per \
        caps-solution caps-error

pochoir plot caps-initial caps-initial.pdf
pochoir plot caps-error caps-error.pdf
pochoir plot caps-solution caps-solution.pdf
pochoir plot caps-error caps-error.pdf

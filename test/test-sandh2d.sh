#!/bin/bash

set -e

tdir="$(dirname $(realpath $BASH_SOURCE))"

export POCHOIR_STORE="${1:-store-sandh2d}"

# for want*
source $tdir/helpers.sh

# ~/opt/jsonnet/bin/jsonnet -m store-sandh2d tutorial/sandh2d.jsonnet

for name in drift weight-col weight-ind
do

    want initial/$name \
         pochoir gen --generator sandh2d --domain domain \
         --initial initial/$name --boundary boundary/$name \
         "$POCHOIR_STORE/${name}.json"

    for flavor in initial boundary
    do
        want_file ${flavor}-${name}.png \
                  pochoir plot-image -a ${flavor}/${name} -o ${flavor}-${name}.png
    done
done

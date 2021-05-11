#!/usr/bin/env bash

# note, this test is intentionally imprecise so that it runs quickly

set -e
set -x

tdir="$(dirname $(realpath $BASH_SOURCE))"
sdir="$(dirname $tdir)"

if [ -n "$1" ] ; then
    POCHOIR_STORE="$1"
    keep="yes"
else
    POCHOIR_STORE=$(mktemp -d /tmp/pochoir-full-test-XXXXX)
    keep="no"
fi
export POCHOIR_STORE
echo "$POCHOIR_STORE"
export POCHOIR_CONFIG=$tdir

pochoir domain -s 84,56,1000 -S 0.03 pcb_domain

pochoir gen -d pcb_domain \
        -i pcb_init -b pcb_bound -g pcb_quarter \
        $POCHOIR_CONFIG/example_gen_pcb_quarter_config.json

pochoir fdm -n 10 --epoch=10 --precision 10 \
        -b pcb_bound \
        -i pcb_init \
        -e per,per,per \
        pcb_sol pcb_err

pochoir velo -d pcb_domain -r pcb_velo pcb_sol
    
pochoir starts -d pcb_domain -s pcb_starts 1.25,0.835,29.0 

pochoir drift -r pcb_drift -s 0,180000,500 \
        -d pcb_domain pcb_starts pcb_velo

pochoir domain -s 1092,2500 -S 0.1 pcb_2D_domain

pochoir gen -d pcb_2D_domain -i pcb_2D_init \
        -b pcb_2D_bound -g pcb_2D \
        $POCHOIR_CONFIG/example_gen_pcb_2D_config.json

pochoir fdm -n 10 --epoch=10 --precision 0.2 \
        -b pcb_2D_bound \
        -i pcb_2D_init \
        -e per,per \
        pcb_2D_sol pcb_2D_err
        
pochoir domain -s 350,66,2000 -S 0.1 pcb_3Dstrips_domain

pochoir gen -d pcb_3Dstrips_domain -i pcb_3Dstrips_init \
        -b pcb_3Dstrips_bound -g pcb_3D \
        $POCHOIR_CONFIG/example_gen_pcb_3D_config.json

pochoir bc-interp -s pcb_2D_sol -i pcb_3Dstrips_init \
        -b pcb_3Dstrips_bound \
        -d pcb_2D_domain -D pcb_3Dstrips_domain \
        pcb_3Dstrips_init_interp pcb_3Dstrips_bound_interp

pochoir fdm -n 10 --epoch=10 --precision 0.2 \
        -b pcb_3Dstrips_bound_interp \
        -i pcb_3Dstrips_bound_interp \
        -e per,per,per \
        pcb_3Dstrips_sol pcb_3Dstrips_err

if [ "$keep" = "no" ] ; then
    rm -rf "$POCHOIR_STORE"
fi






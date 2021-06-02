#!/bin/bash

set -e

#tdir="$(dirname $(realpath $BASH_SOURCE))"

export POCHOIR_STORE="${1:-store}"

source helpers.sh


## Domains ##
do_domain () {
    local name=$1 ; shift
    local shape=$1; shift
    local spacing=$1; shift

    want domain/$name \
         pochoir domain --domain domain/$name \
         --shape=$shape --spacing $spacing
}
do_domain drift3d  25,17,700  '0.1*mm'

# fixme: these weight* identifiers need to split up for N planes.
do_domain weight2d 1092,700   '0.1*mm'
do_domain weight3d 350,32,700 '0.1*mm'


## Initial/Boundary Value Arrays ##
do_gen () {
    local name=$1 ; shift
    local geom=$1; shift
    local gen="pcb_$geom"
    local cfg="example_gen_pcb_${geom}_config.json"

    want initial/$name \
         pochoir gen --generator $gen --domain domain/$name \
         --initial initial/$name --boundary boundary/$name \
         $cfg

}
do_gen drift3d quarter
do_gen weight2d 2D
do_gen weight3d 3D

## Fields
do_fdm () {
    local name=$1 ; shift
    local nepochs=$1 ; shift
    local epoch=$1 ; shift
    local prec=$1 ; shift
    local edges=$1 ; shift

    want potential/$name \
         pochoir fdm \
         --nepochs $nepochs --epoch $epoch --precision $prec \
         --edges $edges \
         --initial initial/$name --boundary boundary/$name \
         --potential potential/$name \
         --increment increment/$name
}
do_fdm drift3d  10      10000      0.02     per,per,fix
do_fdm weight2d 10      10      0.002   per,fix

# special step to form iva/bva from 2D solution
want initial/weight3dfull \
     pochoir bc-interp --xcoord '17.5*mm' \
     --initial initial/weight3dfull --boundary boundary/weight3dfull \
     --initial3d initial/weight3d --boundary3d boundary/weight3d \
     --potential2d potential/weight2d

do_fdm weight3dfull 10      10      0.002     fix,per,fix


want velocity/drift3d \
     pochoir velo --temperature '89*K' \
     --potential potential/drift3d \
     --velocity velocity/drift3d

want starts/drift3d \
     pochoir starts --starts starts/drift3d \
     '1.25*mm,0.835*mm,69*mm' '0.3*mm,0.1*mm,69*mm' '0.3*mm,0.37*mm,69*mm' '0.3*mm,0.64*mm,69*mm' 

want paths/drift3d \
     pochoir drift --starts starts/drift3d \
     --velocity velocity/drift3d \
     --paths paths/drift3d '0*us,4250*us,0.1*us'


want current/induced_current \
     pochoir induce --weighting potential/weight3dfull \
     --paths paths/drift3d \
     --output current/induced_current



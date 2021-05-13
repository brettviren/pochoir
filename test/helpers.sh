#!/bin/bash

want () {
    target="$1" ; shift
    if [ -f "$POCHOIR_STORE/${target}.npz" -o -f "$POCHOIR_STORE/${target}.npz" ] ; then
        echo "have $target"
        return
    fi
    echo "$@"
    $@
    if [ -f "$POCHOIR_STORE/${target}.npz" -o -f "$POCHOIR_STORE/${target}.npz" ] ; then
        echo "made $target"
        return
    fi
    exit -1
}
want_file () {
    target="$1" ; shift
    if [ -f "${target}" ] ; then
        echo "have $target"
        return
    fi
    echo "$@"
    $@
    if [ -f "${target}" ] ; then
        echo "made $target"
        return
    fi
    exit -1
}

#!/usr/bin/env bats

@test "generate sandh IVA/BVA" {
    tmpdir=$(mktemp -d /tmp/pochoir-test-gen-sandh-XXXX)
    echo "# output to $tmpdir" >&3

    cfg="$tmpdir/test-gen-sandh.json"
    echo "$cfg"

    run jsonnet -o $cfg $BATS_TEST_DIRNAME/test-gen-sandh.jsonnet
    echo "$output"
    [ "$status" -eq 0 ]
    [ -s "$cfg" ]
    
    export POCHOIR_STORE=$tmpdir/store

    pochoir domain --shape 1051,1051 --spacing 0.1 wfar
    echo "$output"
    [ "$status" -eq 0 ]
    [ -s "$tmpdir/store/wfar/origin.npz" ]
    [ -s "$tmpdir/store/wfar/shape.npz" ]
    [ -s "$tmpdir/store/wfar/spacing.npz" ]

    pochoir gen -d wfar -g sandh -i sandh-initial -b sandh-boundary $cfg
    echo "$output"
    [ "$status" -eq 0 ]
    [ -s "$tmpdir/store/sandh-initial.npz" ]
    [ -s "$tmpdir/store/sandh-boundary.npz" ]

    pochoir plot-image -d wfar sandh-initial $tmpdir/sandh-initial.pdf
    echo "$output"
    [ "$status" -eq 0 ]
    [ -s "$tmpdir/sandh-initial.pdf" ]

    pochoir plot-image -d wfar sandh-boundary $tmpdir/sandh-boundary.pdf
    echo "$output"
    [ "$status" -eq 0 ]
    [ -s "$tmpdir/sandh-boundary.pdf" ]

    rm -rf "$tmpdir"
}

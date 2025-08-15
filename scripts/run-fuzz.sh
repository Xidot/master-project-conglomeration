#!/bin/env bash

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))
FUZZING_DIR=$(realpath $THIS/../experiments/fuzzing)

pushd $FUZZING_DIR;

# This is a dry compilation run
SRC_DIR=quickjs-print ./fuzz.sh -f

popd;

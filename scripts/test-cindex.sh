#!/bin/env bash

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))
FUZZING_DIR=$(realpath $THIS/../experiments/fuzzing)

pushd $FUZZING_DIR;

# This is a dry compilation run
./analyze.sh

popd;

#!/bin/env bash

set -e

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))
FUZZING_DIR=$(realpath $THIS/experiments/fuzzing)

popd $FUZZING_DIR;

# This is a dry compilation run
./fuzz.sh

pushd;

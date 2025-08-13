#!/bin/env bash

set -e

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))

PATCH_DIR="$(realpath $THIS/patches)"

DO_INSTALL=0

# TODO openai env key to set here - doc in readme
# TODO Install requirements with venv creation

# Initialize foreign source code
git submodule init && git submodule update

# Apply patches
pushd oss-fuzz;
    git apply --3way $PATCH_DIR/oss-fuzz.diff 
popd;

# The names are used by sub scripts
pushd experiments/fuzzing;
    cp -r quickjs quickjs-base;
    cp -r quickjs-base quickjs-abort;
    cp -r quickjs-base quickjs-nop;
    cp -r quickjs-base quickjs-print;

    pushd quickjs-abort;
    git apply --3way $PATCH_DIR/quickjs-abort.diff;
    popd;

    pushd quickjs-nop;
    git apply --3way $PATCH_DIR/quickjs-nop.diff;
    popd;

    pushd quickjs-print;
    git apply --3way $PATCH_DIR/quickjs-print.diff;
    popd;
popd;

# init submodules
#   quickjs 
#   oss-fuzz
# install clang20
# you must install docker!
# init python venv

if [ ! -d "./venv" ]; then
    python -m venv venv
    DO_INSTALL=1
fi

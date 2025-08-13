#!/bin/env bash

# Content based off quickjs of 458c34d29d0d262f824ea1c0e01aa0e3790669da - master

PREFIX="$(realpath $(dirname $0))/gen"

TEST='JS_FreeAtom(JSContext *, JSAtom)'
ENTRY='LLVMFuzzerTestOneInput(const uint8_t *, size_t)'

PROJECT=./quickjs-base

# Compute all functions used by the specified entry point for usage
function run_listing() {
    pushd $PROJECT;
    cindex.py \
        --prepare \
        --prefix "$PREFIX" \
        --lookup "$1" \
        compile_commands.json \
        -I/usr/lib/clang/20/include \
        -fparse-all-comments \
        -Wno-incompatible-pointer-types
    popd;
}

function run_cg() {
    pushd $PROJECT;
    cindex.py --prefix "$PREFIX" --cg --depth 1 \
        --lookup "$1" \
        compile_commands.json \
        -I/usr/lib/clang/20/include \
        -fparse-all-comments \
        -Wno-incompatible-pointer-types
    popd;
}

function run_compile() {
    pushd $PROJECT;
    cindex.py \
        --lookup "$1" --prefix "$PREFIX" \
        compile_commands.json \
        -I/usr/lib/clang/20/include \
        -fparse-all-comments \
        -Wno-incompatible-pointer-types
    popd;
}

# Requires prepare to exist. It is created by run_listing().
function run_compile_all() {
    pushd $PROJECT;
    cindex.py --lookup "dummy" --prefix "$PREFIX" \
        --multi-lookup "$PREFIX/prepare" \
        compile_commands.json \
        -I/usr/lib/clang/20/include \
        -fparse-all-comments \
        -Wno-incompatible-pointer-types
    popd;
}

if [ ! -f "$PREFIX/prepare" ]; then
    run_listing "$ENTRY"
fi

# Will compile multiple user prompts, one for each line in "gen/prepare"
run_compile_all

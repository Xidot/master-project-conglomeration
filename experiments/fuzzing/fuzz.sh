#!/bin/env bash

set -e

# Salvaged options from oss-fuzz

export AFL_DEBUG=1
export AFL_SKIP_CPUFREQ=1
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
export AFL_TRY_AFFINITY=1
export AFL_IGNORE_UNKNOWN_ENVS=1
export AFL_FUZZER_ARGS='-m none -t 5000+'
export AFL_CMPLOG_ONLY_NEW=1
export AFL_FAST_CAL=1
export AFL_IGNORE_PROBLEMS=1
export AFL_FORKSRV_INIT_TMOUT=30000
export AFL_IGNORE_UNKNOWN_ENVS=1
export AFL_QUIET=1
export AFL_IGNORE_PROBLEMS=1

export ASAN_OPTIONS="$ASAN_OPTIONS:abort_on_error=1:symbolize=0:detect_odr_violation=0:"
export MSAN_OPTIONS="$MSAN_OPTIONS:exit_code=86:symbolize=0"
export UBSAN_OPTIONS="$UBSAN_OPTIONS:symbolize=0"
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
export AFL_SKIP_CPUFREQ=1
export AFL_TRY_AFFINITY=1
export AFL_FAST_CAL=1
export AFL_CMPLOG_ONLY_NEW=1
export AFL_FORKSRV_INIT_TMOUT=30000
export AFL_IGNORE_PROBLEMS=1
export AFL_IGNORE_UNKNOWN_ENVS=1

SCRIPT_DIR=$(realpath $(dirname $0))
SRC=${SRC_DIR:-$SCRIPT_DIR/quickjs}
FUZZER=${FUZZER:-fuzz_compile}
FUZZER_OUT=${FUZZER_OUT:-./out}
FUZZER_IN=${FUZZER_IN:-./in}
CORPUS_DIR=${CORPUS_DIR:-corpus/js/}

DO_FUZZ=

# COMPILATION
CC=afl-clang-fast
CXX=afl-clang-fast++

CFLAGS="-O1
    -fno-omit-frame-pointer
    -gline-tables-only
    -Wno-error=enum-constexpr-conversion
    -Wno-error=incompatible-function-pointer-types
    -Wno-error=int-conversion
    -Wno-error=eprecated-declarations
    -Wno-error=implicit-function-declaration
    -Wno-error=implicit-int
    -Wno-error=vla-cxx-extension
    -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
    -fsanitize=address -fsanitize-address-use-after-scope"

CXXFLAGS="-O1
    -fno-omit-frame-pointer
    -gline-tables-only
    -Wno-error=enum-constexpr-conversion
    -Wno-error=incompatible-function-pointer-types
    -Wno-error=int-conversion
    -Wno-error=deprecated-declarations
    -Wno-error=implicit-function-declaration
    -Wno-error=implicit-int
    -Wno-error=vla-cxx-extension
    -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
    -fsanitize=address
    -fsanitize-address-use-after-scope
    -stdlib=libc++"

mkdir -p $FUZZER_OUT
mkdir -p $FUZZER_IN

# afl needs one file with input
echo input > ./in/input

if [ "$1" = "-f" ]; then
    DO_FUZZ=1
fi

build_fuzz_target () {
    local target=$1
    shift
    $CC $CFLAGS -I. -c fuzz/$target.c -o $target.o
    $CXX $CXXFLAGS $target.o -o $SRC/$target $@ $LIB_FUZZING_ENGINE
}

# This is soely used to test that the program can compile
# Options extracted from the fuzzer compilation scripts
function try_compile() {
    pushd $SRC;

    make clean;

    # sed -i -e 's/CFLAGS=/CFLAGS+=/' Makefile
    # sed -i -e 's/#define USE_WORKER/\/\/#define USE_WORKER/' quickjs-libc.c
    CFLAGS="-Wno-error=incompatible-function-pointer-types" CONFIG_CLANG=y make libquickjs.fuzz.a .obj/fuzz_common.o .obj/libregexp.fuzz.o .obj/cutils.fuzz.o .obj/libunicode.fuzz.o
    # zip -r $OUT/fuzz_eval_seed_corpus.zip $SRC/quickjs-corpus/js/*.js
    # zip -r $OUT/fuzz_compile_seed_corpus.zip $SRC/quickjs-corpus/js/*.js


    # build_fuzz_target fuzz_eval .obj/fuzz_common.o libquickjs.fuzz.a
    build_fuzz_target fuzz_compile .obj/fuzz_common.o libquickjs.fuzz.a
    # build_fuzz_target fuzz_regexp .obj/libregexp.fuzz.o .obj/cutils.fuzz.o .obj/libunicode.fuzz.o

    popd;
}

# This uses the oss docker containers to build and yoink the binary
# It uses the quickjs folder in this folder.
function oss_compile() {
    OSS_DIR=../../oss-fuzz
    OSS_PROJ_DIR=../../oss-fuzz/projects/quickjs
    OSS_BUILD_DIR=../../oss-fuzz/build/out/quickjs

    rsync -rav $SRC/ $OSS_PROJ_DIR/quickjs

    pushd $OSS_DIR;
    ./infra/helper.py build_fuzzers quickjs --engine afl
    popd;

    cp $OSS_BUILD_DIR/$FUZZER $SRC/$FUZZER
}

if [ ! -f "$SRC/$FUZZER" ]; then
    # try_compile # check if it compiles
    oss_compile
fi

if [ ! -d "$FUZZER_IN/corpus" ]; then
    git clone https://github.com/renatahodovan/quickjs-corpus.git "$FUZZER_IN/$CORPUS_DIR"
fi

# Don't go into fuzzing if -f not specified
# Useful for only compiling
if [ -z "$DO_FUZZ" ]; then
    exit 0
fi

# bind to last CPU for least usage
BIND_CPU=23
CMD_LINE="afl-fuzz -b $BIND_CPU  $AFL_FUZZER_ARGS -x $SRC/fuzz/fuzz.dict -i "$FUZZER_IN/$CORPUS_DIR" -o $FUZZER_OUT $* -- $SRC/$FUZZER 2> $FUZZER_OUT/log"

echo afl++ setup:
env|grep AFL_

echo $CMD_LINE

bash -c "$CMD_LINE"

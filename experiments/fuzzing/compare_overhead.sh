#!/bin/env bash

# die on err
set -e

# This script compiles the three versions and runs hyperfine for each one. A -
# uses nop instructions to only measure the overhead of the new comparisons. C
# - uses the printf instructions to see how much slower the instrumentation is
# with the syscalls.

A_DIR=./quickjs
B_DIR=./quickjs-base
C_DIR=./quickjs-nop

A_BIN=$A_DIR/fuzz_compile
B_BIN=$B_DIR/fuzz_compile
C_BIN=$C_DIR/fuzz_compile

# compile both binaries
rm -f $A_BIN && SRC_DIR=$A_DIR ./fuzz.sh
rm -f $B_BIN && SRC_DIR=$B_DIR ./fuzz.sh
rm -f $C_BIN && SRC_DIR=$C_DIR ./fuzz.sh

for f in ./in/corpus/js/*; do
    echo "$f"
    filename=$(basename "$f")
    stem=${filename%.*}
    hyperfine -i "$A_BIN $f" -M 100 -w 50 --export-json "./gen/inst_$stem.dat"
    hyperfine -i "$B_BIN $f" -M 100 -w 50 --export-json "./gen/base_$stem.dat"
    hyperfine -i "$C_BIN $f" -M 100 -w 50 --export-json "./gen/print_$stem.dat"
done


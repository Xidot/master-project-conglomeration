#!/bin/env bash

PROJECT=./quickjs-base

pushd $PROJECT;

CFLAGS+=-Wno-incompatible-pointer-types CONFIG_CLANG=y CONFIG_ASAN=y bear -- make libfuzzer

popd;


#!/bin/env bash

set -e

USAGE="Usage: $0 patchfile-1 patchfile-2 ..."

if [ "$#" -lt 1 ]; then
    echo "$USAGE"
    exit 1
fi

args=($*)

total=0
for patch in "${args[@]}"; do
    num=$(grep -E "^@@.*@@$" $patch | wc -l)
    echo -e "$num\t$patch"
    (( total += num ))
done

echo "$total total"

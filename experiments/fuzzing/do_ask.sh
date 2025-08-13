#!/bin/env bash

CWD=`pwd`

# Extract patches from the responses
function strip_diff() {
   sed -n '/```diff/,/```$/ { /```diff$/!p; }' | sed '/```$/d'
}

num=0
for i in ./gen/prompt-*; do
    lines="$(wc -l "$i")"
    echo -e "$lines"
    res=$(ask.py "$i" ../../prompts/system.fullex-alt)
    echo "$res" > "./gen/res-$num"
    echo "$res" | strip_diff "$res" >> "./gen/patch-$num"
    (( num += 1 ))
done

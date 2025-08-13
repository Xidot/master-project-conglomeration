#!/bin/env bash

THIS=$(dirname $(realpath ${BASH_SOURCE%/*}))

# TODO openai env key to set here - doc in readme
# TODO Install requirements with venv creation

if [ ! -d "./venv" ]; then
    python -m venv venv
fi

echo "Relative to $THIS"

export PATH="$PATH:$THIS/scripts"
source $THIS/venv/bin/activate


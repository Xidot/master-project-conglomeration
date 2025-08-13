#!/bin/env bash

# Setup the environment for the scripts and tools to be in path

set -e

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))

export PATH="$PATH:$THIS/scripts"
source $THIS/venv/bin/activate


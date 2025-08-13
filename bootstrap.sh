#!/bin/env bash

# Setup the environment for the scripts and tools to be in path

# set -e

THIS=$(dirname $(realpath ${BASH_SOURCE[0]}))

# TODO: FILL THESE IN
export LLM_KEY="${LLM_KEY:-`cat llm_key`}" 
export LLM_BASEURL="${LLM_BASEURL:-https://api.deepseek.com}"

# Other requirements
export PATH="$PATH:$THIS/scripts"
source $THIS/venv/bin/activate


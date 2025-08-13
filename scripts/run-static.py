#!/bin/env python

import sys, os, subprocess
from subprocess import Popen
import shlex

PROMPTS_PATH=os.path.realpath("../prompts")
TOOL_PATH=os.path.realpath("./cindex.py")
ASK_PATH=os.path.realpath("./ask.py")
# Necessary to parse comments and workaround C20 stddef.h
CLANG_FLAGS="-I/usr/lib/clang/20/include -fparse-all-comments"

# Experiments directory, cindex.py assumes it is in the same directory
STATIC_PATH=os.path.realpath("../experiments/static/")
OUTPUT_FILE=os.path.realpath("../experiments/static/static.log")

# Hand made list of what functions to search for under experiments/static/examples.c
symbols = [ 
    "sum_00(int *, size_t)",
    "sum_01(int *, size_t)",
    "sum_02(int *, size_t)",
    "sum_03(int *, size_t)",
    "sum_04(int *, size_t)",
    "obz_00(int *, size_t)",
    "unit_00(int, int)",
    "unit_01(int, int)",
    "unit_02(int, int)",
    "unit_03(int, int)",
    "cond_00(char *)",
    "cond_01(char *)",
    "cond_03(char *)",
    "bool_00(int)",
    "bool_01(int)",
]

system_prompts = [
    "system.vague",
    "system.empty",
    "system.full",
    "system.forcebug",
]

ANALYZE_CMD=lambda sym: f"python {TOOL_PATH} examples.c --lookup '{sym}' {CLANG_FLAGS}"
PROMPT_FILE=lambda sym: f"prompt-{sym}"
ASK_CMD=lambda usr, sys: f"python {ASK_PATH} '{usr}' '{sys}'"

# Run an analysis and ask process for each symbol in the fake tests
# Output must be inspected manually
# This just reproduces what was initially done manually
outfile = open(OUTPUT_FILE, "w")
for sym in symbols:
    analyze_cmd = shlex.split(ANALYZE_CMD(sym))
    analyze_process = subprocess.run(analyze_cmd, cwd=STATIC_PATH)
    if analyze_process.returncode != 0:
        print("[!] Error")
        exit(1)

    # Run with each system prompt
    for prompt in system_prompts:
        prompt_path=os.path.join(PROMPTS_PATH, prompt)

        # assemble and run the command to ask the LLM
        ask_cmd = shlex.split(ASK_CMD(PROMPT_FILE(sym), prompt_path))
        ask_process = subprocess.run(ask_cmd, cwd=STATIC_PATH, stdout=subprocess.PIPE)
        if ask_process.returncode != 0:
            print("[!] Error")
            exit(1)

        # Save output to file for review
        outfile.write("==================================================\n")
        outfile.write(ask_process.stdout.decode('utf-8'))
        outfile.write("\n")


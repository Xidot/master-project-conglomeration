#!/bin/env python

import sys, os
import subprocess
import shlex

PROMPTS_PATH=os.path.realpath("../../prompts")
ASK_PATH=os.path.realpath("../../scripts/ask.py")

SYSTEM_PROMPT=os.path.join(PROMPTS_PATH, "system.full")
TEST_COUNT = 10
CLANG_FLAGS="-I/usr/lib/clang/20/include -fparse-all-comments"

ASK_CMD=lambda usr, sys: f"python {ASK_PATH} '{usr}' '{sys}'"

TESTS=[
    {
        "name": "shortest-path",
        "user-prompt": "./prompt-1",
        "sys-prompt": SYSTEM_PROMPT,
    },
    {
        "name": "bad-recursion",
        "user-prompt": "./prompt-2",
        "sys-prompt": SYSTEM_PROMPT,
    },
    {
        "name": "cutsets-incomplete",
        "user-prompt": "./prompt-3",
        "sys-prompt": SYSTEM_PROMPT,
    },
    {
        "name": "dice-similarity",
        "user-prompt": "./prompt-4",
        "sys-prompt": SYSTEM_PROMPT,
    },
    {
        "name": "bad-tree-remove",
        "user-prompt": "./prompt-5",
        "sys-prompt": SYSTEM_PROMPT,
    },
]

if __name__ == '__main__':
    for test in TESTS:
        ask_cmd = shlex.split(ASK_CMD(test['user-prompt'], test['sys-prompt']))
        # create logs
        log_file = open(f"{test['name']}.log", "w")
        for i in range(0, TEST_COUNT):
            run_process = subprocess.run(ask_cmd, stdout=subprocess.PIPE)
            if run_process.returncode != 0:
                print("[!] Error")
                exit(1)

            log_file.write("==================================================\n")
            log_file.write(run_process.stdout.decode('utf-8'))
            log_file.write("\n")
            print(f"[+] Done {test['name']} | #{i}")

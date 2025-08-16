#!/bin/env python

import os, sys, json

filter_set = ["fuzz_eval", "fuzz_regexp"]

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} compile_commands.json")
    exit(1)

filename = sys.argv[1];

print(f"Reading: {filename}")
with open(filename, "r") as file:
    data = json.load(file);
    for el in data:
        if el and "file" in el:
            print(el["file"])
            for filter in filter_set:
                print(el["file"])
                if filter in el["file"]:
                    data.remove(el)
                    break

with open(filename, "w") as file:
    json.dump(data, file, indent=4)

print("[+] Done removing the other fuzzers!")

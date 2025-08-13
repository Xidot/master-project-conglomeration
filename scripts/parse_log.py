#!/bin/env python3

import os, sys, io, signal
from matplotlib import pyplot as plt
import time
import multiprocessing as mp
import re, json
import threading
import queue

data_point_pat = r'.*\.\w+:\d+$'

# Note: There was a hastily stitched concurrent version which was not worth the
# debugging

def read_args():
    if len(sys.argv) != 2:
        print(f"{sys.argv[0]}: <fuzz log file>")
        exit(1)
    return sys.argv[1]

# Match our data points
def validate_line(line: str) -> tuple|None:
    line = line.strip()
    if not line or ":" not in line:
        return None

    # Wide pattern
    match = re.match(data_point_pat, line)
    if not match:
        return None
    parts = line.split(":")
    parts[0] = os.path.basename(parts[0])
    return f"{parts[0]}:{parts[1]}"

def merge_hits(lhs, rhs):
    for key in rhs.keys():
        if key in lhs:
            lhs[key] += rhs[key]
        else:
            lhs[key] = rhs[key]
    return lhs

def read_lines(handle: io.TextIOWrapper, hint=1<<21):
    return handle.readlines(hint)

def parse_file(filename):
    hits = {}
    print(f"Opening {filename}")
    file_handle = open(filename, "r");
    file_size = os.path.getsize(filename)

    start_t = time.perf_counter_ns();

    lines = read_lines(file_handle)
    while lines:
        for line in lines:
            ret = validate_line(line)
            if not ret:
                continue
            if ret not in hits:
                hits[ret] = 1;
            else:
                hits[ret] += 1;
            progress_report(1000000, f"{(file_handle.buffer.tell() / file_size) * 100:.5f}%")

        if STOPALL:
            break;
        lines = read_lines(file_handle)

    end_t = time.perf_counter_ns();

    print(hits)
    print(f"{(end_t - start_t)/ 10**9:.5f}s |{(file_handle.buffer.tell() / file_size) * 100:.5f}%")
    with open("log-data.json", "w") as file:
        json.dump(hits, file_handle)

def main():
    filename = read_args();
    parse_file(filename)

if __name__ == '__main__':
    main()

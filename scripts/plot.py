#!/bin/env python

from matplotlib import pyplot as plot
import json, glob
import sys, os

# Note these were manually counted so we might have missed a few out of ~1500
# code changes.
total_patches = 1563
rejects = 217
surviving = total_patches - rejects

redundant = 71
changed_behavior = 57

labels = [
    'Existing error path',
    'Changed behavior',
    'Invalid predicate',
    'Broken syntax',
    'Dead code',
    'Other',
    # 'Corrupted patches/hallucinated',
    # 'Null deref',
    # 'Duplicate',
    # 'Use-after-free in predicate',
    # 'Only refactored code',
    # 'Inserted inside structs or if statements',
    # Commented out to not pollute the graph
]

sizes = [
    71,
    58,
    31,
    35,
    8, # dead code
    6+ # hallucinated patch lines
    2+ # null deref
    2+ # dups
    2+ # use after free
    1+ # refactor
    1, # inserted
]

def plot_rejects():
    fig, ax = plot.subplots()
    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        explode=[0.05 for x in sizes],
        pctdistance=0.85
    )

    # plot.show()
    plot.savefig("img/pie-rejects.pdf")

def plot_bar_patches():
    plot.title("Patch success")
    bars = plot.bar(['Applied', "Rejected"], [surviving, rejects])
    plot.bar_label(bars, [surviving, rejects], label_type='center')
    plot.ylabel("# Changes")
    plot.savefig("img/num-changes.pdf")
    # plot.show()

def parse_overhead_data(pat):
    results = []
    for i in glob.glob(pat):
        print(i)
        with open(i, "r") as file:
            j = json.load(file)
            results.append(j)
    return results

def calc_increase(start, final):
    return (final - start) / abs(start) * 100

def plot_overhead():
    title = "Runtime comparison of instrumented vs non-intrumented fuzzer"
    fig, ax = plot.subplots()

    if len(sys.argv) != 2:
        print("Give me folder")
        exit(1)

    dir = os.path.realpath(sys.argv[1])

    percent_labels = ["Nop instrumentd", "Print Instrumented"]

    # note pattern 1 and 3 are swapped by accident in the initial script
    pattern = os.path.join(dir, "inst_*")
    pattern_2 = os.path.join(dir, "base_*")
    pattern_3 = os.path.join(dir, "print_*")

    set_print = parse_overhead_data(pattern)
    set_base = parse_overhead_data(pattern_2)
    set_inst = parse_overhead_data(pattern_3)

    # Ordered by glob, they match
    inst_times  = []
    base_times  = []
    print_times = []

    mean_inst = 0
    max_inst = 0
    stddev_inst = 0
    for run in set_inst:
        mean_inst += run['results'][0]['mean']
        max_inst = run['results'][0]['max']
        stddev_inst += run['results'][0]['stddev']
        inst_times.append(run['results'][0]['mean'])

    mean_base = 0
    max_base = 0
    stddev_base = 0
    for run in set_base:
        mean_base += run['results'][0]['mean']
        max_base += run['results'][0]['max']
        stddev_base += run['results'][0]['stddev']
        base_times.append(run['results'][0]['mean'])

    mean_print = 0
    max_print = 0
    stddev_print = 0
    for run in set_print:
        mean_print += run['results'][0]['mean']
        max_print += run['results'][0]['max']
        stddev_print += run['results'][0]['stddev']
        print_times.append(run['results'][0]['mean'])

    # Compute percentages compared to base per run

    # First inst vs base
    diffs_inst = []
    for base,inst in zip(base_times, inst_times):
        diffs_inst.append(calc_increase(base, inst))

    # Second inst vs print
    diffs_print = []
    for base,print_t in zip(base_times, print_times):
        diffs_print.append(calc_increase(base, print_t))

    print(f"inst: {mean_inst} base: {mean_base} print: {mean_print}")

    diffs_inst = sum(diffs_inst) / len(diffs_inst)
    diffs_print = sum(diffs_print) / len(diffs_print)
    print(f"perc inst: {diffs_inst} perc print: {diffs_print}")

    # Arrange sets by time
    # for label,val,stddev in zip(
    #     ["Base binary", "Nop instrumented", "Print instrumented"],
    #     [mean_base, mean_inst, mean_print],
    #     [stddev_base, stddev_inst, stddev_print],
    # ):
    #     p = ax.bar(label, val, yerr=stddev)
    #     ax.bar_label(p, label_type='center')

    for label,perc in zip(percent_labels, [diffs_inst, diffs_print]):
        p = ax.bar(label, perc)
        ax.bar_label(p, label_type='center', fmt="%.2f%%")

    ax.set_ylabel('Mean (%) difference')
    ax.set_title(title)
    plot.savefig("img/overhead-percent.pdf")
    # plot.show()

# This plots experiments/fuzzing/gen/results-fuzzing.json
# It in itslef is a json containing frequence hit data for a key made up of
# FILE:LINE combo
# This combo let's us create a cursor which let's us automatically get the
# source code with the if statement if any out and map them into a diagram which
# let's us analyze the hits vs source code
def plot_inst_freq():
    if len(sys.argv) != 2:
        print("I need a json file!")
        exit(1)

    data = None
    try:
        with open(sys.argv[1], "r") as file:
            b = file.read()
            data = json.loads(b)
    except json.JSONDecodeError as e:
        print(f"Bad json {e}")
        exit(1)

    figs, ax = plot.subplots()

    # Sort each file by line number
    data_arr = []
    for d in data.keys():
        file, line = d.split(":")
        data_arr.append({
            'name': f"{file}:{line}",
            'hit_num': data[d]
        });

    def sort_by_name(a):
        return a['name']
    def sort_by_hits(a):
        return a['hit_num']

    plot.rcParams['font.size'] = 4
    data_arr = sorted(data_arr, key=sort_by_hits)
    for idx,d in enumerate(data_arr):
        ax.bar(idx, d['hit_num'], log=True, width=.8)
    print(f"{len(data_arr)} unique hits")

    # also save a file with the sorted keys for cindex
    with open("img/keys.txt", "w") as file:
        for dat in data_arr:
            file.write(f"{dat['name']}\n")

    plot.xticks(rotation=90)
    plot.xlabel("Instrumentations")
    plot.ylabel("Number of hits")
    # plot.tight_layout()
    plot.savefig("img/hit_num_per_file_hits_asc.pdf")
    # plot.show()

if __name__ == '__main__':
    plot_rejects()
    plot_bar_patches()
    plot_overhead()
    plot_inst_freq()
    pass

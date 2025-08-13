
This directory houses the fuzzing scripts and code used in evaluation. The
structure is the following:

```
experiments/fuzzing
├── README.md
├── analyze.sh
├── base-quickjs
├── compare_overhead.sh
├── do_ask.sh
├── fuzz.sh
├── gen
├── in
├── out
├── out.old
├── out.old2
├── out2
├── prepare.old
├── quickjs-abort
├── quickjs-base
├── quickjs-nop
├── quickjs-print
├── scratch
└── thepatch.old

12 directories, 8 files
```

`in/ & out/` are the default AFL++ folders. `out/` holds the AFL++ state and
can be used to resume the fuzzing which was stopped before writing the paper.

`in/` holds the corpus used by quickjs fuzzer which is pulled from a github
repository.

`gen/` holds all generated content using the project tools. Any data is
gathered here, the prompts and LLM responses included. It also houses the
`prepare` file that holds the list of functions to prepare prompts for.

`*.old` files are old files and results, left in initially as a backup, which
now are there for posterity.

`analyze.sh` uses `cindex.py` to compute callgraphs and generate prompts. If
`gen/prepare` does not exist it first computes the `prepare` file with a depth
first call graph search. `prepare` is needed to speedup the prompt generation
significantly through batching.

`fuzz.sh` copies the project into OSS-fuzz and uses that infrastructure to
compile the binary used in the fuzzing. NOTE: `fuzz.sh` will not fuzz. Run
`fuzz.sh -f` to proceed to fuzzing after a successfull compilation.

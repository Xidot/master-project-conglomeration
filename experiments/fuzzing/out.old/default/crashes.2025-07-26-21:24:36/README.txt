Command line used to find this crash:

afl-fuzz -b 23 -m none -t 5000+ -x /home/sproid/_workspace/vu/proj-master/experiments/fuzzing/quickjs/fuzz/fuzz.dict -i ./in/corpus/js/ -o ./out -- /home/sproid/_workspace/vu/proj-master/experiments/fuzzing/quickjs/fuzz_compile

If you can't reproduce a bug outside of afl-fuzz, be sure to set the same
memory limit. The limit used for this fuzzing session was 0 B.

Need a tool to minimize test cases before investigating the crashes or sending
them to a vendor? Check out the afl-tmin that comes with the fuzzer!

Found any cool bugs in open-source tools using afl-fuzz? If yes, please post
to https://github.com/AFLplusplus/AFLplusplus/issues/286 once the issues
 are fixed :)


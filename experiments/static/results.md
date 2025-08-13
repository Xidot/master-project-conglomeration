
sum_00 : overflow, overflow, overflow
sum_01 : uninit, uninit*, uninit*
sum_02 : arr==null x 3
sum_03 : assign, assign, assign
sum_04 : index (but bad instrum.), index, index  
unit_00 : div by zero, div by zero, div by zero
unit_01 : incorrect units, incorrect units, incorrect units
unit_02 : masking return, masking return, masking return
cond_00 : function return 0 on NULL or empty x 3
cond_01 : incorrect NULL check x 3
cond_02 : incorrect check x 3
cond_03 : incorrect size check x 3
bool_00 : incorrect boolean logic because it assumed CPP 
bool_01 : detected incorrect bitwise not

By this we show how many false positives are given for a prompt. We compare
different levels of prompt context. Later we try not including comments to see
if the fpr changes.

Takes 4 with different prompts per function:
- **vague**    : tasks finding _possible_ bugs
- **empty**    : no context and forces a bug
- **full**     : persona, context, formatting specifier, explicit logical bugs reference, add instrumentation
- **forcebug** : tell me where bugs are, context and formatting specifier

True positives are identifying the correct bug line False positives are things
that are identified as possible bugs but are not necessarily things that could
happen given the correct context. False negatives are non-identified true
posittives for a prompt, so the bug is ignored in our examples.

We have 15 functions, out of which 4 are control functions that do not contain
a logiclaly true positive. For each function we can get multiple results, but
contains 1 real issue. So to calculate the we use a confusion matrix: TPR = TP
/ FN, FP = FP / FP + TN

Each function either has a true positive or not, but multiple issues can be
identified. Each false positive is only classified as such because we are not
looking for it, but the result can be meaningful if the context changes. It is
true that some of the false positives are possible bugs if this was not an
in-situ test or each function was, in fact, used in production code.

We consider the mention of the line and the bug as an answer. If the target
line is mentioned then it is a true positive (TP). If it is not mentioned, then
it is considered a false negative. If a any other line is mentioned as a bug in
this context, then we consider the response as a false positive. However, these
are not necessarily wrong bugs. We aim to see how often the LLM will find the
bugs we are targetting. If the control function does not have the bug condition
named then it is a true negative.

For a given test, if the line where the bug is not specifiec then it is
considered a false negative.

unrelated comments, true positive, true negative

out of those 15 functions each prompt identified:
.vague    : fp 4 + 1 + 2 + 1 + 
.empty    :
.full     :
.forcebug :

sum_00 - control
.vague      : size_t cannot be less than zero, not graceful, overflow risk, complains about undocumented behaviour
4 fp
.empty      : missing inlcudes, error handling approach, possible overflow, size type mismatch, documentation mismatch
~5 fp
.full       : overflow
1 fp
.forcebug   : 2 the dramatic exit(1), size_t cannot be less than 0
2 fp

sum_01 - uninit
.vague      : uninitialised, overflow
1 tp, 1 fp
.empty      : uninitialised, overflow
1 tp, 1 fp
.full       : uninitialised, size cannot be negative
1 tp, 1 fp
.forcebug   : uninitialised, size cannot be negative
1 tp, 1 fp

sum_02 - indirect size of array usage
.vague      : no arr == null, index overflow possible
2 fp
.empty      : duplicate typedef, overflow on sum, redundant check of size (bcz loop won't execute otherwise)
3 fp
.full       : no null check, compare against 1 not zero
2 fp
.forcebug   : no null check, type mismatc i to helper
2 fp

sum_03 - wrong assignment
.vague      : return zero, sum overwritten
1 tp, 1 fp
.empty      : overwrite
1 tp
.full       : overwrite
1 tp
.forcebug   : overwrite
1 tp

sum_04 - add index contrary to comment
.vague      : return zero, adds i instead of arr[i]
1 tp, 1 fp
.empty      : adds i instead of member, int overflow
1 tp, 1 fp
.full       : adds i instead of member
1 tp
.forcebug   : return zero, adds i instead of member
1 tp, 1 fp

unit_00 - units control
.vague      : not handle negative
1 fp
.empty      : integer division, return type, negatives unhandled, doc inconsistency?
4 fp
.full       : masking return by zero (div by zero)
1 fp
.forcebug   : masking return by zero
1 fp

unit_01 - incorrect units by variable name
.vague      : div zero, incorrect calc
2 fp
.empty      : div zero, incorrect units (var names), unused doc
3 fp
.full       : incorrect units
1 tp
.forcebug   : incorrect units
1 tp

unit_02 - vagues units by var naming both
.vague      : lost precision, negative case
2 fp
.empty      : div by zero, precision loss, naming issues, masking return by zero, negative results
1 tp, 4 fp
.full       : masking error (div by zero)
1 fp
.forcebug   : negative dist not meaningful
1 fp

unit_03 - vagues units by var naming for time
.vague      : incorrect units
1 tp
.empty      : incorrect docs, masking div by zero, precision, no overflow check
4 fp
.full       : precision loss
1 fp
.forcebug   : precision loss
1 fp

cond_00 - control
.vague      : could be simplified
1 fp
.empty      : thread-safety??
1 fp
.full       : ret 0 intended?
1 fp
.forcebug   : ret 0 unintended??
1 fp

cond_01 : incorrect NULL check
.vague      : assignment
1 tp
.empty      : assignment, redundant strlen, misleading comment
1 tp, 2 fp
.full       : assignment
1 tp
.forcebug   : assignment
1 tp

cond_02 : incorrect streln check
.vague      : incorrect check
1 tp
.empty      : incorrect check, buffer overflow, inconsistent behavior
1 tp, 2 fp
.full       : incorrect check
1 tp
.forcebug   : incorrect check
1 tp

cond_03 : inverted logic - alludes consequences
.vague      : incorrect check
1 tp
.empty      : incorrect check, buffer overflow
1 tp, 1 fp
.full       : incorrect check
1 tp
.forcebug   : incorrect check
1 tp

bool_00 : boolean logic
.vague      : too ambiguous
1 fp
.empty      : too ambiguous, naming issues, ambiguous, bug is mismatch in logic
1 fp, 3 fp
.full       : no meaningful operation
1 fp
.forcebug   : no meaningful output
1 fp

bool_01 : bitwise instead of logical ops
.vague      : bitwise NOT
1 tp
.empty      : bitwise NOT, return type mismatch, inconsistent docs
1 tp, 2 fp
.full       : bitwise NOT
1 tp
.forcebug   : bitwise NOT
1 tp

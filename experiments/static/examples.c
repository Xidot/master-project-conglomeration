#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/**
 * This file includes unit tests for LLM analysis.
 * Each function represents one of the categories of logical bugs given in the
 * README.md. The *_00 functions do not contian logical errors and are the base
 * (hopefully) correct implementations of whatever the comments describe.
 *
 * Following are todos:
 *
 *  TODO Conditional
 *      x `<` instead of `<=`
 *          - off by one
 *      x `<` instead of `>` (inversion)
 *      x `~` instead of `!` (assumption on boolean logic)
 *  TODO Assignment related
 *      - incorrect assignment of:
 *          - semantically incorrect values
 *          - Assignment instead of incremental or addition syntactical sugar
 *  TODO Arithmetic errors
 *      - overflows/underflows
 *          - ignoring int wraparound???
 *      - truncation
 *      - relying on floating-point precision
 *      - div by zero
 *      - rounding assumptions
 *      - incorrect metric conversions (funny example i bet)
 *      - cummulative rounding error
 *  - Bitwise operations
 *  TODO Actual logical errors:
 *      - Incorrect implementation of datastructures
 *          - list, heap, tree, btree..
 *  TODO A non-descript logical code with a human description of the ode such
 *  that the llm can infer some usage about it.
 *  TODO Just use a big program brother.
 * */

// We don't take type mismatches into accounts, as static analyzers are more
// than good enough to catch theses problems'

// @mast:control function
// Result: No logical errors detected.

/* This function calculates the sum of the members in the given array.
 * */
int sum_00(int arr[], size_t size) {
  if (arr == NULL) {
    exit(1);
  }

  int sum = 0;

  if (size <= 0) {
    exit(1);
  }

  for (int i = 0; i < size; ++i) {
    sum += arr[i];
  }

  return sum;
}

// @mast:test not initialized
// Can lead to incorrect behaviour.
// Note: Static analyzers warn you

/* This function calculates the sum of the members in the given array.
 * */
int sum_01(int arr[], size_t size) {
  int sum;

  if (size <= 0) {
    return 0;
  }

  for (int i = 0; i < size; ++i) {
    sum += arr[i];
  }

  return sum;
}

// @mast:test indirect size check
// can lead to incorrect behaviour.
// note: static analyzers warn you

/* This function calculates the sum of the members in the given array.
 * */
int sum_02(int arr[], size_t size) {
  int sum = 0;

  size_t helper = size;
  if (helper < 1) {
    return 0;
  }

  for (int i = 0; i < helper; ++i) {
    sum += arr[i];
  }

  return sum;
}

// @mast:test wrong assignment
/* This function calculates the sum of the members in the given array.
 * */
int sum_03(int arr[], size_t size) {
  int sum = 0;

  if (size < 1) {
    return 0;
  }

  for (int i = 0; i < size; ++i) {
    sum = arr[i];
  }

  return sum;
}

// @mast:test add indexes instead

/* This function calculates the sum of the members in the given array.
 * */
int sum_04(int arr[], size_t size) {
  int sum = 0;

  if (size < 1) {
    return 0;
  }

  for (int i = 0; i < size; ++i) {
    sum += i;
  }

  return sum;
}

// @mast:test comment guarantees behaviour
// @res: the LLM will not add extra overflow checks! This is dangerous, meaning
// sometimes the context might be wrong and it should not be provided.

/* This function calculates the sum of the members in the given array.
 * Integers are guaranteed to never overflow.
 * */
int sum_05(int arr[], size_t size) {
  if (arr == NULL) {
    exit(1);
  }

  int sum = 0;

  if (size <= 0) {
    exit(1);
  }

  for (int i = 0; i < size; ++i) {
    sum += arr[i];
  }

  return sum;
}

// @mast:test obfuscated naming
/*
 * I don't know what this does.
 * */
int obz_00(int *adscvu, size_t aosdfiuvadlksjfaew__ds) {
  int glober = 0;

  if (aosdfiuvadlksjfaew__ds < 1) {
    return 0;
  }

  for (int _DSFUhskj = 0; _DSFUhskj < aosdfiuvadlksjfaew__ds; ++_DSFUhskj) {
    glober += adscvu[_DSFUhskj];
  }

  return glober;
}

// @mast:test incorrect units - control

/* This function calculates kilometers per hour.
 * */
int unit_00(int kilometers, int hours) {
  if (hours > 0) {
    return kilometers / hours;
  }

  return 0;
}

// @mast:test incorrect units
// @mast gpt does not care about the name of the variables.
// @mast gpt takes into account comments
// @mast gpt will not determine a logical bug if meters is not called meters

/* This function calculates kilometers per hour.
 * */
int unit_01(int meters, int time) {
  int seconds = time;
  if (seconds > 0) {
    return meters / seconds;
  }

  return 0;
}

// @mast:test unspecified unit in variable name
// @mast gpt does not care about the name of the variables.
// @mast gpt takes into account comments
// @mast gpt will not determine a logical bug if meters is not called meters

/* This function calculates kilometers per hour.
 * */
int unit_02(int distance, int time) {
  if (time > 0) {
    return distance / time;
  }

  return 0;
}

// @mast:test unspecified unit for distance

/* This function calculates kilometers per hour.
 * */
int unit_03(int meters, int time) {
  if (time > 0) {
    return meters / time;
  }

  return 0;
}

/* This function ensures length is not zero in the string.
 * */
int cond_00(char *str) {
  int will_do = 0;
  if (str == NULL) {
    return will_do;
  }

  if (strlen(str) > 0) {
    will_do = 1;
  }

  return will_do;
}

// @mast for the conditional checks of "=" instead of "==":
// @mast they are irrelevant to test since they are very easily analyzed via
// @mast static analysers
// @mast still tested for completness and found correctly by deepseek. In fact
// @mast it tell me tha tcompiler warnings might be supressed, which I found
// funny.

/* This function ensures length is not zero in the string.
 * */
int cond_01(char *str) {
  int will_do = 0;
  if (str = NULL) {
    return will_do;
  }

  if (strlen(str) > 0) {
    will_do = 1;
  }

  return will_do;
}

// @case off by one

/* This function ensures length is not zero in the string.
 * */
int cond_02(char *str) {
  int will_do = 0;
  if (str == NULL) {
    return will_do;
  }

  if (strlen(str) >= 0) {
    will_do = 1;
  }

  return will_do;
}

// @mast:test Check for inverted logic
// @mast deepseek analysis:
// @mast Dead code - The strlen comparison can never be true
// @mast Inverted logic - Function always returns 0 for valid strings regardless
// of content
// @mast Useless check - The strlen comparison serves no practical purpose

/* This function ensures length is not zero in the string.
 * */
int cond_03(char *str) {
  int crash_system = 0;
  if (str == NULL) {
    return crash_system;
  }

  if (strlen(str) < 0) {
    crash_system = 1;
  }

  return crash_system;
}

// @mast:test default boolean case
// @mast Comments matter a lot, at least in deepseek. Comments will change the
// @mast outcome of the logical analysis for a function. bool_00 for example has
// not
// @mast logical errors unless the comment indicates otherwise.

/* Check that something hapenned and return true or false.
 * */
int bool_00(int result) { return !result; }

// @mast:test use bitwise operations instead
// @mast deepseek can point out incorrect usage of bitwise logic in place of
// @mast boolean logic

/* Check that something hapenned and return true or false.
 * */
int bool_01(int result) { return ~result; }

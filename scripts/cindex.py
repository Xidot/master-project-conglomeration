#!/usr/bin/env python3

import subprocess
from pprint import pprint
from collections import defaultdict
import sys, os
import json
import yaml

from clang.cindex import (
    Cursor,
    CursorKind,
    Index,
    CompilationDatabase,
    TranslationUnit,
    SourceLocation,
    SourceRange,
    File,
)

"""
Dumps a callgraph of a function in a codebase
usage: callgraph.py file.cpp|compile_commands.json [-x exclude-list] [extra clang args...]
The easiest way to generate the file compile_commands.json for any make based
compilation chain is to use Bear and recompile with `bear make`.

When running the python script, after parsing all the codebase, you are
prompted to type in the function's name for which you wan to obtain the
callgraph
"""

# Project specific
CALLGRAPH = defaultdict(list)
FULLNAMES = defaultdict(set)
FUNCS = defaultdict(dict) # Warning, C only
FILES = set()
PROJECT_DIR = os.path.realpath("./")

SOURCED_SYMS = set()

LOOKUP = None

MAX_DEPTH=1

PREFIX=os.path.realpath("./")

# We want a global state
index = Index.create()
translation_units = {}

def is_sourced(cursor):
    return fully_qualified_pretty(cursor) in SOURCED_SYMS

# Perhaps remove some of the fluff like the type signature?
def funcs_to_dot(funcs) -> str:
    text = ""
    text += "strict digraph G {\n"

    # track top level funcs
    visited = set()

    for fun in funcs:
        if fun in visited:
            continue

        callees = CALLGRAPH[fun]
        if not callees:
            continue

        # emit node;
        text += f'"{fun}";\n'
        visited.add(fun);

        # don't emit duplicate edges
        __visited = set()

        # emit relationships
        for callee in callees:
            fqd = fully_qualified_pretty(callee)
            if fqd in __visited:
                continue;

            text += f'"{fun}" -> "{fqd}";\n'
            __visited.add(fqd)

    text += "}\n"
    return text

def callgraph_get_callees(cur_fun):
    callees = CALLGRAPH[cur_fun.displayname]
    if not callees:
        return []
    return [fully_qualified_pretty(x) for x in callees]

def callgraph_get_callers(cur_fun):
    caller_arr = []
    for caller in CALLGRAPH:
        for c in CALLGRAPH[caller]:
            if cur_fun == c:
                caller_arr.append(FUNCS[caller]['name'])
    return caller_arr

def get_diag_info(diag):
    return {
        'severity': diag.severity,
        'location': diag.location,
        'spelling': diag.spelling,
        'ranges': list(diag.ranges),
        'fixits': list(diag.fixits)
    }

def get_source_cursor(cur) -> str:
    ext = cur.extent
    s = get_source_from_range(ext)
    return s

def get_source_from_range(source_range) -> str:
    loc = source_range.start
    len = source_range.end.offset - source_range.start.offset

    assert len > 0 and len < 100000000000

    with open(loc.file.name, "r") as file:
        file.seek(source_range.start.offset)
        return file.read(len)

def in_project(c) -> bool:
    abspath = os.path.realpath(c.location.file.name)
    if c is None:
        return False
    elif abspath in FILES or PROJECT_DIR in abspath:
        return True
    return False

def fully_qualified(c):
    if c is None:
        return ''
    elif c.kind == CursorKind.TRANSLATION_UNIT:
        return ''
    else:
        res = fully_qualified(c.semantic_parent)
        if res != '':
            return res + '::' + c.spelling
        return c.spelling


def fully_qualified_pretty(c):
    if c is None:
        return ''
    elif c.kind == CursorKind.TRANSLATION_UNIT:
        return ''
    else:
        res = fully_qualified(c.semantic_parent)
        if res != '':
            return res + '::' + c.displayname
        return c.displayname


def is_excluded(node, xfiles, xprefs):
    if not node.extent.start.file:
        return False

    for xf in xfiles:
        if node.extent.start.file.name.startswith(xf):
            return True

    fqp = fully_qualified_pretty(node)

    for xp in xprefs:
        if fqp.startswith(xp):
            return True

    return False


# Note: Our focus is on C but CPP support came with the tool already
def show_info(node, xfiles, xprefs, cur_fun=None):
    if node.kind == CursorKind.FUNCTION_TEMPLATE:
        if not is_excluded(node, xfiles, xprefs):
            cur_fun = node
            FULLNAMES[fully_qualified(cur_fun)].add(
                fully_qualified_pretty(cur_fun))

    # Collect functions
    if node.kind == CursorKind.CXX_METHOD or \
            node.kind == CursorKind.FUNCTION_DECL:
        if not is_excluded(node, xfiles, xprefs):
            cur_fun = node
            fqdn = fully_qualified(cur_fun)
            fqdnp = fully_qualified_pretty(cur_fun)
            FULLNAMES[fqdn].add(
                fully_qualified_pretty(cur_fun))

            # Store both, different files
            FUNCS[fqdnp]['name'] = fully_qualified_pretty(cur_fun)
            if cur_fun.is_definition():
                FUNCS[fqdnp]['defi'] = cur_fun
            else:
                FUNCS[fqdnp]['decl'] = cur_fun

    if node.kind == CursorKind.CALL_EXPR:
        if node.referenced and not is_excluded(node.referenced, xfiles, xprefs):
            CALLGRAPH[fully_qualified_pretty(cur_fun)].append(node.referenced)

    for c in node.get_children():
        show_info(c, xfiles, xprefs, cur_fun)

def pretty_print(n):
    v = ''
    if n.is_virtual_method():
        v = ' virtual'
    if n.is_pure_virtual_method():
        v = ' = 0'
    return fully_qualified_pretty(n) + v

def print_calls(fun_name, so_far, depth=0, max_depth=MAX_DEPTH):
    if depth >= max_depth:
        return
    if depth >= 15:
        print('...<too deep>...')
        return


    if fun_name in CALLGRAPH:
        for f in CALLGRAPH[fun_name]:
            print('  ' * (depth + 1) + pretty_print(f))
            if f in so_far:
                continue
            so_far.append(f)
            if fully_qualified_pretty(f) in CALLGRAPH:
                print_calls(fully_qualified_pretty(f), so_far, depth + 1, max_depth=max_depth)
            else:
                print_calls(fully_qualified(f), so_far, depth + 1, max_depth=max_depth)

# Do the same thing as the cull
# The strategy is to get all the callers of a function and the callees and
# include them in a single callgraph to showcase the usage.
def print_callees_and_callers(fun_name):
    # Is it broken?
    if fun_name in FUNCS:
        f = FUNCS[fun_name]
        if f['defi']:
            ext = f['defi'].extent
            print(ext.start.file.name)
            print(get_source_from_range(ext))
    # TODO make optional callgraph

def read_compile_commands(filename):
    if filename.endswith('.json'):
        with open(filename) as compdb:
            return json.load(compdb)
    else:
        return [{'command': '', 'file': filename}]

def read_args(args):
    db = None
    clang_args = []
    excluded_prefixes = []
    excluded_paths = []
    config_filename = None
    lookup = None
    cg_only = False
    max_depth = None
    prefix = None
    prepare_only = False
    multi_lookup_filename = None

    reverse_lookup = None
    reverse_file = None

    i = 0
    while i < len(args):
        if args[i] == '-x':
            i += 1
            excluded_prefixes += args[i].split(',')
        elif args[i] == '-rl':
            i += 1
            reverse_lookup = args[i]
        elif args[i] == '-rlf':
            i += 1
            reverse_file = args[i]
        elif args[i] == '--prepare':
            prepare_only = True
        elif args[i] == '--prefix':
            i += 1
            prefix = os.path.realpath(args[i])
        elif args[i] == '-p':
            i += 1
            excluded_paths += args[i].split(',')
        elif args[i] == '--cg':
            cg_only = True
        elif args[i] == '--depth':
            i += 1
            max_depth = int(args[i], 10)
        elif args[i] == '--cfg':
            i += 1
            config_filename = args[i]
        elif args[i] == '--lookup':
            i += 1
            lookup = args[i]
        elif args[i] == '--multi-lookup':
            i += 1
            multi_lookup_filename = args[i]
        elif args[i][0] == '-':
            clang_args.append(args[i])
        else:
            db = args[i]
        i += 1

    # if len(excluded_paths) == 0:
    #     excluded_paths.append('/usr')

    if prefix is not None:
        global PREFIX
        PREFIX = prefix

    if max_depth is not None:
        global MAX_DEPTH
        MAX_DEPTH = max_depth

    return {
        'db': db,
        'clang_args': clang_args,
        'excluded_prefixes': excluded_prefixes,
        'excluded_paths': excluded_paths,
        'config_filename': config_filename,
        'lookup': lookup,
        'multi_lookup_filename': multi_lookup_filename,
        'cg_only': cg_only,
        'prepare_only': prepare_only,
        'ask': (lookup is None),
        'reverse_lookup': reverse_lookup,
        'reverse_file': reverse_file,
    }


def load_config_file(cfg):
    if cfg['config_filename']:
        with open(cfg['config_filename'], 'r') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            keys = ('clang_args', 'excluded_prefixes', 'excluded_paths')
            for k in keys:
                cfg[k] += data.get(k, [])


def keep_arg(x) -> bool:
    keep_this = x.startswith('-I') or x.startswith('-std=') or x.startswith('-D')
    return keep_this

def analyze_source_files(cfg):
    print('reading source files...')
    for cmd in read_compile_commands(cfg['db']):
        # https://clang.llvm.org/docs/JSONCompilationDatabase.html#format
        # either "arguments" or "command" is required.
        if 'arguments' in cmd:
            arguments = cmd['arguments']
        else:
            arguments = cmd['command'].split()
        c = [x for x in arguments if keep_arg(x)] + cfg['clang_args']
        tu = index.parse(
            cmd['file'],
            c,
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD | TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION
        )

        FILES.add(cmd['file'])
        translation_units[cmd['file']] = tu

        print(cmd['file'])
        if not tu:
            print("unable to load input")

        for d in tu.diagnostics:
            if d.severity == d.Error or d.severity == d.Fatal:
                print(' '.join(c))
                pprint(('diags', list(map(get_diag_info, tu.diagnostics))))
                return

        show_info(tu.cursor, cfg['excluded_paths'], cfg['excluded_prefixes'])

"""
Compute a new buffer of text which includes every definition used in the
function defined by this cursor.

Source code should be organized by file because we want to use this as a
prompt. Each function definition will be orrganized by file and line number.
Type definitions should go to the top always because the LLM will use them
later in its prediction.

Callgraph goes after the source code as a supplementary piece of data. The
function we want to analyze plus the other functions go inbetween.
"""
def custom_lookup(fun):
    if fun not in FUNCS:
        return

    print(f"[+] Analyzing {fun}")

    fun = FUNCS[fun]

    if "defi" not in fun and "decl" not in fun:
        print(f"No definition of {fun}")
        return

    cur_fun_def = None
    if 'defi' in fun:
        cur_fun_def = fun['defi']
    elif 'decl' in fun:
        cur_fun_def = fun['decl']
    else:
        assert(False)

    # the set of callers and calees of our lookup at depth 1
    callees = callgraph_get_callees(cur_fun_def)
    callers = callgraph_get_callers(cur_fun_def)
    files = {} # files refernced in the lookup fun

    visited_symbols = set()

    all_funcs = [fully_qualified_pretty(cur_fun_def)] + callees + callers
    for f in all_funcs:
        fname = FUNCS[f]
        if not fname:
            continue

        cursor = None
        assert (FUNCS[f] is not None)

        if 'defi' in FUNCS[f]:
            cursor = FUNCS[f]['defi']
        elif 'decl' in FUNCS[f]:
            cursor = FUNCS[f]['decl']
        else:
            assert(False)

        assert(cursor is not None)

        if is_sourced(cursor):
            continue

        # Function information
        loc = cursor.location
        filename = loc.file.name

        # Gather type information and struct definitions 
        # Walk function and get relevant information
        for node in cursor.walk_preorder():
            if is_sourced(node):
                continue

            # Gather type information on custom structs
            # TYPE_REF usually referes to typedefs
            if node.kind == CursorKind.TYPE_REF:
                d = node.get_definition()
                assert(d)
                if is_sourced(d):
                    continue

                SOURCED_SYMS.add(fully_qualified_pretty(node))
                SOURCED_SYMS.add(fully_qualified_pretty(d))

                d_loc = d.location
                d_filename = d_loc.file.name
                if d_filename not in files:
                    files[d_filename] = f"---- File: {d_filename}\n\n"
                if d.raw_comment:
                    files[d_filename] += f"{d.raw_comment}\n"
                files[d_filename] += f"/// Line number here: {d_loc.line - 1}\n"
                files[d_filename] += f"{get_source_cursor(d)}\n\n"

            # Try extract structs, enums and their types
            # Including enums will very much reduce the hallucination rates
            if node.kind == CursorKind.DECL_REF_EXPR:
                cur_node_def = node.get_definition()
                if cur_node_def and cur_node_def.kind == CursorKind.ENUM_CONSTANT_DECL:
                    # print(f"{cur_node_def.displayname} {cur_node_def.kind}")
                    # print(get_source_from_range(d.semantic_parent.extent))
                    d = cur_node_def.semantic_parent
                    assert(d)
                    if is_sourced(d):
                        continue

                    SOURCED_SYMS.add(fully_qualified_pretty(node))
                    SOURCED_SYMS.add(fully_qualified_pretty(d))

                    d_loc = d.location
                    d_filename = d_loc.file.name
                    if d_filename not in files:
                        files[d_filename] = f"---- File: {d_filename}\n\n"
                    if d.raw_comment:
                        files[d_filename] += f"{d.raw_comment}\n"
                    files[d_filename] += f"/// Line number here: {d_loc.line - 1}\n"
                    files[d_filename] += f"{get_source_cursor(d)}\n\n"

        if is_sourced(cursor):
            continue

        # Append all the source code from the callgraph functions
        if filename not in files:
            files[filename] = f"---- File: {filename}\n\n"
        if cursor.raw_comment:
            files[filename] += f"{cursor.raw_comment}\n"
        files[filename] += f"/// Line number here: {loc.line - 1}\n"
        files[filename] += f"{get_source_cursor(cursor)}\n\n"
        SOURCED_SYMS.add(fully_qualified_pretty(cursor))

    # print('[+] Doing type analysis for inclusion')

    graph = funcs_to_dot(all_funcs)

    prompt_path = f"prompt-{LOOKUP}"
    prompt_path = os.path.join(PREFIX, prompt_path)
    with open(prompt_path, "w") as file:
        file.write(f'Target function: "{LOOKUP}"\n\n\n');
        for f in files:
            file.write(files[f])
        file.write('\n\n')
        file.write('----- Callgraph:\n')
        file.write(graph)

    print(f'[+] Created {prompt_path}')

def ask_and_print_callgraph():
    while True:
        fun = input('> ')
        if not fun:
            break
        print_callgraph(fun)

def find_matches(fun):
    print('matching:')
    for f, ff in FULLNAMES.items():
        if f.startswith(fun):
            for fff in ff:
                print(fff)

def print_callgraph(fun):
    if fun in CALLGRAPH:
        print(fun)
        print_calls(fun, list(), max_depth=MAX_DEPTH)
    else:
        print('matching:')
        for f, ff in FULLNAMES.items():
            if f.startswith(fun):
                for fff in ff:
                    print(fff)

def get_all_used_funcs(entry, visited = set()):
    """
    Get all unique in project function symbols used by the entry function's callgraph.
    """

    acc = set()
    visited.add(entry)

    for cur_fun in CALLGRAPH[entry]:
        if in_project(cur_fun):
            sym = fully_qualified_pretty(cur_fun)
            if sym in visited:
                continue
            funcs = get_all_used_funcs(sym, visited)
            acc.add(sym)
            # append results of child
            for m in funcs:
                acc.add(m)

    return acc

# Threr was some more processing required...
def split_identifier(identifier: str):
    [file, line] = identifier.split(":")
    return (file, int(line))

def tu_from_file(filepath):
    for file in translation_units.keys():
        if filepath == file:
            return translation_units[file]
    return None

def reverse_lookup(fileline: str):
    """Return source for line + surrounding if statement if possible"""

    file, line = split_identifier(fileline);

    for source_file in FILES:
        if file == os.path.basename(source_file):
            tu = tu_from_file(source_file)
            if tu is None:
                print(f"Error no tu for: {file}")
                exit(1)
            # print(f"Found a file at {source_file}")
            f = File.from_name(tu, file)
            if f is None:
                print(f"Could not find file {f}")
                exit(1)
            
            sloc = SourceLocation.from_position(tu, f, line, 1)
            # We jsut want a range of funlogline - 1 -> +1
            prevloc = SourceLocation.from_position(tu, f, sloc.line - 1, 1)
            nextloc = SourceLocation.from_position(tu, f, sloc.line + 2, 1)
            extent = SourceRange.from_locations(prevloc, nextloc)
            source = get_source_from_range(extent)
            print(source)

def reverse_file(filepath: str):
    with open(filepath, "r") as file:
        for line in file.readlines():
            print(line)
            reverse_lookup(line)

def main():
    if len(sys.argv) < 2:
        print('usage: ' + sys.argv[0] + ' file.cpp|compile_database.json '
              '[extra clang args...]')
        return

    cfg = read_args(sys.argv)
    load_config_file(cfg)

    analyze_source_files(cfg)

    if cfg['reverse_lookup']:
        print(f"[+] Looking for {cfg['reverse_lookup']}")
        reverse_lookup(cfg['reverse_lookup'])
    elif cfg['reverse_file']:
        print(f"[+] Using reverse file: {cfg['reverse_file']}")
        reverse_file(cfg['reverse_file'])
    elif cfg['lookup']:
        global LOOKUP
        LOOKUP = cfg['lookup']

        if cfg['cg_only']:
            print_callgraph(cfg['lookup'])
        elif cfg['prepare_only']:
            functions = get_all_used_funcs(cfg['lookup'])
            with open(os.path.join(PREFIX, "prepare"), "w") as file:
                for fun in functions:
                    file.write(f"{fun}\n")
        elif cfg['multi_lookup_filename']:
            listfilename = cfg['multi_lookup_filename']
            print("Using list from file")
            with open(listfilename, "r") as file:
                global SOURCED_SYMS

                lines = [x.strip() for x in file.readlines()]
                for line in lines:
                    if line in FUNCS:
                        LOOKUP = line
                        custom_lookup(line)
                        SOURCED_SYMS = set()
        elif cfg['lookup'] in FUNCS:
            custom_lookup(cfg['lookup'])
        else:
            find_matches(cfg['lookup'])

if __name__ == '__main__':
    main()

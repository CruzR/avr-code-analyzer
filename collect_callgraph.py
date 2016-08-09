#!/usr/bin/env python

"""
Collect static call graph.

Code needs to be compiled with ``-fdump-rtl-expand`` for this to work.
Only static function invocations are considered. Dynamic invocations
will need to be supplied in some other way.
"""


import glob
import os.path
import pickle
import re


PICKLE_FILE = 'avr_code_analyzer.pickle'

if os.path.exists(PICKLE_FILE):
    with open(PICKLE_FILE, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
else:
    data = {}

callgraph = {}
current_function = None

function_pattern = r';;\s+Function\s+(?P<fname>\w+)'
function_regex = re.compile(function_pattern)
call_pattern = r'\(call.*\("(?P<fname>\w+)"'
call_regex = re.compile(call_pattern)

def parse_rtl(line):
    match = function_regex.search(line)
    if match:
        global current_function
        current_function = match.group('fname')
        callgraph[current_function] = callgraph.get(current_function, [])

    match = call_regex.search(line)
    if match:
        callee = match.group('fname')
        callgraph[current_function].append({'callee': callee, 'type': 'static'})


for filename in glob.iglob('**/*.expand', recursive=True):
    with open(filename) as rtl_file:
        for line in rtl_file:
            parse_rtl(line)


data['callgraph'] = callgraph

with open(PICKLE_FILE, 'wb') as pickle_file:
    pickle.dump(data, pickle_file)

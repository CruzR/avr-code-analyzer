#!/usr/bin/env python

"""
Collect stack usage per function.

To use this script, make sure to compile your project with
the ``-fstack-usage`` flag, otherwise GCC won't emit the
required files. Also, to get a complete picture, you will
have to compile everything, even libraries you would normally
link in (e.g. the standard library).
"""

import glob
import pickle
import re


stack_usage = []

su_pattern = r'.*:(?P<fname>.*)\t(?P<size>.*)\t(?P<type>.*)'
su_regex = re.compile(su_pattern)

def parse_and_add(line):
    match = su_regex.match(line)
    if not match:
        print("Warning: Could not parse line", repr(line))
    else:
        stack_usage.append({'fname': match.group('fname'),
                            'size': match.group('size'),
                            'type': match.group('type')})

    
# GCC emits one stack usage file per compilation unit.
# TODO: What if several compilation units contain static
# functions with the same name?
for filename in glob.iglob('**/*.su', recursive=True):
    with open(filename) as stack_usage_file:
        for line in stack_usage_file:
            parse_and_add(line)

# Just dump the data to a pickle for now.
with open('avr_code_analyzer.pickle', 'wb') as pickle_file:
    pickle.dump({'stack_usage': stack_usage}, pickle_file)

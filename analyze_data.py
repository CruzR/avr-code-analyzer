#!/usr/bin/env python

"""
Analyze previously collected data.
"""


import os.path
import pickle
import sys


PICKLE_FILE = 'avr_code_analyzer.pickle'

if not os.path.exists(PICKLE_FILE):
    print("Error: You need to run the collection scripts first.",
          file=sys.stderr)
    sys.exit(1)

with open(PICKLE_FILE, 'rb') as pickle_file:
    data = pickle.load(pickle_file)

callgraph = data['callgraph']
stack_usage = data['stack_usage']


class CycleDetected(ValueError):
    def __init__(self, stack):
        ValueError.__init__(self)
        self.stack = stack


def detect_cycles(start_node):
    current_stack = []
    visited = set()
    completed = set()

    def dfs(fn):
        current_stack.append(fn)
        if fn in completed:
            return
        if fn in visited and fn not in completed:
            # Cycle detected!
            cycle_start = current_stack.find(fn)
            cycle = current_stack[cycle_start:]
            raise CycleDetected(cycle)
        visited.add(fn)

        for edge in callgraph.get(fn, []):
            dfs(edge['callee'])

        completed.add(fn)

    dfs(start_node)


try:
    detect_cycles('main')
    data['cycle_free'] = True
except CycleDetected as e:
    print("Error: cycle detected:", " -> ".join(e.stack), file=sys.stderr)
    sys.exit(1)


def find_reachable_nodes(start_node):
    visited = set()

    def dfs(fn):
        if fn in visited:
            return
        visited.add(fn)

        for edge in callgraph.get(fn, []):
            dfs(edge['callee'])

    dfs(start_node)
    return visited


reachable_nodes = find_reachable_nodes('main')
reduced_callgraph = {k: callgraph.get(k, []) for k in reachable_nodes}
data['reduced_callgraph'] = reduced_callgraph


def accumulate_stack_usage(start_node):
    accumulated_stack = {}

    def dfs(fn):
        if fn in accumulated_stack:
            return

        for edge in callgraph.get(fn, []):
            dfs(edge['callee'])

        # TODO: massage input data so that such hacks are not necessary any more
        cost = ([int(x['size']) for x in stack_usage if x['fname'] == fn] + [0])[0]
        cost_others = [accumulated_stack[x['callee']] for x in callgraph.get(fn, [])]
        accumulated_stack[fn] = cost + sum(cost_others)

    dfs(start_node)
    return accumulated_stack


accumulated_stack = accumulate_stack_usage('main')
data['accumulated_stack'] = accumulated_stack


with open(PICKLE_FILE, 'wb') as pickle_file:
    pickle.dump(data, pickle_file)

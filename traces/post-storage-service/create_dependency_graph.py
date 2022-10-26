#!/usr/bin/env python

import os
import json
from prettytable import PrettyTable

filename = "2d93fdbc8ec71efe.json"

def file_to_json(filename):
    with open(filename, "rb") as f:
        json_data = json.load(f)
        return json_data

spanid_map = {}
ops = []
root = ""
total_duration = 0

def spanid_to_opname(json_data):
    for span in json_data["spans"]:
        spanID = span["spanID"]
        opName = span["operationName"]
        spanid_map[spanID] = opName

def print_operations(operations):
    t = PrettyTable(['OperationName', 'Parent', 'Idx', 'StartTime', 'EndTime', 'Duration',  'in_cp', 'cp', 'cp_dur', 'SelfDuration', 'Percentage'])
    t.sortby = 'StartTime'
    for op, data in operations.items():
        t.add_row([op, data['parent'], data["idx"], data["start"], data["end"], data["duration"], data["in_cp"], data['cp'], data["cp_dur"], data["self_duration"], round(data["percent_dur"], 2)])
    print(t)

def print_contents(dictionary):
    print("Print contents:")
    for key, value in dictionary.items():
        print(key, " ", value)

def retrieve_operations(json_data):
    operations = {}
    idx = 0
    for span in json_data["spans"]:
        name = span["operationName"]
        if name == "/wrk2-api/post/compose":
            continue
        operations[name] = {}
        op = operations[name]
        op["idx"] = idx
        idx = idx + 1
        op["start"] = span["startTime"]
        op["end"] = span["startTime"] + span["duration"]
        op["duration"] = span["duration"]
        op["children"] = []
        op["in_cp"] = 0
        if len(span["references"]) > 0:
            parentID = span["references"][0]["spanID"]
            op["parent"] = spanid_map[parentID]
        else:
            op["parent"] = None
        #print(name, " ", op["parent"])
        if op["parent"] == "/wrk2-api/post/compose":
            root = name
            #print("set rooot ", root)
        ops.append(name)
        print(name, "  ", op["idx"], "  ", op["start"],  "   ", op["end"],  "    ", op["parent"], "\n")

    return operations, root

def get_starttime(op):
    return operations[op]["start"]
def get_endtime(op):
    return operations[op]["end"]
def get_duration(op):
    return operations[op]["duration"]


def create_dependency_graph(json_data, operations, root):
    num_ops = len(operations) + 1
    print("num_ops: ", num_ops, "  roooot:   ", root, "\n")
    graph = [[0 for i in range(num_ops)] for j in range(num_ops)]
    global total_duration
    # Captures dependencies based on the references
    for op, data in operations.items():
        if data["parent"] is not None:
            parent = data["parent"]
            if parent == '/wrk2-api/post/compose':
                continue
            parent_idx = operations[parent]["idx"]
            child_idx = data["idx"]
            print("Parentidx: ", parent_idx, " child_idx ", child_idx)
            print(op)
            operations[parent]["children"].append(op) 
            #graph[parent_idx][child_idx] = 1
    #print_operations(operations)
    print("\n\n", root, "\r\n")
    # Lets capture asynchrony / synchrony

    for op, data in operations.items():
        data["cp"] = []
        data["cp_dur"] = 0
        print(op)
        if data["children"]:
            if len(data["children"]) == 1:
                data["cp"].append(data["children"][0])
                data["cp_dur"] = operations[data["children"][0]]["duration"]
            else:
                children = data["children"]
                children.sort(key=get_starttime)
                num_children = len(children)
                cc = []
                pov = []
                start = get_starttime(children[0])
                end = get_endtime(children[0])
                dur = get_duration(children[0])
                start_idx = 0
                cp_op = children[0]
                #print(start, "  ", end, " ", dur, " ", cp_op)
                i = 1
                for i in range(1, num_children):
                    #print(data["cp"])
                    #print(data["cp_dur"], " duration")
                    op_name = children[i]
                    st = get_starttime(op_name)
                    en = get_endtime(op_name)
                    #print(start, "  ", end, " ", st, " ", en, " ", cp_op, " ", op_name)
                    if (end < st) :# No Overlap
                        #print("No overlap")
                        #print(i, " ", start_idx,  " ",  cp_op)
                        data["cp_dur"] += (end-start)
                        data["cp"].append(cp_op)

                        cp_op = op_name
                        if (i == num_children -1):
                            data["cp"].append(children[i])
                            data["cp_dur"] = data["cp_dur"] + en - st
                        start = st
                        end = en
                        start_idx = i

                    elif (en < end): # complete overlap
                        #print("Complete overlap")
                        continue
                    else:
                        #print("Partial overlap")
                        end = en
                        if (en-st > dur):
                            cp_op = op_name
                if (start_idx != num_children - 1):
                    data["cp_dur"] += (end-start)
                    data["cp"].append(cp_op)
            data["self_duration"] = data["duration"] - data["cp_dur"] 
        else:
            data["self_duration"] = data["duration"]


    total_duration += operations[root]["self_duration"]
    operations[root]["in_cp"] = 1
    dfs(operations, root)
    print("\ntotal_duration: ", total_duration)
    for op, data in operations.items():
        data["percent_dur"] = data["self_duration"] * 100 / total_duration if data["in_cp"] else 0

    return graph

def dfs(operations, root):
    global total_duration
    for op in operations[root]["cp"]:
        operations[op]["in_cp"] = 1
        print(op,  " ", operations[op]["self_duration"], " ", total_duration)
        total_duration += operations[op]["self_duration"]
        dfs(operations, op)


def print_dependency_graph(graph):
    print("Dependency graph: \n")
    i = 0
    j = 0

    for i in range(len(spanid_map)):
        print(i, ":   ", end='')
        for j in range(len(spanid_map)):
            print(graph[i][j],"  ", end = '')
        print("     ", ops[i], "\n")




def print_ops_duration(operations):
    print("\n\n")
    t = PrettyTable(['OperationName', 'SelfDuration', 'TotalDuration', 'Percentage'])
    t.sortby = 'Percentage'
    t.reversesort=True
    for op, data in operations.items():
        t.add_row([op, data["self_duration"], data["duration"], round(data["percent_dur"], 2)])
        #print(op, "   self:  ", data["self_duration"] , "    Total: ", data["duration"], "    percentage: " , data["percent_dur"])
    print(t)


json_data = file_to_json(filename)
spanid_to_opname(json_data)
print_contents(spanid_map)
operations, root = retrieve_operations(json_data)
graph = create_dependency_graph(json_data, operations, root)
print_operations(operations)
#print_dependency_graph(graph)
print_ops_duration(operations)


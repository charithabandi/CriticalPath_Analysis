#!/usr/bin/env python

import os
import json
import glob
from prettytable import PrettyTable
import statistics

filename = "2d93fdbc8ec71efe.json"
compose_posts = "/wrk2-api/post/compose"
home_timeline_read = "/wrk2-api/home-timeline/read"
user_timeline_read = "/wrk2-api/user-timeline/read"
follow_user = "/wrk2-api/user/follow"
register_user = "/wrk2-api/user/register"

############################################### UTILS ########################
def file_to_json(filename):
    with open(filename, "rb") as f:
        json_data = json.load(f)
        return json_data

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
"""
def print_dependency_graph(graph):
    print("Dependency graph: \n")
    for i in range(len(spanid_map)):
        print(i, ":   ", end='')
        for j in range(len(spanid_map)):
            print(graph[i][j],"  ", end = '')
        print("     ", ops[i], "\n")
"""

def print_critical_path_analytics(operations):
    print("\n\n")
    t = PrettyTable(['OperationName', 'SelfDuration', 'TotalDuration', 'Percentage'])
    t.sortby = 'Percentage'
    t.reversesort=True
    for op, data in operations.items():
        t.add_row([op, data["self_duration"], data["duration"], round(data["percent_dur"], 2)])
        #print(op, "   self:  ", data["self_duration"] , "    Total: ", data["duration"], "    percentage: " , data["percent_dur"])
    print(t)

def get_starttime(op):
    return operations[op]["start"]
def get_endtime(op):
    return operations[op]["end"]
def get_duration(op):
    return operations[op]["duration"]


def spanid_to_opname(json_data):
    global spanid_map, skip
    spanid_map = {}
    for span in json_data["spans"]:
        spanID = span["spanID"]
        opName = span["operationName"]
        print(opName)
        if (span["warnings"] is not None):
            skip = 1
            return 
        spanid_map[spanID] = opName


def dfs(operations, root):
    global total_duration, cp
    if cp == "":
        cp = root
    else:
        cp = cp + " -> " + root

    for op in operations[root]["cp"]:
        operations[op]["in_cp"] = 1
        operations[op]["not_in_cp"] = 0
        print(op,  " ", operations[op]["self_duration"], " ", total_duration)
        total_duration += operations[op]["self_duration"]
        dfs(operations, op)

def print_op_cnts():
    t = PrettyTable(['OperationName', 'In CP Count', 'Not In CP Count', '#Traces'])
    for op_name, cnt in op_cnt.items():
        t.add_row([op_name, cnt[0], cnt[1], cnt[0] + cnt[1]])
    print(t, "\n\n")

def finalstats():
    for key, data in omni_results.items():
        final_stats[key] = {}
        final_stats[key]["mean_total_duration"] = round(statistics.mean(d["total_duration"] for d in data), 2)
        final_stats[key]["min_total_duration"] = min(d["total_duration"] for d in data)
        final_stats[key]["max_total_duration"] = max(d["total_duration"] for d in data)

        final_stats[key]["mean_self_duration"] = round(statistics.mean(d["self_duration"] for d in data), 2)
        final_stats[key]["min_self_duration"] = min(d["self_duration"] for d in data)
        final_stats[key]["max_self_duration"] = max(d["self_duration"] for d in data)

        final_stats[key]["mean_cp_duration"] = round(statistics.mean(d["cp_duration"] for d in data),2)
        final_stats[key]["min_cp_duration"] = min(d["cp_duration"] for d in data)
        final_stats[key]["max_cp_duration"] = max(d["cp_duration"] for d in data)

        final_stats[key]["mean_percent_duration"] = round(statistics.mean(d["percent_duration"] for d in data), 2)
        final_stats[key]["mean_percent_duration"] = min(d["percent_duration"] for d in data)
        final_stats[key]["mean_percent_duration"] = max(d["percent_duration"] for d in data)

        final_stats[key]["in_cp_count"] = op_cnt[key][0]
        final_stats[key]["not_in_cp_count"] = op_cnt[key][1]
        final_stats[key]["total_apprearences"] = op_cnt[key][0] + op_cnt[key][1]


def dump_omni_results():
    finalstats()
    filepath = "/users/chbandi/omni_results.json"
    with open(filepath, 'w') as file:
        json_string = json.dumps(omni_results, default=lambda o: o.__dict__, indent=4)
        file.write(json_string)

    filepath = "/users/chbandi/finalstats.json"
    with open(filepath, 'w') as file:
        json_string = json.dumps(final_stats, default=lambda o: o.__dict__, indent=4)
        file.write(json_string)

    filepath = "/users/chbandi/totalDuration.json"
    with open(filepath, 'w') as file:
        json_string = json.dumps(total_dur_list, default=lambda o: o.__dict__, indent=4)
        file.write(json_string)

    filepath = "/users/chbandi/criticalPath.json"
    with open(filepath, 'w') as file:
        json_string = json.dumps(criticalPath, default=lambda o: o.__dict__, indent=4)
        file.write(json_string)

def is_ngx_server(name):
    if name in [compose_posts, home_timeline_read, user_timeline_read, register_user, follow_user]:
        return True
    return False

################################################## 

spanid_map = {}
#ops = []
operations = {}
omni_results = {}
op_cnt = {}
skip = 0
final_stats = {}
total_dur_list = {}
criticalPath = {}
cp = ""
traceID = ""

def analyze_trace(filename):
    global skip, operations
    #Extract JSON data from the traces
    skip = 0
    json_data = file_to_json(filename)
    print("Analyzing trace id: ", json_data["traceID"])
    #construct spanid to operation name map
    spanid_to_opname(json_data)
    if skip:
        return 
    print_contents(spanid_map)

    #Extract operation info
    operations, root = retrieve_operations(json_data)

    #Critical path analysis
    if root == "":
        return 
    critical_path_analysis(json_data, operations, root)
    update_global_stats(json_data, operations)
    print_operations(operations)
    print_critical_path_analytics(operations)

def analyze_traces():
    read_files = glob.glob("*.json")
    for f in read_files:
        global spanid_map, root, total_duration, traceID
        spanid_map = {}
        root = ""
        traceID = ""
        total_duration = 0
        analyze_trace(f)
    print_op_cnts()
    dump_omni_results()

def retrieve_operations(json_data):
    global operations, spanid_map, root, traceID
    operations = {}
    idx = 0
    root = ""
    traceID = json_data["traceID"]
    for span in json_data["spans"]:
        name = span["operationName"]
        if is_ngx_server(name):
            continue
        print(name)
        operations[name] = {}
        op = operations[name]
        op["idx"] = idx
        idx = idx + 1
        op["start"] = span["startTime"]
        op["end"] = span["startTime"] + span["duration"]
        op["duration"] = span["duration"]
        op["children"] = []
        op["in_cp"] = 0
        op["not_in_cp"] = 1
        if len(span["references"]) > 0:
            parentID = span["references"][0]["spanID"]
            op["parent"] = spanid_map[parentID]
        else:
            op["parent"] = None
        #print(name, " ", op["parent"])
        if is_ngx_server(op["parent"]):
            root = name
            #print("set rooot ", root)
        #ops.append(name)
        print(name, "  ", op["idx"], "  ", op["start"],  "   ", op["end"],  "    ", op["parent"], "\n")

    return operations, root


def critical_path_analysis(json_data, operations, root):
    num_ops = len(operations) + 1
    print("num_ops: ", num_ops, "  roooot:   ", root, "\n")
    #graph = [[0 for i in range(num_ops)] for j in range(num_ops)]
    global total_duration, cp, traceID
    # Captures dependencies based on the references
    for op, data in operations.items():
        if data["parent"] is not None:
            parent = data["parent"]
            if is_ngx_server(parent):
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
        #total_duration += data["self_duration"]


    total_duration += operations[root]["self_duration"]
    operations[root]["in_cp"] = 1
    operations[root]["not_in_cp"] = 0
    cp = ""
    dfs(operations, root)
    print("\n CriticalPath:  ",cp, "\n") 
    print("\ntotal_duration: ", total_duration)
    if root not in total_dur_list:
        total_dur_list[root] = []
    total_dur_list[root].append(total_duration)
    if cp in criticalPath:
        criticalPath[cp][0] = criticalPath[cp][0] + 1
    else:
        criticalPath[cp] = [1, traceID]


    for op, data in operations.items():
        data["percent_dur"] = data["self_duration"] * 100 / total_duration if data["in_cp"] else 0

def update_global_stats(json_data, operations):
    for op_name, data in operations.items():
        if op_name not in  omni_results:
            omni_results[op_name] = []
            op_cnt[op_name] = [0,0]
        stats = {"total_duration": data["duration"], "self_duration": data["self_duration"], "cp_duration": data["cp_dur"], "percent_duration": round(data["percent_dur"], 2)}
        omni_results[op_name].append(stats)
        if data["in_cp"]:
            op_cnt[op_name][0] = op_cnt[op_name][0] + 1
        if data["not_in_cp"]:
            op_cnt[op_name][1] = op_cnt[op_name][1] + 1

#analyze_trace("04b70754a177e5c0.json")
analyze_traces()

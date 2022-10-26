#!/usr/bin/env python

import os
import json
import glob

read_files = glob.glob("*.json")
omni_dict = {}

for f in read_files:
    with open(f, "rb") as trace:
        json_data = json.load(trace)
        for span in json_data["spans"]:
            if span["operationName"] not in omni_dict:
                omni_dict[span["operationName"]] = []
            omni_dict[span["operationName"]].append(span["duration"])


print(len(omni_dict.keys()))

for keys, value in omni_dict.items():
    print(keys)

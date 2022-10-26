#!/usr/bin/env python

import os
import json
import glob
import statistics

read_files = glob.glob("*.json")
omni_dict = {}
cnt_dict = {}

for f in read_files:
    with open(f, "rb") as trace:
        json_data = json.load(trace)

        for span in json_data["spans"]:
            if span["operationName"] not in omni_dict:
                omni_dict[span["operationName"]] = []
            omni_dict[span["operationName"]].append(span["duration"])
            
            if span["operationName"] == "compose_text_client":
                compose_text_client = span["duration"]
            elif span["operationName"] == "compose_media_client":
                compose_media_client =  span["duration"]
            elif span["operationName"] == "compose_unique_id_client":
                compose_unique_id_client = span["duration"]
            elif span["operationName"] == "compose_creator_client":
                compose_creator_client = span["duration"]
            
            elif span["operationName"] == "compose_urls_client":
                compose_urls_client = span["duration"]
            elif span["operationName"] == "compose_user_mentions_client":
                compose_user_mentions_client = span["duration"]

        if compose_urls_client > compose_user_mentions_client:
            cnt_dict["compose_urls_client"] = cnt_dict.setdefault("compose_urls_client", 0) + 1
        else:
            cnt_dict["compose_user_mentions_client"] = cnt_dict.setdefault("compose_user_mentions_client", 0) + 1

        maxi = max(compose_text_client, compose_media_client, compose_unique_id_client, compose_creator_client)
        if maxi == compose_creator_client:
            print("compose_creator_client: ", json_data["traceID"])
            cnt_dict["compose_creator_client"] = cnt_dict.setdefault("compose_creator_client", 0) + 1
        elif maxi == compose_media_client:
            print("compose_media_client: " , json_data["traceID"])
            cnt_dict["compose_media_client"] = cnt_dict.setdefault("compose_media_client", 0) + 1
        elif maxi == compose_unique_id_client:
            print("compose_unique_id_client: ", json_data["traceID"])
            cnt_dict["compose_unique_id_client"] = cnt_dict.setdefault("compose_unique_id_client", 0) + 1
        else:
            cnt_dict["compose_text_client"] =  cnt_dict.setdefault("compose_text_client", 0) + 1

print("\n\n\n")
print(len(omni_dict.keys()))

for keys, value in omni_dict.items():
    print(keys, ": { \n        cnt: ", len(value), "\n        Mean:  ", statistics.mean(value), "\n        Median: ", statistics.median(value), "\n        Mode:  ", statistics.mode(value),  "\n        Min:  ", min(value), "\n        Max:  ", max(value), "\n}")

print("Cnt dictionary\n\n")

for keys, value in cnt_dict.items():
    print(keys, " : ", value)

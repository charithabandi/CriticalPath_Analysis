from matplotlib.axis import XAxis
import os
import json
import numpy
import pandas
import matplotlib.pyplot as plt
import statistics

opcnt = json.load(open('opcnt_results.json', 'r'))
xAxis = [key for key, value in opcnt.items()]
yAxis = [value for key, value in opcnt.items()]

'''
## LINE GRAPH ##
plt.bar(xAxis,yAxis, color='maroon', marker='o')
plt.xlabel('variable')
plt.ylabel('value')
'''
## BAR GRAPH ##
fig = plt.figure()
plt.bar(xAxis,yAxis, color='maroon')
plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
plt.ylabel('operation counts')


mean_results = {}
omni_results = json.load(open('omni_results.json', 'r'))
xAxis = [key for key, value in opcnt.items()]
for key, data in omni_results.items():
  mean_results[key] = []
  mean_results[key].append(statistics.mean(d["total_duration"] for d in data))
  mean_results[key].append(statistics.mean(d["self_duration"] for d in data))
  mean_results[key].append(statistics.mean(d["cp_duration"] for d in data))
  mean_results[key].append(statistics.mean(d["percent_duration"] for d in data))
  print(key, " ", round(mean_results[key][0], 2) , " ", round(mean_results[key][1], 2) , " ", round(mean_results[key][2], 2) , " ", round(mean_results[key][3]))


tot_dur = [value[0] for key, value in mean_results.items()]
self_dur = [value[0] for key, value in mean_results.items()]
cp_dur = [value[0] for key, value in mean_results.items()]
percent_dur = [value[0] for key, value in mean_results.items()]

fig = plt.figure()
plt.bar(xAxis,tot_dur, color='maroon')
plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
plt.ylabel('Total duration')

fig = plt.figure()
plt.bar(xAxis,self_dur, color='maroon')
plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
plt.ylabel('Self duration')

fig = plt.figure()
plt.bar(xAxis,cp_dur, color='maroon')
plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
plt.ylabel('CP duration')


fig = plt.figure()
plt.bar(xAxis,percent_dur, color='maroon')
plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
plt.ylabel('percentage duration')





#!/usr/bin/evv python

import os
import json
import numpy
import pandas
import matplotlib.pyplot as plt

opcnt_file = "/users/chbandi/traces/opcnt_results.json"
omni_results_file = "/users/chbandi/traces/omni_result.json"

def lets_plot_graphs():
    opcnt = json.load(open('opcnt_results.json', 'r'))
    xAxis = [key for key, value in opcnt.items()]
    yAxis = [value for key, value in opcnt.items()]
    
    fig = plt.figure()
    plt.bar(xAxis,yAxis, color='maroon')
    plt.xticks(range(len(xAxis)),xAxis, rotation = 'vertical' )
    plt.ylabel('operation counts')
    
    """
    omni_results = json.load(open('omni_result.json', 'r'))
    xAxis = [key for key, value in opcnt.items()]
    yAxis = [mean(value)[""] for key, value in opcnt.items()]
    """


lets_plot_graphs()

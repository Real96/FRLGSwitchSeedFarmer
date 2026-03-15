import csv
import statistics
from itertools import zip_longest
import json


SUBFRAME_MULTIPLIER = config["REAPEAT_TIMES"]
RAW_FILE_NAME = config["OUTPUT_FILE_NAME"]
PROCESSED_FILENAME = config["PROCESSED_FILE_NAME"]

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


seeds = None
frames = None
times = None
time_unit = 280896/16777216/SUBFRAME_MULTIPLIER
with open(RAW_FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    transposed_data = list(zip(*reader))
    seeds = [int(seed, 16) for seed in transposed_data[0][1:]]
    frames = [int(frame) for frame in transposed_data[1][1:]]
    times = [float(ms) for ms in transposed_data[2][1:]]
indices = list(range(len(seeds)))

positions = {}
for index, seed in enumerate(seeds):
    if seed not in positions:
        positions[seed] = []
    positions[seed].append(times[index])
	
for seed in positions:
    positions[seed].sort()
	
windows = {}
for seed in positions:
    position_list = positions[seed]
    windows[seed] = []
    index = 0
    running_window = []
    while  index < len(position_list):
        if len(running_window) > 0 and position_list[index] - running_window[-1] >= 0.024:
            windows[seed].append(tuple(running_window))
            running_window = []
        running_window.append(position_list[index])
        index+=1
    windows[seed].append(tuple(running_window))
	
averages = [0 for _ in range(len(seeds))]
for index, seed in enumerate(seeds):
    time = times[index]
    window_list = windows[seed]
    for window in window_list:
        if time in window:
            averages[index] = statistics.mean(window)
			
indices.sort(key = lambda x: frames[x])
indices.sort(key = lambda x: times[x])
indices.sort(key = lambda x: averages[x])
for i in range(len(averages)):
    averages[i] = int(round(averages[i]/time_unit))

sorted_seeds = [seeds[x] for x in indices]
sorted_frames = [seeds[x] for x in indices]
sorted_times = [times[x] for x in indices]
sorted_averages = [averages[x] for x in indices]

reduced_seeds = []
reduced_times  = []
last_seed = None
index = 0
while index < len(sorted_seeds):
    if sorted_seeds[index] != last_seed:
        reduced_seeds.append(sorted_seeds[index])
        reduced_times.append(sorted_averages[index])
        last_seed = sorted_seeds[index]
    index+=1

column_headers = ['Seed', f'Seed Time (1/{SUBFRAME_MULTIPLIER}) GBA Frames)']
all_data = [[f"{seed:04X}" for seed in reduced_seeds], reduced_times]
rows = zip_longest(*all_data, fillvalue="")
with open(PROCESSED_FILENAME, "w+", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(column_headers) 
    for row in rows:
        writer.writerow(row)
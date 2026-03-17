import csv, statistics, json
from itertools import zip_longest
from collections import Counter

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SUBFRAME_MULTIPLIER = config["PROCESSED_TIME_UNIT"]
RAW_FILE_NAME = config["OUTPUT_FILE_NAME"]
PROCESSED_FILENAME = config["PROCESSED_FILE_NAME"]

seeds = None
frames = None
times = None
time_unit = 280896 / 16777216 / SUBFRAME_MULTIPLIER

with open(RAW_FILE_NAME, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    transposed_data = list(zip(*reader))
    seeds = [int(seed, 16) for seed in transposed_data[0][1:]]
    frames = [int(frame) for frame in transposed_data[1][1:]]
    times = [float(ms) for ms in transposed_data[2][1:]]

windows = {}
compressed_frames = []
for index in range(len(frames)):
    frame = frames[index]
    if frame not in windows:
        windows[frame] = []
        compressed_frames.append(frame)
    windows[frame].append(seed[index])

compressed_seeds = []
for frame in windows:
    window = windows[frame]
    seed = Counter(window).most_common(1)[0]
    compressed_seeds.append(seed)
    
uncompressed_index = 0
compressed_times = []
for compressed_index, frame in enumerate(frames):
    t = 0
    c = 0
    while uncompressed_index < len(frames) and frame[uncompressed_index] == frame:
        if compressed_seeds[compressed_index] == seeds[uncompressed_index]:
            t+=times[uncompressed_index]
            c+=1
        compressed_index+=1
    average = int(round(t/time_unit))
    compressed_times.append(average)

indices = list(range(len(compressed_frames)))
indices.sort(key=lambda x: compressed_frames[x])

sorted_seeds = [f"{compressed_seeds[x]:04X}" for x in indices]
sorted_times = [compressed_times[x] for x in indices]
sorted_frames = [compressed_seeds[x] for x in indices]

column_headers = ["Seed", f"Seed Time (1/{SUBFRAME_MULTIPLIER}) GBA Frames", "Seed Number"]
all_data = [sorted_seeds, sorted_times, sorted_frames]
rows = zip_longest(*all_data, fillvalue="")

with open(PROCESSED_FILENAME, "w+", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(column_headers)

    for row in rows:
        writer.writerow(row)

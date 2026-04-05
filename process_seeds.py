import csv, json, os
from collections import Counter
from itertools import zip_longest

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SUBFRAME_MULTIPLIER = config["PROCESSED_TIME_UNIT"]
RAW_FILE_NAME_BASE = config["OUTPUT_FILE_NAME_BASE"]
RAW_FILE_NAME = ""
matching_files = [f for f in os.listdir(".") if f.startswith(RAW_FILE_NAME_BASE)]

if not matching_files:
    print(f'No files with name starting with "{RAW_FILE_NAME_BASE}" found.')
    exit()

print("Raw files found:\n")

for i, filename in enumerate(matching_files, start=1):
    print(f"{i}. {filename}")

print()

try:
    choice = int(input("Enter the number of the csv file to process: "))

    if 1 <= choice <= len(matching_files):
        RAW_FILE_NAME = matching_files[choice - 1]
    else:
        print("Invalid selection.")
except ValueError:
    print("Please enter a valid number.")

PROCESSED_FILENAME = config["PROCESSED_FILE_NAME_BASE"] + matching_files[
    choice - 1
].removeprefix(RAW_FILE_NAME_BASE)
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

for frame, seed in zip(frames, seeds):
    if frame not in windows:
        windows[frame] = []
        compressed_frames.append(frame)

    windows[frame].append(seed)

compressed_seeds = []

for window in windows.values():
    seed = Counter(window).most_common(1)[0][0]
    compressed_seeds.append(seed)

compressed_times = []

for compressed_index, frame in enumerate(compressed_frames):
    t = 0
    c = 0
    target_seed = compressed_seeds[compressed_index]

    for uncompressed_seed, uncompressed_frame, uncompressed_time in zip(
        seeds, frames, times
    ):
        if (target_seed, frame) == (uncompressed_seed, uncompressed_frame):
            t += uncompressed_time
            c += 1

    t /= c
    average = int(round(t / time_unit))
    compressed_times.append(average)

indices = list(range(len(compressed_frames)))
indices.sort(key=lambda x: compressed_frames[x])
sorted_seeds = [f"{compressed_seeds[x]:04X}" for x in indices]
sorted_times = [compressed_times[x] for x in indices]
sorted_frames = [compressed_frames[x] for x in indices]

for i in range(0, len(sorted_seeds) - 1):
    seed_one = sorted_seeds[i]
    seed_two = sorted_seeds[i + 1]

    if seed_one == seed_two:
        print(
            f"WARNING: Consecutive seed indices {i} and {i + 1} are identical: {seed_one}"
        )

column_headers = [
    "Seed",
    f"Seed Time (1/{SUBFRAME_MULTIPLIER}) GBA Frames",
    "Seed Number",
]
all_data = [sorted_seeds, sorted_times, sorted_frames]
rows = zip_longest(*all_data, fillvalue="")

with open(PROCESSED_FILENAME, "w+", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(column_headers)

    for row in rows:
        writer.writerow(row)

print(f'\nProcessed seeds file name: "{PROCESSED_FILENAME}"')

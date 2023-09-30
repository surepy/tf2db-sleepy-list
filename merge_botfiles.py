# for my friends.
import json
import os

merged_players = []
merged_file_count = 0
for filename in os.listdir():
    if not filename.startswith('playerlist.sleepy-bots') or filename == "playerlist.sleepy-bots.merged.json":
        continue

    print(f"merging ${filename}");
    data = json.load(open(filename, 'r'))
    merged_file_count += 1
    merged_players = merged_players + data["players"]

all_players_json = {
    "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",
    "file_info": {
        "authors": [ "surepy" ],
        "description": f"sleepy's merged bot list, {merged_file_count} files and {len(merged_players)} bots marked.",
        "title": f"sleepy-bots.merged"
    },
    "players": merged_players
}

# Write the JSON object to a file
with open('playerlist.sleepy-bots.merged.json', 'w') as f:
    json.dump(all_players_json, f, indent=4)

print(f"merge done: {len(merged_players)} bots")
#!/bin/python3
# REQUESTED: simple script to export megascatterbomb's "mega cheater database"
# into a tf2bd list.
# drops all data that isn't cheater or suspicious

# DEPENDENCIES: chompjs <https://pypi.org/project/chompjs/>
# region: Australia

import json
import requests
import chompjs
import time
from pathlib import Path
from datetime import datetime

cheater_count = 0
suspicious_count = 0
dropped_count = 0

def convert_to_tf2bd_attrib(data):
    # well, it works.
    global cheater_count, suspicious_count, dropped_count
    attributes = []

    # yea
    if data['color']['border'] == "#ff3300":
        attributes.append("cheater")
        print(f"marked cheater.")
        cheater_count = cheater_count + 1
    elif data['color']['border'] == "#ffff00":
        attributes.append("suspicious")
        print(f"marked suspicious.")
        suspicious_count = suspicious_count + 1
    else: 
        print(f"dropped. color={data['color']['border']}")
        dropped_count = dropped_count + 1

    return {
        "attributes": attributes,
        "last_seen": {
            "player_name": data["label"],
            "time": 1685362066
        },
        "proof": [
            f"located at x: {data['x']}, y: {data['y']}"
        ],
        "steamid": data["id3"]
    }

# script run time
run_time = int(time.time())
today_str = datetime.today().isoformat()

# we're sending a request, and getting the full site in text (lol)
site_data_str = requests.get("https://megascatterbomb.com/mcd").text

# dump request data into a txt file if cloudflare "under attack" mode is active
# i don't know how to bypass it.
# site_data_str = Path('mcd_data.txt').read_text()

# this is kind of terrible, and probably might break.
data_start_point = "var nodes = new vis.DataSet("

data_start = site_data_str.find(data_start_point)
data_start += len(data_start_point)

# where does our data end?
data_end_point = "var edges = new vis.DataSet(["
data_end = site_data_str.find(data_end_point)

site_data_str = site_data_str[data_start:data_end]

# remove the ");"
site_data_str = site_data_str[:site_data_str.rfind(");")]

# parse the thing
site_data = chompjs.parse_js_object(site_data_str)

player_data = []

for mark_data in site_data:
    print(f"id: {mark_data['id']} | verdict: ", end='')
    # Lazy fix for idiot programmer
    verdict = convert_to_tf2bd_attrib(mark_data)
    if (len(verdict["attributes"]) > 0):
        player_data.append(verdict)

all_players_json = {
    "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",
    "file_info": {
        "authors": [ "megascatterbomb" ],
        "description": f"scraped & converted list from https://megascatterbomb.com/mcd using export_megacheaterdb_as_tf2bd.py at {today_str}.",
        "title": f"megacheaterdb - {today_str}"
    },
    "players": player_data
}

# Write the JSON object to a file
with open('playerlist.megacheaterdb.json', 'w') as f:
    json.dump(all_players_json, f, indent=4)

print(f"Result: {cheater_count} Cheaters, {suspicious_count} Suspicious, {dropped_count} Dropped.")
print(f"Saved {len(player_data)} players to playerlist.megacheaterdb.json (time: {int(time.time()) - run_time}s)")
# Import the xml and requests modules
import xml.etree.ElementTree as ET
import requests
import json
import time

# surepy's tf2bd import script
# 50% of this code is generated using GPT, lol

# simple script for importing all group users for tf2bd ban list.
# i dont want to implement untrusted_groups rn
# remember to remove people that you didn't mean to mark!

# !!!!!!!!!!!!! fill this

# list author (you!)
authors = [
    "surepy"
]

# Replace {url} with the group URL
group_url = ""

# what to mark as? cheater / suspicious / exploiter / etc
mark = "cheater"

# don't mark these people, **steamid64 only**!
whitelist = [
]

# Steam API key
api_key = ""

# sleep between requests
request_sleep = 0

# only add people with this username (for groups with players)
force_username = 0
force_username_data = "Siec"

if not api_key:
    print("API key not set, using member ID as name")

# 

print(f"importing group {group_url}...")

if force_username:
    print(f"NOTE: force_username is set to {force_username_data}.")

# script run time
run_time = int(time.time())

# Initialize the page number and total pages
page = 1
total_pages = 1

def generate_mark(group_id, group_name, user_id, user_name):
    return {
        "attributes": [mark],
        "last_seen": {
            "player_name": user_name,
            "time": run_time
        },
        "proof": [
                f"[GROUP BAN] {group_name} ({group_id})",
                "generated from group_bans.py"
            ],
        "steamid": user_id
    }

def generate_player_marks(group_id, group_name, member_ids):
    player_data = []

    api_player_data = [] 

    # Use the Steam Web API to get the member name
    if api_key:
        # If API key is set, make a request to Steam Web API to get player data
        api_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={','.join(member_ids)}"

        try:
            response = requests.get(api_url).json()
        except requests.exceptions.RequestException as e:
            # Handle any request errors
            print(f'Error: {e}')

        try:
            api_player_data = response['response']['players']
        except (KeyError, IndexError) as e:
            print(f'Error: {e}')


    # we have data from the API, and we should loop that instead
    if force_username: 
        if api_player_data:
            for api_player in api_player_data:
                try:
                    if (api_player['personaname'] == force_username_data):
                        print(f"added {api_player['steamid']} (name: {api_player['personaname']})")
                        player_data.append(
                            generate_mark(
                                group_id, group_name, api_player["steamid"], api_player["personaname"]
                                )
                            )
                    else:
                        print(f"{api_player['personaname']} isn't {force_username_data}, skipping.")
                except (KeyError, IndexError) as e:
                    # Handle any JSON errors
                    print(f'Error: {e}')
                    print(f"obj={api_player}")
                    continue
        else:
            print(f"we can't determine this player ({member_id}), skipping.")
    else:
        if api_player_data:
            for api_player in api_player_data:
                try:
                    print(f"added {api_player['steamid']} (name: {api_player['personaname']})")
                    player_data.append(
                        generate_mark(
                            group_id, group_name, api_player["steamid"], api_player["personaname"]
                            )
                        )
                except (KeyError, IndexError) as e:
                    # Handle any JSON errors
                    print(f'Error: {e}')
                    print(f"obj={api_player}")
                    continue
        # either api key was not set, or api has failed us.
        # fall back to using the member id.
        else:
            for member_id in member_ids:
                print(f"added {member_id}")
                player_data.append(
                    generate_mark(
                        group_id, group_name, member_id, member_id
                        )
                    )
    
    return player_data

# Initialize the list to store the player data
player_data = []

# Loop until the page number exceeds the total pages
while page <= total_pages:
    # Make a web request to get the xml string for the current page
    xml_url = f'https://steamcommunity.com/groups/{group_url}/memberslistxml/?xml=1&p={page}'
    try:
        xml_string = requests.get(xml_url).text
    except requests.exceptions.RequestException as e:
        # Handle any request errors
        print(f'Error: {e}')
        exit()

    # Parse the xml string
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        # Handle any parsing errors
        print(f'Error: {e}')
        exit()

    # Get the total pages from the first page
    if page == 1:
        total_pages = int(root.find('totalPages').text)

    # Print the group name and ID from the first page
    if page == 1:
        group_name = root.find('groupDetails/groupName').text
        group_id = root.find('groupID64').text
        print(f'Group name: {group_name}')
        print(f'Group ID: {group_id}')

    # member id queue to send to api (or add by 100)
    member_id_list = []

    # Loop through the members and print their IDs and names
    for member in root.findall('members/steamID64'):
        # Get the member ID
        member_id = member.text

        # Check if the player is whitelisted
        if member_id in whitelist:
            continue

        # add for 
        member_id_list.append(member_id)
        
        # send a request, every 100 ids and clear member_id_list (incredibly lazy coding)
        if (len(member_id_list) >= 100):
            player_data.extend(generate_player_marks(group_id, group_name, member_id_list))
            member_id_list = []
    
    # if member_id_list not empty after loop, send a request (incredibly lazy coding)
    if member_id_list:
        player_data.extend(generate_player_marks(group_id, group_name, member_id_list))
    
    # Increment the page number
    page += 1

    # sleep between requests if this becomes a problem
    time.sleep(request_sleep)

# Construct the JSON object for all players
all_players_json = {
    "$schema": "https://raw.githubusercontent.com/PazerOP/tf2_bot_detector/master/schemas/v3/playerlist.schema.json",
    "file_info": {
        "authors": authors,
        "description": f"auto-generated file marking all members of {group_url}, (whitelist: {whitelist})",
        "title": f"group ban: {group_url}"
    },
    "players": player_data
}

# Write the JSON object to a file
with open('group_bans.json', 'w') as f:
    json.dump(all_players_json, f, indent=4)

print(f"Saved {len(player_data)} players to group_bans.json (time: {int(time.time()) - run_time}s)")
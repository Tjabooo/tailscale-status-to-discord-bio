import requests
import os
import json
import time

DISCORD_API_URL = 'https://discord.com/api/v9/users'
TAILSCALE_STATUS_COMMAND = 'tailscale status --json'
SLEEP_INTERVAL = 5
TOKEN = '' # Your token here
USER_ID = '' # Your user id here

headers = {
    'authorization': TOKEN
}

def get_discord_user_profile():
    response = requests.get(f'{DISCORD_API_URL}/{USER_ID}/profile?with_mutual_guilds=false&with_mutual_friends_count=false', headers=headers)
    response.raise_for_status()
    user_data = response.json().get("user")
    bio = user_data.get("bio")
    return bio

def get_tailscale_status():
    tailscale_log = os.popen(TAILSCALE_STATUS_COMMAND).read()
    return json.loads(tailscale_log)

def update_discord_status(windows, linux, school, rest):
    bio_update = f'> system status -\n> Windows (Home): {windows}\n> Arch Linux (Home): {linux}\n> Arch Linux (School): {school}\n{rest}'
    response = requests.patch(f'{DISCORD_API_URL}/@me/profile', headers=headers, json={'bio': bio_update})
    response.raise_for_status()
    return response

def main():
    while True:
        discord_bio = get_discord_user_profile()
        windows_status, linux_status, school_status = map(lambda x: x.split(" ")[-1], discord_bio.split("\n")[1:4])

        tailscale_log = get_tailscale_status()
        windows, linux, school = map(lambda key: "Online ✅" if tailscale_log['Peer'][key]['Online'] else "Offline ❌", [
            '',
            '',
            ''
        ]) # Your node keys

        if any(status.split(" ")[0] != current_status for status, current_status in zip([windows, linux, school], [windows_status, linux_status, school_status])):
            response = update_discord_status(windows, linux, school, '\n'.join(discord_bio.split("\n")[4:]))
            print(response, response.content)
            print(f"Windows (Home): {windows.split(' ')[0]}, Arch Linux (Home): {linux.split(' ')[0]}, Arch Linux (School): {school.split(' ')[0]}")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()

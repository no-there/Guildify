import requests
import datetime
import spotipy
import json
import time
import os

posted = False
pause = False

config = json.load(open("config.json"))

spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=config["config"]["SpotifyAPI"]["scopes"], client_id=config["config"]["SpotifyAPI"]["client"], client_secret=config["config"]["SpotifyAPI"]["secret"], redirect_uri=config["config"]["SpotifyAPI"]["redirect"]))

def get_current_track(spotify):
    # get current track

    track = spotify.current_user_playing_track()

    if track == None or track["is_playing"] == False:
        return None 

    return {
        "id": track["item"]["id"],
        "progress_ms": track["progress_ms"]
    }

def get_track_data(spotify, track):
    # get track data

    progress = track["progress_ms"]

    track = spotify.track(track["id"], market=None)

    reset = track["duration_ms"] - progress

    return {
        "name": track["name"],
        "reset": int(reset),
        "artist": [artist["name"] for artist in track["artists"]]
    }

def set_status(track): 
    # Set track as status on Guilded

    url = "https://www.guilded.gg/api/users/me/status"

    if track is None:
        # set status to nothing once, so it doesn't spam API
        
        payload = json.dumps({})
        pause = True
    else:
        payload = json.dumps({
            "content": {
                "object": "value",
                "document": {
                    "object": "document",
                    "data": {},
                    "nodes": [{
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [{
                            "object": "text",
                            "leaves": [{
                                "object": "leaf",
                                "text": f"Listening to {track['name']} by {', '.join(track['artist'])}",
                                "marks": []
                            }]
                        }]
                    }]
                }
            },
            "customReactionId": config["status"]["emoji"],
            "expireInMs": 0
        })

    response = requests.request("POST", url, headers=config["config"]["GuildedAPI"], data=payload)

    if response.status_code != 200:
        print(f"\t ❌ Failed to update status - check your config. (Code: {response.status_code})")
        print(response.text)
        exit()

if __name__ == "__main__":
    while True:
        os.system("cls" if os.name == "nt" else "clear")

        # hide cursor
        print('\033[?25l', end="")

        print("""   ____       _ _     _ _  __       
  / ___|_   _(_) | __| (_)/ _|_   _ 
 | |  _| | | | | |/ _` | | |_| | | |
 | |_| | |_| | | | (_| | |  _| |_| |
  \____|\__,_|_|_|\__,_|_|_|  \__, |
    ⚡ Guildify by not here   |___/ """)


        track = get_current_track(spotify)

        if track is not None:
            # get track data if there is a track playing
            track = get_track_data(spotify, track)
            print(f"\n\t 🎵 Playing {track['name']} by {', '.join(track['artist'])}")
        else:
            print("\n\t 🎵 Nothing currently playing")

        if pause == False or track is not None:
            # prevents spamming API
            set_status(track)

        # convert to seconds / else wait 15s before checking Spotify API
        timer = int(track["reset"] / 1000) if track is not None else 15

        # loop timer to update terminal screen
        for i in range(int(timer)):
            print(f"\t ⌛ Resync in {datetime.timedelta(seconds=round(timer))}", end="\r", flush=True) # convert seconds to hours, minutes & seconds
            # wait 1.1s on last second to prevent capturing the same track
            time.sleep(1 if timer > 1 else 1.1)

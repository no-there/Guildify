import requests
import datetime
import spotipy
import json
import time
import os

config = json.load(open("config.json"))

spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=config["config"]["SpotifyAPI"]["scopes"], client_id=config["config"]["SpotifyAPI"]["client"], client_secret=config["config"]["SpotifyAPI"]["secret"], redirect_uri=config["config"]["SpotifyAPI"]["redirect"]))

def get_current_track(spotify):
    # get current track

    track = spotify.current_user_playing_track()

    if track["is_playing"] == False:
        return None 

    return {
        "id": track["item"]["id"],
        "progress_ms": track["progress_ms"]
    }

def get_track_data(spotify, track):
    # get track data

    if track is None:
        return None

    progress = track["progress_ms"]

    track = spotify.track(track["id"], market=None)

    reset = track["duration_ms"] - progress

    return {
        "name": track["name"],
        "reset": int(reset),
        "artist": [artist["name"] for artist in track["artists"]]
    }

def set_status(track): 
    # set track as status

    url = "https://www.guilded.gg/api/users/me/status"

    if track is None:
        payload = json.dumps({})
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
        print(f"\t❌ Failed to update status")
        print(response.text)
        exit()

if __name__ == "__main__":
    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print('\033[?25l', end="")

        print("""   _____                   _     _    __         
  / ____|                 | |   (_)  / _|        
 | (___    _ __     ___   | |_   _  | |_   _   _ 
  \___ \  | '_ \   / _ \  | __| | | |  _| | | | |
  ____) | | |_) | | (_) | | |_  | | | |   | |_| |
 |_____/  | .__/   \___/   \__| |_| |_|    \__, |
          | |                               __/ |
          |_|                              |___/ """)

        track = get_current_track(spotify)
        track = get_track_data(spotify, track)

        if track is not None:
            print(f"\n\t 🎵 Playing {track['name']} by {', '.join(track['artist'])}")
        else:
            print("\n\t 🎵 Nothing currently playing")

        set_status(track)

        timer = int(track["reset"] / 1000) if track is not None else 10

        for i in range(int(timer)):
            timer = timer - 1

            print(f"\t ⌛ Resync in {datetime.timedelta(seconds=round(timer))}", end="\r", flush=True)

            time.sleep(1 if timer > 1 else 1.1)

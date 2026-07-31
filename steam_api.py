import requests
from dotenv import load_dotenv
import os
import json
load_dotenv()
BACKLOG_FILE = "backlog.json"
API_KEY = os.environ["STEAM_API_KEY"]
#STEAM_ID = os.environ["STEAM_ID"]

def resolve_steam_id( api_key):
    raw_id = input("Enter your Steam-ID: ")

    params_alpha = {
        "key": api_key,
        "vanityurl" : raw_id
    }
    if raw_id.isdigit():
        return raw_id
    else:
        
        response = requests.get(url="https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/", params=params_alpha )
        alpha_response = response.json()
        alpha_steam_id = alpha_response["response"]["steamid"]
        resolved_steam_id = alpha_steam_id
        return resolved_steam_id

url_digits = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"


def load_backlog(filename):
    if not os.path.exists(filename):
        return {}
    else:
        with open(filename,"r") as f:
            return json.load(f)
def save_backlog(backlog,filename):
    with open (filename, "w") as f:
        json.dump(backlog, f, indent=2)
def query(params):
    response = requests.get(url_digits, params=params)
    response.raise_for_status()

    data = response.json() 
    games = data["response"].get("games",[])
    if not games:
        print("No player data found, check STEAM_ID or profile visibility")
    else:
        print(f"Found {len(games)} games")
#        for game in games[:5]:  # just peek at first 5
#           print(f"{game['name']} — {game['playtime_forever']} min played")
    return games
def sync_games(steam_games, backlog):
    for game in steam_games: #existing entry
        appid = str(game["appid"])
        if appid in backlog:
            backlog[appid]["playtime_forever"]= game["playtime_forever"]
            backlog[appid]["name"]= game["name"]
            backlog[appid].setdefault("rating", None)
            backlog[appid].setdefault("notes", "")
        else:
            backlog[appid] = {
                "name" :game["name"],

                "playtime_forever" : game["playtime_forever"],

                "status" : "unplayed",

                "rating": None,

                "notes":""
                }
            
    return backlog
def list_games(backlog, status_filter = None):
    for appid, game in backlog.items():
        if status_filter == None:
            print(appid, game)
        elif game["status"] == status_filter:
                print(appid, game)
def find_appid_by_name(backlog, name_query):
    matches = []
    for appid, game in backlog.items():
        if name_query.lower() in game["name"].lower():
            matches.append(appid)
        else:
            print("No matches")
    return matches
def mark_status(backlog, filename, appid, new_status):
    appid = str(appid)
    if appid in backlog:
        backlog[appid]["status"] = new_status
        save_backlog(backlog, filename)
    else:
        print("Appid not found")



def main():
    
    STEAM_ID = resolve_steam_id(API_KEY)
    print("Resolved to:", STEAM_ID)
    backlog_file = f"backlog_{STEAM_ID}.json"
    params = {
        "key":API_KEY,
        "steamid" :STEAM_ID,
        "include_appinfo" : True,
        "include_played_free_games" : True
    }
    games = query(params)
    backlog = load_backlog(backlog_file)
    backlog = sync_games(games, backlog)
    list_games(backlog)   
    game_to_update =input("Enter a game to update status: ")                 
    find_appid_by_name(backlog, game_to_update)
    mark_status(backlog,backlog_file, appid, new_status)
    list_games(backlog)
    save_backlog(backlog, backlog_file)

if __name__ == "__main__":
    main()
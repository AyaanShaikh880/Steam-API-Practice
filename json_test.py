from steam_api import load_backlog, save_backlog

backlog = load_backlog()

print(backlog)

backlog ["440"] = {
    "name" : "Team Fortress 2",
    "playtime_forever":320,
    "status" : "playing"
}

save_backlog(backlog)
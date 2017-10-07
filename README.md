# Joinbot


| | | 
-|-
Script file | `joinbot.py`
Arguments | `None`
Requirements| `discord.py`
Files required|`bot-token.txt` (will use first and second line as tokens and ignore all other lines)
Notes| Creates folders called `bot-1` and sometimes `bot-2` which store user message counts. (See below)
Folder structure| `./bot-<bot_number>/<server_id>/<month>/` containing files `<user_id>.txt` where the first line is the message count and the second line is the user's name.

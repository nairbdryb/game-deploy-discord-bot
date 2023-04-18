# Game Deploy Discord Bot

# Description
This bot is a discord bot that allows your members to control which games are currently running. Multiple instances of this bot can be run so long as there are not re-used emojis. 

# Deployment
- Clone the repository
- Rename example_env.txt to .env
- Change the values in the .env file
- Change the values in the config.json file

## .env File
BOT_TOKEN: is the token given to you by discords developer portal.

CHANNEL_ID: is the id of the channel you want the bot to send messages to.

FREQUENCY_SECONDS: cooldown in seconds before the server can be changed again.

INSTANCE_NAME: this field defines the name of the server that will appear on the message. This is useful if you have multiple instances of this bot.


## config.json
This file is in json format. It should be an array of json objects with the following keys:

instance_name: the human readable name of the game server or map to run 

map_name: unused? the in-game map name

start_command: command to run to start this instance

stop_command: command to run to stop this instance

emoji: *unique* emoji among all instances, defines the reaction in discord that will start this instance.
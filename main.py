import os
import discord
from dotenv import load_dotenv
import json
import atexit
import time

class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.last_time = 0
        self.frequency = os.getenv('FREQUENCY_SECONDS')
        self.channel = self.get_channel(int(self.channelID))
        await self.send_message()

    async def on_message(self, message):
        '''
        Test function, reads all messages and prints them.
        '''
        print(f'Message form {message.author}: {message.content}')

    def check_time(self):
        '''
        Ensures that the server is not overloaded with requests.
        '''
        if time.time() < self.last_time + int(self.frequency):
            return False
        else:
            return True

    async def on_raw_reaction_add(self, payload):
        '''
        This function handles reactions to the message sent by the bot.
        '''
        if payload.member.bot:
            return
        if payload.channel_id != int(self.channelID):
            return
        for instance in self.config:
            if (instance["emoji"] == payload.emoji.name) and self.check_time():
                print(f"starting instance {instance['instance_name']}")
                # TODO run stop and start commands
                for inst in self.config:
                    if inst["instance_name"] != instance["instance_name"]:
                        os.system(inst["stop_command"])
                os.system(instance["start_command"])
                self.last_time = time.time()
                continue
            elif payload.emoji.name == "♻":
                await self.message.delete()
                self.config = json.load(open("config.json" , "r"))
                await self.send_message()
                break
            # remove reaction no matter the result
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, payload.member)

    def get_status(self):
        os.system("arkmanager status @all | sed -e 's/\x1b\[[0-9;]*m//g' > status.txt") 
        serverData = [{}]
        i = 0
        try:
            with open("status.txt", "r", encoding='UTF-8') as file:
                lines = file.readlines()
            for line in lines:
                if "Running command" in line:
                    serverData[i]["instance_name"] = line.split(" ")[-1].strip().replace("'", "")
                elif "Server running" in line:
                    serverData[i]["running"] = line.split(" ")[-2].strip()
                elif "Steam Players" in line and not "Active" in line:
                    serverData[i]["players"] = line.split(" ")[-3].strip()
                elif "connect link" in line:
                    serverData[i]["connect_link"] = line.split(" ")[-2].strip()
                elif "version" in line:
                    serverData[i]["version"] = line.split(" ")[-2].strip()
                    i+=1 
                    serverData.append({})
            message = ""
            for data in serverData:
                if "instance_name" in data and data["running"] == "Yes":
                    message += f"Current map: **{data['instance_name']}**\nPlayers: {data['players']}\nLink: {data['connect_link']}\nVersion: {data['version']}\n\n"
            if message == "":
                return "No servers are currently running\n\n"
            return message
        except Exception as err:
            return "Unable to get server status\n\n"


    async def send_message(self):
        '''
        This function sends the message to the channel specified in the .env file.
        '''
        if self.channel is not None:
            print(f"found channel: {self.channel}")
            message_content = self.get_status()
            message_content += "These are the maps that are available to be switched to:\n"
            for instance in self.config:
                message_content += f"{instance['instance_name']}: {instance['emoji']}\n"
            message_content += "Please react to this message with the emoji of the instance you want to run.\n React with ♻ to refresh the list."
            # Custom Embed, this is used to add color to the sidebar and a message title
            embed = discord.Embed(title=f"{self.instance_name} Status", description=message_content, color=discord.Colour.random())
            self.message = await self.channel.send(embed=embed)
            for instance in self.config:
                await self.message.add_reaction(instance["emoji"])
            await self.message.add_reaction("♻")

def exit_handler():
    print("\nexiting")
    # for instance in client.config:
    #     print(f"stopping instance {instance['instance_name']}")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    load_dotenv()
    client = DiscordClient(intents = intents)
    atexit.register(exit_handler)
    

    TOKEN = os.getenv('BOT_TOKEN')
    client.channelID = os.getenv('CHANNEL_ID')
    client.instance_name = os.getenv('INSTANCE_NAME')
    file = open("config.json" , "r")
    client.config = json.load(file)
    print(client.channelID)
    client.run(TOKEN)

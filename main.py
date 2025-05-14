import os
import inspect
import discord
import datetime

import getToken

from src.raport import Raport
from src.trackers.trackerGlobal import TrackerGlobal

class MyClient(discord.Client):
    globalTracker = TrackerGlobal()
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves and other bots
        if (message.author == self.user or message.author.bot == True):
            return
        
        elif message.content == "Angleotron help" or message.content == "Ang help":
            reply = inspect.cleandoc("""> Angleotron is a bot that takes notes on all messages sent by users in form of streaks, that user can later read.
            > Currently implemented are following commands:
            > - `Angleotron raport`/`Ang raport` - presents all past streaks
            > - `Angleotron clean`/`Ang clean` - removes all past streaks
            > - `Angleotron autoclean`/`Ang autoclean` - automatically removes all past streaks after requesting raport
            > - `Angleotron listen`/`Ang listen` - makes the bot listen only to channels in specific category. If none is selected, listens to all of them.""")
            await message.channel.send(reply)

        elif message.content == "Angleotron raport" or message.content == "Ang raport":
            raport = self.globalTracker.RequestRaport(message.guild, message.author)
            # Put details into text file    
            now = datetime.datetime.now().strftime("%d%m%Y")
            filename = f"Details - {message.author} {now}.txt"

            # If return is string value
            if type(raport) != Raport:
                await message.channel.send(raport, delete_after=15)
                return

            with open(filename, "w") as file:
                file.write(raport.GetDetails())
            
            # Send message with summary and details
            with open(filename, "rb") as file:
                msgSent = await message.channel.send(raport.GetSummary(), file=discord.File(file, filename))

            # Then send command, if there is any xp to get
            xpCommand = raport.GetRewardCommand(msgSent.jump_url)
            if xpCommand != 0:
                await message.channel.send(xpCommand)

            # Delete original raport request sent by the user from the chat
            # and text file left in the folder
            await message.delete()
            if os.path.exists(filename):
                os.remove(filename)

        elif message.content == "Angleotron clean" or message.content == "Ang clean":
            reply = self.globalTracker.CleanList(message.guild, message.author)
            await message.channel.send(reply)
            await message.delete()

        elif message.content == "Angleotron autoclean" or message.content == "Ang autoclean":
            reply = self.globalTracker.ToggleAutoClean(message.guild, message.author)
            await message.channel.send(reply)
            await message.delete()

        elif message.content == "Angleotron listen" or message.content == "Ang listen":
            reply = self.globalTracker.UpdateListenList(message.guild, message.channel.category)
            await message.channel.send(reply, delete_after=15)
            await message.delete()
            
        else: 
            # Note users message.
            self.globalTracker.NoteMessage(message)


# Process
print("Booting up bot!")

client = MyClient()
token = getToken.GetToken()
client.run(token)

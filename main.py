
import os
import inspect
import discord
import datetime

import getToken
from src.streak import Streak

from typing import List

# Structs
        

class Raport:
    def __init__(self, list: List[Streak], user: discord.User):
        self.user = user
        self.streaks = list

    def GetDetails(self) -> str:
        details = ""

        # Collect details
        for streak in self.streaks:
            if streak.isValid() == True:
                details += streak.PrintStreakRaport() + "\n"
        
        return details
    
    def GetSummary(self) -> str:
        firstStreakDate = self.streaks[0].GetStreakStartDateString()

        # Prepare summary
        summary = f"# {self.user.display_name} - Raport\n"
        summary += f"Collection of streaks starting from {firstStreakDate}\n"

        return summary
    
    def GetRewardCommand(self, sourceLink: str) -> str:
        firstStreakDate = self.streaks[0].GetStreakStartDateString()
        totalTime = 0
        totalXp = 0

        for streak in self.streaks:
            if streak.isValid() == True:
                totalXp += streak.GetXpReward()
                totalTime += streak.GetStreakDurationSeconds()
        
        totalTimeString = f"{(totalTime // 3600):02d}:{((totalTime % 3600) // 60):02d}:{(totalTime % 60):02d}"
        return f"\nCommand: ```!xp +{totalXp} (RP: From {firstStreakDate}, during {totalTimeString} | Details: {sourceLink})```"

    def isValid(self) -> bool:
        for curr in self.streaks:
            if curr.isValid() == True:
                return True
        return False



# Trackers
class TrackerUser:
    def __init__(self, user: discord.User):
        self.user = user
        self.streakList = []

    def AddMessage(self, message: discord.Message) -> None:
        # If there is no streak in list, create new streak
        if len(self.streakList) == 0:
            newStreak = Streak(message.created_at, message.jump_url)
            self.streakList.append(newStreak)
        # If there is at least one streak in the list
        else:
            latestStreak = self.streakList[-1]
            # Check if the curernt streak is ongoing
            if latestStreak.IsOngoing(message.created_at) == True:
                # If so, update the last time
                latestStreak.ExtendStreak(message.created_at, message.jump_url)
            else:
                # If not, create new one.
                newStreak = Streak(message.created_at, message.jump_url)
                self.streakList.append(newStreak)

        print(f"Message by {message.author}\n\tNoted message: ({message.jump_url})\n\tTimestamp ({message.created_at})")
    
    def GetRaport(self) -> Raport:
        # Prepare Raport
        return Raport(self.streakList, self.user)
        
class TrackerServer:
    def __init__(self, server: discord.Guild):
        self.server = server
        self.userTrackers = []
        self.listeningCategoryList = []

    def findUser(self, userId: int) -> TrackerUser:
        for x in self.userTrackers:
            if x.user.id == userId:
                return x
        return False

    def NoteMessage(self, message: discord.Message) -> None:
        # Check if bot should listen to message's channel
        # Check only if there are any categories selected
        if len(self.listeningCategoryList) > 0:
            channelPresent = False
            for x in self.listeningCategoryList:
                if message.channel.category.id == x.id:
                    channelPresent = True
            if channelPresent == False:
                print(f"{message.author} has sent a message, which is ignore due to listening rule.")
                return # If category is not on the list, ignore message

        # If bot is allowed to listen to that category, process message
        result = self.findUser(message.author.id)
        if result == False:
            # Add new user tracker
            newTracker = self.RegisterNewTracker(message.author)
            newTracker.AddMessage(message)
        else:
            # Add message to existing tracker
            result.AddMessage(message)

    def RequestRaport(self, user: discord.User) -> Raport:
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            return result.GetRaport()
        
    def RegisterNewTracker(self, user: discord.User) -> TrackerUser:
        print(f"Registring new User Tracker for {user.name} (user) on server {self.server.name}")
        newTracker = TrackerUser(user)
        self.userTrackers.append(newTracker)
        return newTracker
    
    def CleanList(self, user: discord.User) -> str:
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            self.userTrackers.remove(result)
            return f"Past streaks have been removed."
        
    def ToggleListeningCategory(self, category: discord.CategoryChannel) -> str:
        for x in self.listeningCategoryList:
            if category.id == x.id:
                self.listeningCategoryList.remove(x)
                print(f"Now I won't be listening to channels from category \"{x.name}\".")
                return f"Now I won't be listening to channels from category \"{x.name}\"."
        
        self.listeningCategoryList.append(category)
        print(f"Now I will be listening to channels from category \"{category.name}\".")
        return f"Now I will be listening to channels from category \"{category.name}\"."

class TrackerGlobal:
    def __init__(self):
        self.serverTrackers = []
        
    def findServer(self, serverId: int):
        for x in self.serverTrackers:
            if x.server.id == serverId:
                return x
        return False

    def NoteMessage(self, message: discord.Message) -> None:
        result = self.findServer(message.guild.id)
        if result == False:
            # Add new user tracker
            newTracker = self.RegisterNewTracker(message.guild)
            newTracker.NoteMessage(message)
        else:
            # Add message to existing tracker
            result.NoteMessage(message)

    def RequestRaport(self, server: discord.Guild, user: discord.User) -> Raport:
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.RequestRaport(user)
        
    def CleanList(self, server: discord.guild, user: discord.User) -> str:
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.CleanList(user)

    def RegisterNewTracker(self, server: discord.Guild) -> TrackerServer:
        print(f"Registring new Server Tracker for {server.name} (Guild)")
        newTracker = TrackerServer(server)
        self.serverTrackers.append(newTracker)
        return newTracker

    def UpdateListenList(self, server: discord.Guild, category: discord.CategoryChannel) -> str:
        result = self.findServer(server.id)
        if result == False:
            result = self.RegisterNewTracker(server)
        
        return result.ToggleListeningCategory(category)









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
            > - `Angleotron clean`/`Ang autoclean` - automatically removes all past streaks after requesting raport
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
            await message.channel.send(raport.GetRewardCommand(msgSent.jump_url))

            # Delete original raport request sent by the user from the chat
            # and text file left in the folder
            await message.delete()
            if os.path.exists(filename):
                os.remove(filename)

        elif message.content == "Angleotron clean" or message.content == "Ang clean":
            reply = self.globalTracker.CleanList(message.guild, message.author)
            await message.channel.send(reply, delete_after=15)
            await message.delete()

        elif message.content == "Angleotron autoclean" or message.content == "Ang autoclean":
            #reply = self.globalTracker.UpdateListenList(message.guild, message.channel.category)
            await message.channel.send("Not implemented yet", delete_after=15)
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

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
token = getToken.GetToken()
client.run(token)

import inspect
import discord
import datetime
import getToken

class TrackerGlobal:
    def __init__(self):
        self.serverTrackers = []
        
    def findServer(self, serverId: int):
        for x in self.serverTrackers:
            if x.serverId == serverId:
                return x
        return False

    def NoteMessage(self, message: discord.Message):
        result = self.findServer(message.guild.id)
        if result == False:
            # Add new user tracker
            newTracker = self.RegisterNewTracker(message.guild)
            newTracker.NoteMessage(message)
        else:
            # Add message to existing tracker
            result.NoteMessage(message)

    def RequestRaport(self, server: discord.Guild, user: discord.User):
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.RequestRaport(user)
        
    def CleanList(self, server: discord.guild, user: discord.User):
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.CleanList(user)

    def RegisterNewTracker(self, server: discord.Guild):
        print(f"Registring new Server Tracker for {server.name} (Guild)")
        newTracker = TrackerServer(server.id)
        self.serverTrackers.append(newTracker)
        return newTracker

    def UpdateListenList(self, server: discord.Guild, category: discord.CategoryChannel):
        result = self.findServer(server.id)
        if result == False:
            result = self.RegisterNewTracker(server)
        
        return result.ToggleListeningCategory(category)

class TrackerServer:
    def __init__(self, serverId: int):
        self.serverId = serverId
        self.userTrackers = []
        self.listeningCategoryList = []

    def findUser(self, userId: int):
        for x in self.userTrackers:
            if x.userId == userId:
                return x
        return False

    def NoteMessage(self, message: discord.Message):
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
            newTracker = TrackerUser(message.author.id)
            self.userTrackers.append(newTracker)
            newTracker.AddMessage(message)
        else:
            # Add message to existing tracker
            result.AddMessage(message)

    def RequestRaport(self, user: discord.User):
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            return result.GetRaport()
        
    def CleanList(self, user: discord.User):
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            self.userTrackers.remove(result)
            return f"Past streaks have been removed."
        
    def ToggleListeningCategory(self, category: discord.CategoryChannel):
        for x in self.listeningCategoryList:
            if category.id == x.id:
                self.listeningCategoryList.remove(x)
                print(f"Now I won't be listening to channels from category \"{x.name}\".")
                return f"Now I won't be listening to channels from category \"{x.name}\"."
        
        self.listeningCategoryList.append(category)
        print(f"Now I will be listening to channels from category \"{category.name}\".")
        return f"Now I will be listening to channels from category \"{category.name}\"."

class TrackerUser:
    def __init__(self, userId: int):
        self.userId = userId
        self.streakList = []

    def AddMessage(self, message: discord.Message):
        # If there is no streak in list, add message
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
    
    def GetRaport(self):
        finalString = ""

        for streak in self.streakList:
            finalString += streak.PrintRaport() + "\n"

        # when all messages have been checked, close the last
        return finalString
        


class Streak:
    def __init__(self, begTime: datetime.datetime, begMsgLink: str):
        self.beginTime = begTime
        self.lastTime = begTime
        self.begMsgLink = begMsgLink
        self.lastMsgLink = begMsgLink

    # Check if streak is ongoing
    def IsOngoing(self, currTime: datetime.datetime):
        # Check if time between last msg and current is lesser then streak length
        return self.lastTime + datetime.timedelta(minutes=STREAK_LENGTH) > currTime

    def isValid(self):
        if self.beginTime != self.lastTime:
            return True
        else:
            return False

    # Update latest msg data
    def ExtendStreak(self, newTime: datetime.datetime, newLink: str):
        self.lastTime = newTime
        self.lastMsgLink = newLink

    # Present data as string
    def PrintRaport(self):
        dif = self.lastTime - self.beginTime

        streakStartString = self.beginTime.strftime("%d/%m/%Y %H:%M:%S")
        durationString = f"{(dif.seconds // 3600):02d}:{((dif.seconds % 3600) // 60):02d}:{(dif.seconds % 60):02d}"
        xpReward = (dif.seconds // 60) // STREAK_TRESHOLD * XP_PER_TRESHOLD

        finalString = f"Streak found: {streakStartString} lasted {durationString} from {self.begMsgLink} to {self.lastMsgLink}"
        if xpReward > 0:
            finalString += f"\nCommand: ```!xp +{xpReward} (RP: From {self.begMsgLink} to {self.lastMsgLink}, during {durationString})```"

        return finalString














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
            > - `Angleotron listen`/`Ang listen` - makes the bot listen only to channels in specific category. If none is selected, listens to all of them.""")
            await message.channel.send(reply)

        elif message.content == "Angleotron raport" or message.content == "Ang raport":
            reply = self.globalTracker.RequestRaport(message.guild, message.author)
            await message.channel.send(reply)
            await message.delete()

        elif message.content == "Angleotron clean" or message.content == "Ang clean":
            reply = self.globalTracker.CleanList(message.guild, message.author)
            await message.channel.send(reply, delete_after=60)
            await message.delete()

        elif message.content == "Angleotron listen" or message.content == "Ang listen":
            reply = self.globalTracker.UpdateListenList(message.guild, message.channel.category)
            #await message.channel.send(reply, ephemeral=True)
            await message.channel.send(reply, delete_after=15)
            await message.delete()

        else: 
            # Note users message.
            self.globalTracker.NoteMessage(message)


# Process
print("Booting up bot!")
STREAK_LENGTH = 22 # in minutes
STREAK_TRESHOLD = 60 # in minutes
XP_PER_TRESHOLD = 100 # in minutes

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
token = getToken.GetToken()
client.run(token)

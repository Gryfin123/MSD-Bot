'''
To do:
- Blacklistowanie kanałów
- Liczenie Streaków na bierząco
- kasowanie zapisków dłuższych niż tydzień (Streaków których ostatnia wiadomość jest starsza niż tydzień)
- na koniec raportu dać komende do skopiowania ( ```!xp +### (RP: [raport]))

Done:
- podział na serwery
- wykluczanie botów (np. Avrae, użytkownicy tupperowi, etc.)
- komenda na kasowanie przeszłych zapisków.
'''
import inspect
import discord
import datetime
import getToken

class TrackerGlobal:
    def __init__(self):
        self.serverTrackers = []
        
    def findServer(self, serverId):
        for x in self.serverTrackers:
            if x.serverId == serverId:
                return x
        return False

    def NoteMessage(self, message):
        result = self.findServer(message.guild.id)
        if result == False:
            # Add new user tracker
            print(f"Registring first message on {message.guild.name} (Guild)")
            newTracker = TrackerServer(message.guild.id)
            self.serverTrackers.append(newTracker)
            newTracker.NoteMessage(message)
        else:
            # Add message to existing tracker
            result.NoteMessage(message)

    def RequestRaport(self, server, user):
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.RequestRaport(user)
        
    def CleanList(self, server, user):
        result = self.findServer(server.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name} in {server.name}"
        else:
            return result.CleanList(user)

class TrackerServer:
    def __init__(self, serverId):
        self.serverId = serverId
        self.userTrackers = []

    def findUser(self, userId):
        for x in self.userTrackers:
            if x.userId == userId:
                return x
        return False

    def NoteMessage(self, message):
        result = self.findUser(message.author.id)
        if result == False:
            # Add new user tracker
            print(f"Registring first message of {message.author} on {message.guild}")
            newTracker = TrackerUser(message.author.id)
            self.userTrackers.append(newTracker)
            newTracker.AddMessage(message)
        else:
            # Add message to existing tracker
            result.AddMessage(message)

    def RequestRaport(self, user):
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            return result.GetRaport()
        
    def CleanList(self, user):
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            self.userTrackers.remove(result)
            return f"Past streaks have been removed."

class TrackerUser:
    def __init__(self, userId):
        self.userId = userId
        self.streakList = []

    def AddMessage(self, message):
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

        print(f"\tNoted message: ({message.jump_url})\n\tTimestamp ({message.created_at})")
    
    def GetRaport(self):
        finalString = ""

        for streak in self.streakList:
            finalString += streak.PrintRaport()

        # when all messages have been checked, close the last
        return finalString
        

class Streak:
    def __init__(self, begTime, begMsgLink):
        self.beginTime = begTime
        self.lastTime = begTime
        self.begMsgLink = begMsgLink
        self.lastMsgLink = begMsgLink

    # Check if streak is ongoing
    def IsOngoing(self, currTime):
        # Check if time between last msg and current is lesser then streak length
        return self.lastTime + datetime.timedelta(minutes=STREAK_LENGTH) > currTime
        
    # Update latest msg data
    def ExtendStreak(self, newTime, newLink):
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
            > - `Angleotron ignore`/`Ang ignore` - removes channel where it is used on from survailence""")
            await message.channel.send(reply)

        elif message.content == "Angleotron raport" or message.content == "Ang raport":
            reply = self.globalTracker.RequestRaport(message.guild, message.author)
            await message.channel.send(reply)

        elif message.content == "Angleotron clean" or message.content == "Ang clean":
            reply = self.globalTracker.CleanList(message.guild, message.author)
            await message.channel.send(reply)

        elif message.content == "Angleotron ignore" or message.content == "Ang ignore":
            reply = "not implemented"
            await message.channel.send(reply)

        else: 
            # Note users message.
            print(f"{message.author} has sent a message.")
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

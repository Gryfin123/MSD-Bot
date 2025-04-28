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
        self.streakLength = 22 # in minutes
        self.minimumStreakLength = 60 # in minutes

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
            return result.GetRaport(self.streakLength, self.minimumStreakLength)
        
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
        self.messageList = {}

    def AddMessage(self, message):
        self.messageList[message.created_at] = message.jump_url
        print(f"Noted message with link ({message.jump_url}) and timestamp ({message.created_at})")

    def GetRaport(self, streakLength, minLength):
        finalString = ""

        streakBeg = False
        streakLast = False

        for msgTime in self.messageList:
            # If it's first list element
            if streakBeg == False:
                streakBeg = msgTime   
                streakLast = msgTime
                continue

            # Check if time between last msg and current is lesser then streak length
            if streakLast + datetime.timedelta(minutes=streakLength) > msgTime:
                # If so, update streakLast and go to next message
                streakLast = msgTime
                continue
            else:
                # If not, check how much time passed between streakBeg and streakLast, 
                #  prepare and append final string 
                #  and set streakBeg to this message.
                dif = streakLast - streakBeg
                link1 = self.messageList[streakBeg]
                link2 = self.messageList[streakLast]

                streakStartString = streakBeg.strftime("%d/%m/%Y %H:%M:%S")
                durationString = f"{(dif.seconds // 3600):02d}:{((dif.seconds % 3600) // 60):02d}:{(dif.seconds % 60):02d}"
                amountXP = (dif.seconds // 60) // minLength

                information = f"Streak found: {streakStartString} lasted {durationString} from {link1} to {link2}\n"
                commandLink = f"Copy & Paste po xp: ```!xp +{amountXP} (RP: Od {link1} do {link2}, trwający {durationString})```\n"

                finalString += f"{information} {commandLink}"

                streakBeg = msgTime
                streakLast = msgTime

        # when all messages have been checked, close the last -
        dif = streakLast - streakBeg
        link1 = self.messageList[streakBeg]
        link2 = self.messageList[streakLast]

        streakStartString = streakBeg.strftime("%d/%m/%Y %H:%M:%S")
        durationString = f"{(dif.seconds // 3600):02d}:{((dif.seconds % 3600) // 60):02d}:{(dif.seconds % 60):02d}"
        amountXP = (dif.seconds // 60) // minLength

        information = f"Streak found: {streakStartString} lasted {durationString} from {link1} to {link2}\n"
        commandLink = f"Copy & Paste po xp: ```!xp +{amountXP} (RP: Od {link1} do {link2}, trwający {durationString})```\n"

        finalString += f"{information} {commandLink}"

        return finalString















# Process
print("Booting up bot!")

class MyClient(discord.Client):
    globalTracker = TrackerGlobal()
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves and other bots
        if (message.author == self.user or message.author.bot == True):
            return

        elif message.content == "Angleotron raport" or "Ang raport":
            reply = self.globalTracker.RequestRaport(message.guild, message.author)
            await message.channel.send(reply)

        elif message.content == "Angleotron clean" or "Ang clean":
            reply = self.globalTracker.CleanList(message.guild, message.author)
            await message.channel.send(reply)

        else: 
            # Note users message.
            print(f"{message.author} has sent a message.")
            self.globalTracker.NoteMessage(message)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
token = getToken.GetToken()
client.run(token)

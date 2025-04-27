'''
To do:
- Blacklistowanie kanałów
- podział na serwery
- wykluczanie botów (np. Avrae, użytkownicy tupperowi, etc.)
- Liczenie Streaków na bierząco
- kasowanie zapisków dłuższych niż tydzień (Streaków których ostatnia wiadomość jest starsza niż tydzień)
- na koniec raportu dać komende do skopiowania ( ```!xp +### (RP: [raport]))


'''
import discord
import datetime
import getToken

class TrackerGlobal:
    streakLength = 22 # in minutes
    minimumStreakLength = 60 # in minutes
    def __init__(self):
        self.trackers = []

    def findUser(self, userId):
        for x in self.trackers:
            if x.userId == userId:
                return x
        return False

    def NoteMessage(self, message):
        result = self.findUser(message.author.id)
        if result == False:
            # Add new user tracker
            print(f"Registring first message of {message.author}")
            newTracker = TrackerUser(message.author.id)
            self.trackers.append(newTracker)
            newTracker.AddMessage(message)
        else:
            # Add message to existing tracker
            result.AddMessage(message)

    def RequestRaport(self, user):
        result = self.findUser(user.id)
        if result == False:
            return f"There are no noted messages sent by {user.global_name}"
        else:
            return result.GetRaport(self.streakLength)

class TrackerServer:
    pass




class TrackerUser:
    def __init__(self, userId):
        self.userId = userId
        self.messageList = {}

    def AddMessage(self, message):
        self.messageList[message.created_at] = message.jump_url
        print(f"Noted message with link ({message.jump_url}) and timestamp ({message.created_at})")

    def GetRaport(self, streakLength):
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
                amountXP = (dif.seconds // 60) // TrackerGlobal.minimumStreakLength

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
        amountXP = (dif.seconds // 60) // TrackerGlobal.minimumStreakLength

        information = f"Streak found: {streakStartString} lasted {durationString} from {link1} to {link2}\n"
        commandLink = f"Copy & Paste po xp: ```!xp +{amountXP} (RP: Od {link1} do {link2}, trwający {durationString})```\n"

        finalString += f"{information} {commandLink}"

        return finalString















# Process
print("I start!")

class MyClient(discord.Client):
    globalTracker = TrackerGlobal()
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        elif message.content == "Angelotron raport":
            text = self.globalTracker.RequestRaport(message.author)
            await message.channel.send(text)

        else:
            # Note message in user list.
            print(f"{message.author} has sent a message.")
            self.globalTracker.NoteMessage(message)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
token = getToken.GetToken()
client.run(token)
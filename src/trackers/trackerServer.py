import discord

from src.raport import Raport
from src.trackers.trackerUser import TrackerUser

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

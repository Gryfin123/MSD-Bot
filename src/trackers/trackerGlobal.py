import discord

from src.raport import Raport
from src.trackers.trackerServer import TrackerServer

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

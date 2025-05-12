import discord

from src.streak import Streak
from src.raport import Raport

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
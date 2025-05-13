import discord

from typing import List
from src.streak import Streak

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
        
        if details == "":
            details = "No valid streaks were found."

        return details
    
    def GetSummary(self) -> str:
        firstStreakDate = self.streaks[0].GetStreakStartTimestampString()

        # Prepare summary
        summary = f"# {self.user.display_name} - Raport\n"
        summary += f"Collection of streaks starting from <t:{firstStreakDate}:f>. Remember to use `Ang clean` to remove streaks if they are not removed automatically to make it easier to use.\n"

        return summary
    
    def GetRewardCommand(self, sourceLink: str) -> str:
        firstStreakDate = self.streaks[0].GetStreakStartTimestampString()
        totalTime = 0
        totalXp = 0

        for streak in self.streaks:
            if streak.isValid() == True:
                totalXp += streak.GetXpReward()
                totalTime += streak.GetStreakDurationSeconds()
        
        totalTimeString = f"{(totalTime // 3600):02d}:{((totalTime % 3600) // 60):02d}:{(totalTime % 60):02d}"
        #totalTimeString = f"<t:{totalTime}:f>"
        return f"\nCommand: ```!xp +{totalXp} (RP: From <t:{firstStreakDate}:f>, during {totalTimeString} | Details: {sourceLink})```"

    def isValid(self) -> bool:
        for curr in self.streaks:
            if curr.isValid() == True:
                return True
        return False

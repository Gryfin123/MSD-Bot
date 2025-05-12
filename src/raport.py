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

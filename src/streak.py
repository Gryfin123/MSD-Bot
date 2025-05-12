import datetime
import math
from src.globalVars import GlobalVars

class Streak:
    def __init__(self, begTime: datetime.datetime, begMsgLink: str):
        self.beginTime = begTime
        self.lastTime = begTime
        self.begMsgLink = begMsgLink
        self.lastMsgLink = begMsgLink

    # Check if streak is ongoing
    def IsOngoing(self, currTime: datetime.datetime) -> bool:
        # Check if time between last msg and current is lesser then streak length
        return self.lastTime + datetime.timedelta(minutes = GlobalVars.STREAK_LENGTH) > currTime

    def isValid(self) -> bool:
        if self.beginTime != self.lastTime:
            return True
        else:
            return False

    def GetStreakDurationSeconds(self) -> int:
        return (self.lastTime - self.beginTime).seconds

    def GetStreakDurationString(self) -> int:
        dif = self.GetStreakDurationSeconds()
        return f"{(dif // 3600):02d}:{((dif % 3600) // 60):02d}:{(dif % 60):02d}"
    
    def GetStreakStartTimestampString(self) -> str:
        return  math.floor(self.beginTime.timestamp())
    
    def GetStreakStartDateString(self) -> str:
        return  self.beginTime.strftime("%d/%m/%Y %H:%M:%S")
    
    def GetStreakLastDateString(self) -> str:
        return  self.lastTime.strftime("%d/%m/%Y %H:%M:%S")
    
    def GetXpReward(self) -> int:
        dif = self.GetStreakDurationSeconds()
        return (dif // 60) // GlobalVars.STREAK_TRESHOLD * GlobalVars.XP_PER_TRESHOLD

    # Update latest msg data
    def ExtendStreak(self, newTime: datetime.datetime, newLink: str) -> None:
        self.lastTime = newTime
        self.lastMsgLink = newLink

    # Present streak as string
    def PrintStreakRaport(self) -> str:
        return f"{self.GetStreakStartDateString()} - {self.GetStreakLastDateString()} (UTC)| {self.GetXpReward()}xp | Lasted {self.GetStreakDurationString()} from {self.begMsgLink} to {self.lastMsgLink}"

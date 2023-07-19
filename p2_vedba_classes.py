from variables import *
from config import *
import os
from matplotlib import pyplot as plt
from math import log
import powerlaw

DataDir = PROJECTROOT + DATA + "FeaturesInTotal/"

Files = [f for f in os.listdir(DataDir) if f[-3:] == "csv"]

def hl(mlv):
        if mlv > -3.4:
                return "HM"
        else:
                return "LOW"

def time_vs_activity_levels():
        HyenaNames = [x for (x,y) in TAG_LOOKUP.items()]
        
        FeaturesDir = PROJECTROOT + DATA + "FeaturesInTotal/"

        for Hyena in HyenaNames:
                print("Now working on", Hyena)
                ArrayOfLogMeanVeDBAs, ArrayOfTimes = [], []
                with open(FeaturesDir + Hyena +".csv") as File:
                        FirstLine = True
                        for line in File:
                                if FirstLine:
                                        FirstLine=False
                                        continue
                                ArrayOfLogMeanVeDBAs.append(log(float(line.rstrip("\n").split(",")[14])))
                                ArrayOfTimes.append(int(line.rstrip("\n").split(",")[0]))
                ArrayOfTimes = [HYENA_REC_START_TIMES[Hyena] + dt.timedelta(seconds=x) for x in ArrayOfTimes]
                ArrayOfTimes = [x + dt.timedelta(hours=3) for x in ArrayOfTimes]
                ArrayOfStates = [hl(vedba) for vedba in ArrayOfLogMeanVeDBAs]

                TwentyFourHourProps = []
                for x in range(24):
                        TwentyFourHourProps.append([])
                CurrDate = ArrayOfTimes[0].date()
                CurrHour = ArrayOfTimes[0].hour
                i = 0
                count = 0
                count_act = 0
                while i < len(ArrayOfTimes):
                        if ArrayOfTimes[i].hour == CurrHour:
                                if ArrayOfStates[i] == "HM":
                                        count_act +=3
                                count += 3
                        else:
                                TwentyFourHourProps[CurrHour].append(count_act/count)
                                #print("{},{}".format(CurrHour, count_act/count))
                                CurrHour = ArrayOfTimes[i].hour
                                count, count_act = 0, 0
                        i += 1
                TwentyFourHourProps = [sum(x)/len(x)*100 for x in TwentyFourHourProps]
                plt.plot(range(24), TwentyFourHourProps, label=Hyena)
        plt.xlabel("Hour of the day")
        plt.ylabel("Percentage time in High or Medium activity leveks")
        plt.axvspan(-2, 6, facecolor='black', alpha=0.2)
        plt.axvspan(18, 26, facecolor='black', alpha=0.2)
        plt.xlim(-1, 24)
        plt.legend()
        plt.savefig(PROJECTROOT + FIGURES + "ActivityPatterns_VeDBA.pgf")
        plt.savefig(PROJECTROOT + FIGURES + "ActivityPatterns_VeDBA.png")

if __name__ == "__main__":
    time_vs_activity_levels()

from variables import *
from config import *
import os
from matplotlib import pyplot as plt
from math import log
import powerlaw

DataDir = PROJECTROOT + DATA + "FeaturesInTotal/"

Files = [f for f in os.listdir(DataDir) if f[-3:] == "csv"]

#logvedbas = []
#
#for f in Files:
#        firstLine = True
#        print(f)
#        with open(DataDir+f) as F:
#                for line in F:
#                        if firstLine:
#                                firstLine = False
#                                continue
#                        logvedbas.append(log(float(line.split(",")[14])))
#        print("Now we have", len(logvedbas), "reads.")
#
#plt.xlabel("log mean VeDBA")
#plt.ylabel("Frequency")
##plt.axvline(x=-3.4, color="black", linestyle="dotted")
##plt.axvline(x=0,color="black", linestyle="dotted")
#plt.axvspan(-9, -3.4, facecolor='blue', alpha=0.3)
#plt.axvspan(-3.4, 0, facecolor='yellow', alpha=0.3)
#plt.axvspan(0, 2, facecolor='red', alpha=0.3)
#plt.xlim(-8.5, 1.5)
#plt.hist(logvedbas, 100, density=True, color="black")
#plt.savefig(PROJECTROOT + FIGURES + "VedbaDist.pgf")
#plt.savefig(PROJECTROOT + FIGURES + "VedbaDist.png")

## I found -3.4 and 0.0 to be suitable boundaries to draw thresholds from the histogram
#
#Dur = 0
#CurrState = "Unknown"
#LOWs = []
#MEDs = []
#HIGHs = []
#
#for f in Files:
#        print(f)
#        firstLine = True
#        CurrState = "Unknown"
#
#        with open(DataDir+f) as F:
#                for line in F:
#                        if firstLine:
#                                firstLine = False
#                                continue
#
#                        logv = log(float(line.split(",")[14]))
#
#                        if logv < -3.4:
#                                state = "Low"
#                        elif logv < 0 and logv > -3.4:
#                                state = "Med"
#                        else:
#                                state = "High"
#
#                        if state == CurrState:
#                                Dur += WINDOW_DURATION
#
#                        else:
#                                if CurrState == "Low":
#                                        LOWs.append(Dur)
#                                elif CurrState == "Med":
#                                        MEDs.append(Dur)
#                                elif CurrState == "High":
#                                        HIGHs.append(Dur)
#
#                                Dur = 0
#                                CurrState = state
#        print("Now we have", len(LOWs), len(MEDs), len(HIGHs), "reads.")
#
#fig, axs = plt.subplots(1,3, sharex=True, sharey=True)
#
#fit = powerlaw.Fit(LOWs, xmin=3.0)
#fit.plot_ccdf(color="black", linewidth=1.5, ax = axs[0])
#fit.exponential.plot_ccdf(color='black', linestyle='dotted', label="Exponential", ax=axs[0])	#	Uncomment to show the exponential distribution on the plot
#fit.power_law.plot_ccdf(color='green', linestyle='dotted', label="Zeta", ax=axs[0])
#fit.lognormal.plot_ccdf(color='brown', linestyle='dotted', label="Lognormal", ax=axs[0])
#fit.truncated_power_law.plot_ccdf(color='red', linestyle='dotted', label="Polylog", ax=axs[0])
#axs[0].legend()
#
#fit = powerlaw.Fit(MEDs, xmin=3.0)
#fit.plot_ccdf(color="black", linewidth=1.5, ax = axs[1])
#fit.exponential.plot_ccdf(color='black', linestyle='dotted', label="Exponential", ax=axs[1])	#	Uncomment to show the exponential distribution on the plot
#fit.power_law.plot_ccdf(color='green', linestyle='dotted', label="Zeta", ax=axs[1])
#fit.lognormal.plot_ccdf(color='brown', linestyle='dotted', label="Lognormal", ax=axs[1])
#fit.truncated_power_law.plot_ccdf(color='red', linestyle='dotted', label="Polylog", ax=axs[1])
#
#fit = powerlaw.Fit(HIGHs, xmin=3.0)
#fit.plot_ccdf(color="black", linewidth=1.5, ax = axs[2])
#fit.exponential.plot_ccdf(color='black', linestyle='dotted', label="Exponential", ax=axs[2])	#	Uncomment to show the exponential distribution on the plot
#fit.power_law.plot_ccdf(color='green', linestyle='dotted', label="Zeta", ax=axs[2])
#fit.lognormal.plot_ccdf(color='brown', linestyle='dotted', label="Lognormal", ax=axs[2])
#fit.truncated_power_law.plot_ccdf(color='red', linestyle='dotted', label="Polylog", ax=axs[2])
#axs[0].set_ylabel('Complementary Cumulative Distribution Function')
#axs[1].set_xlabel('Duration of Bout in Seconds')
#axs[0].set_title('Low')
#axs[1].set_title('Medium')
#axs[2].set_title('High')
#
#axs[0].set_facecolor("#b2b2ff")
#axs[1].set_facecolor("#ffffb2")
#axs[2].set_facecolor("#ffb2b2")
#
#plt.savefig('VeDBA_bdds.png')
#plt.savefig('VeDBA_bdds.pgf')
#
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
time_vs_activity_levels()

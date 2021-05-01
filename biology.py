import random
import datetime as dt
import numpy as np
import matplotlib
import math
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import powerlaw
import statistics
from scipy import signal

from config import *
from variables import *

ALL_FEATURES_DIR = PROJECTROOT + DATA + "FeaturesInTotal/"
ALL_CLASSIFICATIONS_DIR = PROJECTROOT + DATA + "ClassificationsInTotal/"

HYENAS = [Hyena for Hyena, Tag in TAG_LOOKUP.items()]

def get_bout_duration_distributions(discrete_data = True):
    """
    Arrives at the bout duration distributions for each state exhibited by the hyenas,
    and saves (a) the AICs in PROJECTROOT/DATA/BiologicalAnalyses/ ; and (b) the
    plots of the cumulative distribution functions in PROJECTROOT/FIGURES/ .

    Args:
        discrete_data (bool): Should the data be treated as discrete? Default is True.
    """

    STATES_DATA_DICT = {}
    for State in STATES:
        STATES_DATA_DICT[State] = []

    for hyena in HYENAS:
        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]

        CurrState = "UNKNOWN"
        Beginning = True
        BeginTime = False

        for i in range(len(TimeAndStates)-1):

            if TimeAndStates[i+1][1] == CurrState:
                pass
            else:
                if Beginning:
                    Beginning = False
                else:
                    STATES_DATA_DICT[CurrState].append(int((TimeAndStates[i+1][0] - BeginTime).total_seconds()))

                BeginTime = TimeAndStates[i+1][0]
                CurrState = TimeAndStates[i+1][1]

    for state, durs in STATES_DATA_DICT.items():
        ERRORS = []
        for i in durs:
            if i <= 0 or i%WINDOW_DURATION != 0:
                ERRORS.append(i)

        if len(ERRORS) > 0:
            print(state, ": the following unreliable durations were computed. ", *ERRORS)

    STATES_AICS = {}
    for state in STATES:

        fit = powerlaw.Fit([x/WINDOW_DURATION for x in STATES_DATA_DICT[state]], discrete=True, xmin=1)
        STATES_AICS[state] = [2*(1 - sum(fit.exponential.loglikelihoods(fit.data))), 2*(2-sum(fit.lognormal.loglikelihoods(fit.data))), 2*(1-sum(fit.power_law.loglikelihoods(fit.data))), 2*(2-sum(fit.truncated_power_law.loglikelihoods(fit.data)))]
        fig = fit.plot_ccdf(linewidth=1.5, color='black')
        fit.exponential.plot_ccdf(linestyle="dotted", color='green', ax=fig, label="Exponential")
        fit.lognormal.plot_ccdf(linestyle="dotted", color='brown', ax=fig, label="Lognormal")
        fit.power_law.plot_ccdf(linestyle="dotted", color='blue', ax=fig, label="Power Law")
        fit.truncated_power_law.plot_ccdf(linestyle="dotted", color='red', ax=fig, label="Truncated Power Law")
        plt.xlabel("Duration in number of consequent windows (each window was 3s)")
        plt.title("{}: Complementary Cumulative Distribution Function".format(state))
        plt.legend()
        plt.savefig(PROJECTROOT + FIGURES + "{}.png".format(state))
        plt.savefig(PROJECTROOT + FIGURES + "{}.pgf".format(state))
        plt.cla()

    DISTS_ORDER = ["Exponential", "Lognormal", "Power Law", "Truncated Power Law"]
    with open(PROJECTROOT + DATA + "BiologicalAnalyses/" + "BDDs.txt", "w") as File:
        File.write('\t\t'.join(["-----"] + DISTS_ORDER + ["Best Fit"]) + "\n")
        for State in STATES:
            File.write("\t\t".join([State] + [str(round(s, 1)) for s in STATES_AICS[State]] + [DISTS_ORDER[STATES_AICS[State].index(min(STATES_AICS[State]))]]) + "\n")

#def get_constant_state_transition_probabilities():
#def get_time_varying_state_transition_probabilities():
#def get_daily_activity_patterns():

def lying_to_lyup_bouts_histogram(individual_wise = False):#TODO Add individual-wise feature

    ListOfSpecificBouts = []
    ListOfLyingBouts = []

    for hyena in HYENAS:

        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]

        CurrState = "UNKNOWN"
        Beginning = True
        BeginTime = False

        for i in range(len(TimeAndStates)-1):

            if TimeAndStates[i+1][1] == CurrState:
                pass
            else:
                if Beginning:
                    Beginning = False
                else:
                    if CurrState == LYING:
                        ListOfLyingBouts.append(int((TimeAndStates[i+1][0] - BeginTime).total_seconds()))
                    if CurrState == LYING and TimeAndStates[i+1][1] == LYUP:
                        ListOfSpecificBouts.append(int((TimeAndStates[i+1][0] - BeginTime).total_seconds()))

                BeginTime = TimeAndStates[i+1][0]
                CurrState = TimeAndStates[i+1][1]

    #plt.hist(ListOfSpecificBouts, color="black", log=True, bins=200)
    fit1 = powerlaw.Fit([x/WINDOW_DURATION for x in ListOfLyingBouts], discrete=True, xmin=1)
    fig1 = fit1.plot_pdf(color="black", label="All LYING bouts")
    fit2 = powerlaw.Fit([x/WINDOW_DURATION for x in ListOfSpecificBouts], discrete=True, xmin=1)
    fit2.plot_pdf(color="gray", label=r"LYING $\rightarrow$ LYUP bouts", ax=fig1)
    plt.xlabel("Bout duration in number of windows, each of 3 seconds")
    plt.ylabel("Probability density function")
    plt.title("Distribution of durations of LYING bouts that transitioned into LYUP")
    plt.legend()
    plt.savefig(PROJECTROOT + FIGURES + "Vigilance_hist_pdfs.png")


def vedba_and_behaviour_correlations():

    LOWS_DIR_GLOBAL = {}
    MIDS_DIR_GLOBAL = {}
    HIGHS_DIR_GLOBAL = {}
    for state in STATES:
        LOWS_DIR_GLOBAL[state] = 0
        MIDS_DIR_GLOBAL[state] = 0
        HIGHS_DIR_GLOBAL[state] = 0

    for hyena in HYENAS:
        FirstLine = True
        VeDBAs = [x.split(",")[14] for x in open(ALL_FEATURES_DIR+hyena+".csv", "r")][1:]
        VeDBAs = [math.log(float(x)) for x in VeDBAs]
        Results_States = [x.split(",")[1].rstrip() for x in open(ALL_CLASSIFICATIONS_DIR+hyena+".csv", "r")][1:]

        LOWS_DIR = {}
        MIDS_DIR = {}
        HIGHS_DIR = {}

        for state in STATES:
            LOWS_DIR[state] = 0
            MIDS_DIR[state] = 0
            HIGHS_DIR[state] = 0


        for i in range(len(VeDBAs)):
            if VeDBAs[i] <= -3.4:
                LOWS_DIR[Results_States[i]] += 1

            elif -3.4 < VeDBAs[i] <= 0:
                MIDS_DIR[Results_States[i]] += 1

            elif VeDBAs[i] > 0:
                HIGHS_DIR[Results_States[i]] +=1

            else:
                raise ValueError("This should not have occured. VeDBA range unrecognised.")

        for state in STATES:
            LOWS_DIR_GLOBAL[state] += LOWS_DIR[state]
            MIDS_DIR_GLOBAL[state] += MIDS_DIR[state]
            HIGHS_DIR_GLOBAL[state] += HIGHS_DIR[state]

    # Now for some normalisation.

    N = sum([count for (state,count) in LOWS_DIR_GLOBAL.items()])
    LOWS_DIR_GLOBAL = {state:(count/N) for (state, count) in LOWS_DIR_GLOBAL.items()}

    N = sum([count for (state,count) in MIDS_DIR_GLOBAL.items()])
    MIDS_DIR_GLOBAL = {state:(count/N) for (state, count) in MIDS_DIR_GLOBAL.items()}

    N = sum([count for (state,count) in HIGHS_DIR_GLOBAL.items()])
    HIGHS_DIR_GLOBAL = {state:(count/N) for (state, count) in HIGHS_DIR_GLOBAL.items()}

    print(LOWS_DIR_GLOBAL, MIDS_DIR_GLOBAL, HIGHS_DIR_GLOBAL)

    
    LEVELS = ["Low", "Medium", "High"]
    LYING_VEDBAS = np.array([LOWS_DIR_GLOBAL[LYING], MIDS_DIR_GLOBAL[LYING], HIGHS_DIR_GLOBAL[LYING]])
    LYUP_VEDBAS = np.array([LOWS_DIR_GLOBAL[LYUP], MIDS_DIR_GLOBAL[LYUP], HIGHS_DIR_GLOBAL[LYUP]])
    STAND_VEDBAS = np.array([LOWS_DIR_GLOBAL[STAND], MIDS_DIR_GLOBAL[STAND], HIGHS_DIR_GLOBAL[STAND]])
    WALK_VEDBAS = np.array([LOWS_DIR_GLOBAL[WALK], MIDS_DIR_GLOBAL[WALK], HIGHS_DIR_GLOBAL[WALK]])
    LOPE_VEDBAS = np.array([LOWS_DIR_GLOBAL[LOPE], MIDS_DIR_GLOBAL[LOPE], HIGHS_DIR_GLOBAL[LOPE]])

    plt.bar(LEVELS, LYING_VEDBAS, 0.35, label=LYING)
    plt.bar(LEVELS, LYUP_VEDBAS, 0.35, label=LYUP, bottom=LYING_VEDBAS)
    plt.bar(LEVELS, STAND_VEDBAS, 0.35, label=STAND, bottom=LYING_VEDBAS + LYUP_VEDBAS)
    plt.bar(LEVELS, WALK_VEDBAS, 0.35, label=WALK, bottom = LYING_VEDBAS + LYUP_VEDBAS + STAND_VEDBAS)
    plt.bar(LEVELS, LOPE_VEDBAS, 0.35, label=LOPE, bottom = LYING_VEDBAS + LYUP_VEDBAS + WALK_VEDBAS + STAND_VEDBAS)

    plt.xlabel("VeDBA levels")
    plt.ylabel("Proportion of time in each state")
    plt.ylim(0,1.1)
    plt.legend()

    plt.savefig(PROJECTROOT + FIGURES + "States_and_VeDBAs.png")


def _isDay(time):

    if 6 <= time.hour < 18:
        return True
    else:
        return False

def day_vs_night_vigilance_behaviours():

    LyupBout_Day_Global = []
    LyupBout_Night_Global = []

    TimeDayLyupsGlobal = 0
    TimeDayLyupsInd = []
    TimeNightLyupsGlobal = 0
    TimeNightLyupsInd = []

    LyingToLyupCount_Day_Global = 0
    TransitionProbDayInd = []
    LyingToLyupCount_Night_Global = 0
    TransitionProbNightInd = []

    Report = open(PROJECTROOT + DATA + "BiologicalAnalyses/" + "ViglanceBehaviourReport.txt", "w")
    Report.write("Vigilance behaviour (LYUP) with day and Night\n\n")

    Vigilance_fig, ax = plt.subplots()

    for hyena in HYENAS:
        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]
        LyupBout_Day = []
        LyupBout_Night = []

        TimeDayLyups = 0
        TimeNightLyups = 0

        LyingToLyupCount_Day = 0
        LyingToLyupCount_Night = 0

        count = 0
        boutLength = 0


        for (time, state) in TimeAndStates[:-1]:
            if state == LYUP:
                boutLength += WINDOW_DURATION

                if _isDay(time):
                    TimeDayLyups += WINDOW_DURATION
                    TimeDayLyupsGlobal += WINDOW_DURATION
                else:
                    TimeNightLyups += WINDOW_DURATION
                    TimeNightLyupsGlobal += WINDOW_DURATION

            elif state == LYING:
                if _isDay(time) and boutLength > 0:#Note boutLength only tracks LYUP states here and later
                    LyupBout_Day.append(boutLength)
                    LyupBout_Day_Global.append(boutLength)
                    boutLength = 0
                elif (not _isDay(time)) and boutLength > 0:#Note boutLength only tracks LYUP states here and later
                    LyupBout_Night.append(boutLength)
                    LyupBout_Night_Global.append(boutLength)
                    boutLength = 0

                if TimeAndStates[count+1][1] == LYUP:
                    if _isDay(time):
                        LyingToLyupCount_Day += 1
                        LyingToLyupCount_Day_Global += 1
                    else:
                        LyingToLyupCount_Night += 1
                        LyingToLyupCount_Night_Global += 1

            else:
                if _isDay(time) and boutLength > 0:#Note boutLength only tracks LYUP states here and later
                    LyupBout_Day.append(boutLength)
                    LyupBout_Day_Global.append(boutLength)
                    boutLength = 0
                elif (not _isDay(time)) and boutLength > 0:#Note boutLength only tracks LYUP states here and later
                    LyupBout_Night.append(boutLength)
                    LyupBout_Night_Global.append(boutLength)
                    boutLength = 0

            count += 1

        Report.write("["+hyena+"]\n")

        TimeInLyup_Day = TimeDayLyups / (TimeDayLyups + TimeNightLyups)
        Report.write("Proportion of time spent in LYUP state:\tDay: {:.3f}\tNight: {:.3f}\n".format(TimeInLyup_Day, 1 - TimeInLyup_Day))
        TimeDayLyupsInd.append(TimeInLyup_Day)
        TimeNightLyupsInd.append(1 - TimeInLyup_Day)

        LyingToLyup_prop_Day = LyingToLyupCount_Day / (LyingToLyupCount_Day + LyingToLyupCount_Night)
        Report.write("Proprtion of LYING states moving to LYUP:\tDay: {:.3f}\tNight: {:.3f}\n".format(LyingToLyup_prop_Day, 1 - LyingToLyup_prop_Day))
        TransitionProbDayInd.append(LyingToLyup_prop_Day)
        TransitionProbNightInd.append(1 - LyingToLyup_prop_Day)

        Day_fit = powerlaw.Fit([x/3 for x in LyupBout_Day], discrete=True, xmin=1)
        Night_fit = powerlaw.Fit([x/3 for x in LyupBout_Night], discrete=True, xmin=1)
        Day_fit.plot_ccdf(linewidth = 1.5, color="red", alpha=0.4, ax=ax)
        Night_fit.plot_ccdf(linewidth = 1.5, color="darkblue", alpha=0.4, ax=ax)

    Report.write("[TOTAL]\n")

    TimeInLyup_Day = TimeDayLyupsGlobal / (TimeDayLyupsGlobal + TimeNightLyupsGlobal)
    Report.write("Proportion of time spent in LYUP state:\tDay: {:.3f} +/- {:.3f} \tNight: {:.3f} +/- {:.3f}\n".format(TimeInLyup_Day, statistics.stdev(TimeDayLyupsInd), 1 - TimeInLyup_Day, statistics.stdev(TimeNightLyupsInd)))

    LyingToLyup_prop_Day = LyingToLyupCount_Day_Global / (LyingToLyupCount_Day_Global + LyingToLyupCount_Night_Global)
    Report.write("Proprtion of LYING states moving to LYUP:\tDay: {:.3f} +/- {:.3f}\tNight: {:.3f} +/- {:.3f}\n".format(LyingToLyup_prop_Day, statistics.stdev(TransitionProbDayInd), 1 - LyingToLyup_prop_Day, statistics.stdev(TransitionProbNightInd)))

    Day_fit = powerlaw.Fit([x/3 for x in LyupBout_Day_Global], discrete=True, xmin=1)
    Night_fit = powerlaw.Fit([x/3 for x in LyupBout_Night_Global], discrete=True, xmin=1)
    Day_fit.plot_ccdf(linewidth = 1.5, color = "red", label="Day bouts", ax=ax)
    Night_fit.plot_ccdf(linewidth = 1.5, color = "darkblue", label = "Night bouts", ax=ax)

    plt.legend()
    plt.xlabel("Number of windows, each of 3 seconds")
    plt.ylabel("CCDF")
    plt.savefig(PROJECTROOT + FIGURES + "LYUP_BDDS_DayVsNight.pdf")

    Report.close()


def hourly_activity_patterns():
    fig_true, axs = plt.subplots(2,1, sharex=True, sharey=True)
    #for i in axs:
    #    i.set_box_aspect(0.5)

    for hyena in HYENAS:
        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]


        DaysAndHours_Dict = {}
        for (time, state) in TimeAndStates:

            if (time.month, time.day, time.hour) not in DaysAndHours_Dict:
                DaysAndHours_Dict[(time.month, time.day, time.hour)] = []

            if state in [WALK, LOPE]:
                DaysAndHours_Dict[(time.month, time.day, time.hour)].append(1)
            else:
                DaysAndHours_Dict[(time.month, time.day, time.hour)].append(0)

        DaysAndHours_Dict = {which_hour:statistics.mean(activity) for (which_hour, activity) in DaysAndHours_Dict.items()}
        HourlyActivityTimeSeries = np.array(list(DaysAndHours_Dict.values()))
                
        autocorrelation = signal.correlate(HourlyActivityTimeSeries, HourlyActivityTimeSeries, mode='same') / len(HourlyActivityTimeSeries)
        lags = signal.correlation_lags(len(HourlyActivityTimeSeries), len(HourlyActivityTimeSeries), mode='same')
        axs[0].plot(lags, autocorrelation, label=hyena)

        random.shuffle(HourlyActivityTimeSeries)
        autocorrelation = signal.correlate(HourlyActivityTimeSeries, HourlyActivityTimeSeries, mode='same') / len(HourlyActivityTimeSeries)
        lags = signal.correlation_lags(len(HourlyActivityTimeSeries), len(HourlyActivityTimeSeries), mode='same')
        axs[1].plot(lags, autocorrelation, label=hyena)

    axs[0].vlines(np.arange(min(lags), max(lags), 24), 0, 0.08, color="black", alpha=0.13)
    axs[1].vlines(np.arange(min(lags), max(lags), 24), 0, 0.08, color="black", alpha=0.13)
    axs[0].legend(fontsize='x-small')
    axs[0].text(-570,0.105,"a", fontsize='large', fontweight='bold')
    axs[1].text(-570,0.105,"b", fontsize='large', fontweight='bold')
    fig_true.supxlabel("Correlation lag in hours")
    fig_true.supylabel("Normalised autocorrelation")
    fig_true.savefig(PROJECTROOT + FIGURES + "HourlyActivityAutocorrelation.pdf")
    

def daily_activity_patterns():
    fig_true, axs = plt.subplots(2,1, sharex=True, sharey=True)

    for hyena in HYENAS:
        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]

        Days_Dict = {}
        for (time, state) in TimeAndStates:

            if (time.month, time.day) not in Days_Dict:
                Days_Dict[(time.month, time.day)] = []

            if state in [WALK, LOPE]:
                Days_Dict[(time.month, time.day)].append(1)
            else:
                Days_Dict[(time.month, time.day)].append(0)

        Days_Dict = {which_day:statistics.mean(activity) for (which_day, activity) in Days_Dict.items()}
        DailyActivityTimeSeries = np.array(list(Days_Dict.values()))
                
        autocorrelation = signal.correlate(DailyActivityTimeSeries, DailyActivityTimeSeries, mode='same') / len(DailyActivityTimeSeries)
        lags = signal.correlation_lags(len(DailyActivityTimeSeries), len(DailyActivityTimeSeries), mode='same')
        axs[0].scatter(lags, autocorrelation, label=hyena, s=0.9)

        random.shuffle(DailyActivityTimeSeries)
        autocorrelation = signal.correlate(DailyActivityTimeSeries, DailyActivityTimeSeries, mode='same') / len(DailyActivityTimeSeries)
        lags = signal.correlation_lags(len(DailyActivityTimeSeries), len(DailyActivityTimeSeries), mode='same')
        axs[1].scatter(lags, autocorrelation, label=hyena, s=0.9)

    axs[0].legend(fontsize='x-small')
    axs[0].text(-24, 0.06,"a", fontsize='large', fontweight='bold')
    axs[1].text(-24, 0.06,"b", fontsize='large', fontweight='bold')
    fig_true.supxlabel("Correlation lag in number of days")
    fig_true.supylabel("Normalised autocorrelation")
    fig_true.savefig(PROJECTROOT + FIGURES + "DailyActivityAutocorrelation.pdf")

#get_bout_duration_distributions()
#lying_to_lyup_bouts_histogram()
#vedba_and_behaviour_correlations()
day_vs_night_vigilance_behaviours()
#hourly_activity_patterns()
#daily_activity_patterns()


import random
import datetime as dt
import numpy as np
import matplotlib
import math
import statistics as stats
#matplotlib.use("Agg")
from matplotlib import pyplot as plt
import powerlaw
import statistics
from scipy import signal, stats

from config import *
from variables import *

ALL_FEATURES_DIR = PROJECTROOT + DATA + "FeaturesInTotal/"
ALL_CLASSIFICATIONS_DIR = PROJECTROOT + DATA + "ClassificationsInTotal/"

HYENAS = [Hyena for Hyena, Tag in TAG_LOOKUP.items()]

# NOT USED IN PAPER
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

#NOT USED IN PAPER
def lying_to_lyup_bouts_histogram(individual_wise = False):#TODO Add individual-wise feature
    """
    Generates histogram of all bouts of LYING that ended in LYUP, contrasts it with histogram of all LYING bouts.
    """

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


def generate_vedba_histograms():
    """
    Plots the histogram of log-mean-VeDBA for all individuals separately, as well as pooled.
    Indicates the three activity levels through colours.
    """

    All_VeDBAs = []
    i = 0

    axes_dict = plt.figure(constrained_layout=True).subplot_mosaic("""
    AB
    AC
    AD
    AE
    AF
    """, gridspec_kw = {"width_ratios":[6,1]}) #Generates the necessary plot subfigures

    alphabets = ["B", "C", "D", "E", "F"]
    for hyena in HYENAS:
        print("Working on", hyena)
        hyena_VeDBAs = []

        FirstLine = True
        VeDBAs = [x.split(",")[14] for x in open(ALL_FEATURES_DIR+hyena+".csv", "r")][1:]
        VeDBAs = [math.log(float(x)) for x in VeDBAs]

        hyena_VeDBAs.extend(VeDBAs)
        All_VeDBAs.extend(VeDBAs)

        axes_dict[alphabets[i]].hist(hyena_VeDBAs, 100, color="black")
        axes_dict[alphabets[i]].set_xticks([])
        axes_dict[alphabets[i]].set_xticklabels([])
        axes_dict[alphabets[i]].set_yticks([])
        axes_dict[alphabets[i]].set_yticklabels([])
        left, right = axes_dict[alphabets[i]].get_xlim()
        bottom, top = axes_dict[alphabets[i]].get_ylim()
        axes_dict[alphabets[i]].text(left, top, hyena, weight="bold", verticalalignment="bottom")

        i += 1

    print("Generating plots...", end=" ")
    main_axis = axes_dict["A"]
    main_axis.set_xlabel("log mean VeDBA")
    main_axis.set_ylabel("Frequency")
    axes_dict["F"].set_xlabel(" ") # to align the bottom of both columns

    main_axis.hist(All_VeDBAs, 100, color="black")
    p,q = main_axis.get_xlim()

    if p > q:
        p,q = q,p
    main_axis.axvspan(xmin=p, xmax=-3.4, color="blue", alpha=0.5)
    main_axis.axvspan(xmin=-3.4, xmax=0, color="yellow", alpha=0.5)
    main_axis.axvspan(xmin=0, xmax=q, color="red", alpha=0.5)
    main_axis.hist(All_VeDBAs, 100, color="black")
    print("done.")
    plt.savefig(PROJECTROOT + FIGURES + "VeDBA_distributions.pdf")        
    plt.savefig(PROJECTROOT + FIGURES + "VeDBA_distributions.png")        



def vedba_and_behaviour_correlations():
    """
    Plots the proportion of each behavioural state in each VeDBA level.
    """

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
    plt.savefig(PROJECTROOT + FIGURES + "States_and_VeDBAs.pdf")


def _isDay(time):

    if 6 <= time.hour < 18:
        return True
    else:
        return False

# NOT USED IN PAPER
def day_vs_night_vigilance_behaviours():
    """
    Reports general statistics about the LYUP state, which we initially thought of as a vigilance state.
    """

    LyupBout_Day_Global = []
    LyupBout_Night_Global = []

    TimeDayLyupsGlobal = 0
    TimeDayTotalGlobal = 0
    TimeDayLyupsInd = []
    TimeNightLyupsGlobal = 0
    TimeNightTotalGlobal = 0
    TimeNightLyupsInd = []

    LyingToLyupCount_Day_Global = 0
    LyingToAnyCount_Day_Global = 0
    TransitionProbDayInd = []
    LyingToLyupCount_Night_Global = 0
    LyingToAnyCount_Night_Global = 0
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
        TimeDayTotal = 0
        TimeNightLyups = 0
        TimeNightTotal = 0

        LyingToLyupCount_Day = 0
        LyingToAnyCount_Day = 0
        LyingToLyupCount_Night = 0
        LyingToAnyCount_Night = 0

        count = 0
        boutLength = 0


        for (time, state) in TimeAndStates[:-1]:
            if _isDay(time):
                TimeDayTotal += WINDOW_DURATION
                TimeDayTotalGlobal += WINDOW_DURATION
            else:
                TimeNightTotal += WINDOW_DURATION
                TimeNightTotalGlobal += WINDOW_DURATION

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

                if TimeAndStates[count+1][1] != LYING:
                    if _isDay(time):
                        LyingToAnyCount_Day += 1
                        LyingToAnyCount_Day_Global += 1
                    else:
                        LyingToAnyCount_Night += 1
                        LyingToAnyCount_Night_Global += 1

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

        TimeInLyup_Day = TimeDayLyups / TimeDayTotal
        TimeInLyup_Night = TimeNightLyups / TimeNightTotal
        Report.write("Proportion of time spent in LYUP state:\tDay: {:.3f}\tNight: {:.3f}\n".format(TimeInLyup_Day, TimeInLyup_Night))
        TimeDayLyupsInd.append(TimeInLyup_Day)
        TimeNightLyupsInd.append(TimeInLyup_Night)

        LyingToLyup_prop_Day = LyingToLyupCount_Day / LyingToAnyCount_Day
        LyingToLyup_prop_Night = LyingToLyupCount_Night / LyingToAnyCount_Night
        Report.write("Proportion of LYING states moving to LYUP:\tDay: {:.3f}\tNight: {:.3f}\n".format(LyingToLyup_prop_Day, LyingToLyup_prop_Night))
        TransitionProbDayInd.append(LyingToLyup_prop_Day)
        TransitionProbNightInd.append(LyingToLyup_prop_Night)

        Day_fit = powerlaw.Fit([x/3 for x in LyupBout_Day], discrete=True, xmin=1)
        Night_fit = powerlaw.Fit([x/3 for x in LyupBout_Night], discrete=True, xmin=1)
        Day_fit.plot_ccdf(linewidth = 1.5, color="red", alpha=0.4, ax=ax)
        Night_fit.plot_ccdf(linewidth = 1.5, color="darkblue", alpha=0.4, ax=ax)

    Report.write("\n[TOTAL]\n")

    TimeInLyup_Day = TimeDayLyupsGlobal / TimeDayTotalGlobal
    TimeInLyup_Night = TimeNightLyupsGlobal / TimeNightTotalGlobal
    Report.write("Proportion of time spent in LYUP state:\tDay: {:.3f} +/- {:.3f} \tNight: {:.3f} +/- {:.3f}\n".format(TimeInLyup_Day, statistics.stdev(TimeDayLyupsInd), TimeInLyup_Night, statistics.stdev(TimeNightLyupsInd)))

    LyingToLyup_prop_Day = LyingToLyupCount_Day_Global / LyingToAnyCount_Day_Global
    LyingToLyup_prop_Night = LyingToLyupCount_Night_Global / LyingToAnyCount_Night_Global
    Report.write("Proportion of LYING states moving to LYUP:\tDay: {:.3f} +/- {:.3f}\tNight: {:.3f} +/- {:.3f}\n".format(LyingToLyup_prop_Day, statistics.stdev(TransitionProbDayInd), LyingToLyup_prop_Night, statistics.stdev(TransitionProbNightInd)))

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
    """
    Plots autocorrelation for the hourly activity time-series with lags 0 through 36.
    Also shuffles the order to remove temporal information before repeating the analysis.
    """
    fig_true, axs = plt.subplots(2,1, sharex=True, sharey=True)
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
        a = list(lags).index(0)
        b = list(lags).index(36)
        axs[0].plot(lags[a:b], autocorrelation[a:b], label=hyena)

        random.shuffle(HourlyActivityTimeSeries)
        autocorrelation = signal.correlate(HourlyActivityTimeSeries, HourlyActivityTimeSeries, mode='same') / len(HourlyActivityTimeSeries)
        lags = signal.correlation_lags(len(HourlyActivityTimeSeries), len(HourlyActivityTimeSeries), mode='same')
        a = list(lags).index(0)
        b = list(lags).index(36)
        axs[1].plot(lags[a:b], autocorrelation[a:b], label=hyena)

    axs[0].axvline(24, color="black", alpha=0.13)
    axs[1].axvline(24, color="black", alpha=0.13)
    axs[0].legend(fontsize='x-small')
    axs[0].set_title("Maintaining sequence order")
    axs[1].set_title("Randomised sequence order")
    fig_true.supxlabel("Correlation lag in hours")
    fig_true.supylabel("Normalised autocorrelation")
    fig_true.savefig(PROJECTROOT + FIGURES + "HourlyActivityAutocorrelation.pdf")
    fig_true.savefig(PROJECTROOT + FIGURES + "HourlyActivityAutocorrelation.png")
    
# NOT USED IN PAPER
def daily_activity_patterns():
    """
    Looks for any autocorrelation in activity levels across days, testing for effects of e.g. fatigue and recuperation.
    """
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


def get_circadian_rhythms():
    """
    Quantifies the daily activity pattern for each hyena by finding average time spent in a movement state
    for each hour of the day.
    """

    time_zone_shift = 3

    x_axis_vals = list(range(12,24)) + list(range(0, 12))
    x_axis_vals = [str(x)+":00" for x in x_axis_vals]
    for i in range(len(x_axis_vals)):
        if len(x_axis_vals[i])== 4:
            x_axis_vals[i] = "0" + x_axis_vals[i]
    fig, ax = plt.subplots()

    ax.axvspan(6.5, 18.5, color="gray", alpha=0.5)

    for hyena in HYENAS:

        hourly_activity_pattern = []
        for i in range(24):
            hourly_activity_pattern.append([])

        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]

        len_hour = 0
        count_active = 0
        First = True

        for time, state in TimeAndStates:

            if First:
                start_hour = time.hour
                First = False

            if state in [WALK, LOPE]:
                count_active += WINDOW_DURATION
            len_hour += WINDOW_DURATION

            if time.hour != start_hour:
                hourly_activity_pattern[start_hour].append(count_active/len_hour)
                len_hour, count_active = 0, 0
                start_hour = time.hour


        hourly_activity_means = [stats.mean(List) for List in hourly_activity_pattern]
        hourly_activity_stdevs = [stats.stdev(List) for List in hourly_activity_pattern]

        hourly_activity_means = hourly_activity_means[12 - time_zone_shift:] + hourly_activity_means[:12 - time_zone_shift]
        hourly_activity_stdevs = hourly_activity_stdevs[12 - time_zone_shift:] + hourly_activity_stdevs[:12 - time_zone_shift]

        ax.plot(list(range(24)), hourly_activity_means, 'o-', markersize=2, label=hyena)

    ax.legend()
    ax.set_xticks(list(range(24)))
    ax.set_xticklabels(x_axis_vals, rotation='vertical')
    ax.set_ylabel("Fraction of time in active states")
    plt.savefig(PROJECTROOT + FIGURES + "circadian_rhythms.pdf")
    plt.savefig(PROJECTROOT + FIGURES + "circadian_rhythms.png")
        

def get_stackplot_for_states_in_day():
    """
    Generates stackplots of time spent in each behavioural state as a function of time of day.
    """

    states_ordered = [LOPE, WALK, STAND, LYUP, LYING]

    time_zone_shift = 3

    x_axis_vals = list(range(12,24)) + list(range(0, 12))
    x_axis_vals = [str(x)+":00" for x in x_axis_vals]
    for i in range(len(x_axis_vals)):
        if len(x_axis_vals[i])== 4:
            x_axis_vals[i] = "0" + x_axis_vals[i]


    for hyena in HYENAS:
        fig, ax = plt.subplots()

        statewise_hourly_activity_pattern = []
        for state in states_ordered:
            statewise_hourly_activity_pattern.append([])
        for stateData in statewise_hourly_activity_pattern:
            for i in range(24):
                stateData.append([])

        TimeAndStates = [line for line in open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")][1:]
        TimeAndStates = [(dt.datetime.fromisoformat(line.split(",")[0]), line.split(",")[1].rstrip("\n"))\
                                                            for line in TimeAndStates]

        len_hour = 0
        First = True

        count_keeper = {}
        for state in states_ordered:
            count_keeper[state] = 0

        for time, state in TimeAndStates:

            if First:
                start_hour = time.hour
                First = False

            count_keeper[state] += WINDOW_DURATION
            len_hour += WINDOW_DURATION

            if time.hour != start_hour:
                for state in states_ordered:
                    state_index = states_ordered.index(state)
                    statewise_hourly_activity_pattern[state_index][(start_hour + time_zone_shift -12)%24].append(count_keeper[state]/len_hour)
                len_hour= 0
                for state in states_ordered:
                    count_keeper[state] = 0
                start_hour = time.hour

        temp_list = []
        for stateData in statewise_hourly_activity_pattern:
            stateData = [stats.mean(List) for List in stateData]
            temp_list.append(stateData)

        statewise_hourly_activity_pattern = temp_list
        ax.stackplot(list(range(24)), statewise_hourly_activity_pattern, labels=states_ordered)
        ax.legend(loc="upper left", fontsize='small')
        ax.set_xticks(list(range(24)))
        ax.set_xticklabels(x_axis_vals, rotation='vertical')
        ax.text(23, 0.9, s=hyena, va="top", ha="right")
        plt.savefig(PROJECTROOT + FIGURES + f"/{hyena}-behaviour-daily-stackplot.pdf")
        ax.cla()

def _load_daywise_times_and_states(filename, ignore_first_day=True, ignore_last_day=True):
    lines = [line.strip().split(",") for line in open(filename)][1:]
    TimeAndStates = [(dt.datetime.fromisoformat(line[0]).astimezone(tz=dt.timezone(dt.timedelta(hours=3))), line[1]) for line in lines]

    Date = TimeAndStates[0][0].date()

    time_1 = TimeAndStates[0][0] - dt.timedelta(seconds = WINDOW_DURATION)

    BIG_DICT = {Date:[]}
    for time, state in TimeAndStates:
        if time - time_1 != dt.timedelta(seconds = WINDOW_DURATION):
#            print("W:", time_1, "error encountered: time skip of", (time-time_1).total_seconds(), "s. Appending state 'UNKNOWN'.")
            for cnt in range(int((time - time_1).total_seconds()/WINDOW_DURATION) - 1):
                proposed_time = time + dt.timedelta(seconds = cnt*WINDOW_DURATION)
                BIG_DICT[proposed_time.date()].append((proposed_time, 'UNKNOWN'))
        time_1 = time
        if time.date() == Date:
            BIG_DICT[time.date()].append((time, state))
        else:
            #New day encountered
            BIG_DICT[time.date()] = []
            Date = time.date()
            BIG_DICT[time.date()].append((time, state))


    if ignore_first_day:
        BIG_DICT.pop(TimeAndStates[0][0].date())
    if ignore_last_day:
        BIG_DICT.pop(Date)
    return BIG_DICT


def _get_hourly_activity_values(list_of_time_and_states):
    """
    Takes a list of time and state pairs, usually from the dict returned by _load_daywise_states. Returns hourly activity levels.
    """
    if len(list_of_time_and_states) != 86400/WINDOW_DURATION:
        raise ValueError("list_of_time_and_states needs to be one full day of data.")

    list_of_activity_levels = [0]*24
    for time, state in list_of_time_and_states:
        if state in [WALK, LOPE]:
            var = 1
        elif state in ['UNKNOWN']:
            var = 0.5
        elif state in [STAND, LYING, LYUP]:
            var = 0
        else:
            raise ValueError(f"State {state} not recognised.")
        list_of_activity_levels[time.hour] += var*WINDOW_DURATION

    list_of_activity_levels = [act/3600 for act in list_of_activity_levels]        
    return list_of_activity_levels

def _sync_between_two_lists(list1, list2):#For hourly series of activity
    if len(list1) > len(list2):
        list1 = list1[:len(list2)]
    elif len(list2) > len(list1):
        list2 = list2[:len(list1)]

    list1, list2 = np.array(list1), np.array(list2)
    msd = (list1 - list2)**2
    return 1 - msd.sum()/len(msd)

def _sync_in_lying_states(list1, list2):
    if len(list1) > len(list2):
        list1 = list1[:len(list2)]
    elif len(list2) > len(list1):
        list2 = list2[:len(list1)]

    sync_lying = 0
    unsync_lying = 0

    for i in range(len(list1)):
        if list1[i] == list2[i] == LYING:
            sync_lying += 1
        elif ((list1[i] == LYING) or (list2[i]==LYING)) and not list1[i] == list2[i]:
            unsync_lying += 1

    return sync_lying/(sync_lying + unsync_lying)
    
# NOT USED IN PAPER
def get_sleep_debt_in_hyena_activity_patterns_pairwise(time_resolution=600):#Trial run. Don't use this. Hard to interpret.
    """
    A very roundabout way to look at activity patterns and sleep debt across individuals.
    Analysis probably doesn't make sense.
    Ignore this entire function.
    """
    fig, axs = plt.subplots(5,5, sharex=True, sharey=True)
    fig.tight_layout()
    hyena_cnt_1, hyena_cnt_2 = 0, 0
    for hyena1 in HYENAS:
        hyena_cnt_2 = 0
        hyena1_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena1}.csv")
        hyena1_hourly_activity_levels = []
        for time_state_list in list(hyena1_time_and_states.values()):
            hyena1_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))

        for hyena2 in HYENAS:
            hyena2_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena2}.csv")
            hyena2_hourly_activity_levels = []
            List_h2 = list(hyena2_time_and_states.values())
            for time_state_list in List_h2:
                hyena2_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))
                
            correlations = signal.correlate(hyena1_hourly_activity_levels, hyena2_hourly_activity_levels, mode='full')
            lags = signal.correlation_lags(len(hyena1_hourly_activity_levels), len(hyena2_hourly_activity_levels), mode='full')
            h24_index = np.where(lags==24)[0][0] #Find which index is the 24h lag stored at
            main_corr = correlations[h24_index]

            shuffled_correlations = []
            for count in range(100):
                print(f"{hyena1} - {hyena2}. N:{count}", end="\033[K\r")
                random.shuffle(List_h2)
                hyena2_hourly_activity_levels = []

                for time_state_list in List_h2:
                    hyena2_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))
                    
                correlations = signal.correlate(hyena1_hourly_activity_levels, hyena2_hourly_activity_levels, mode='full')
                lags = signal.correlation_lags(len(hyena1_hourly_activity_levels), len(hyena2_hourly_activity_levels), mode='full')
                h24_index = np.where(lags==24)[0][0] #Find which index is the 24h lag stored at

                shuffled_correlations.append(correlations[h24_index]/main_corr)
            axs[hyena_cnt_1, hyena_cnt_2].hist(shuffled_correlations)
            axs[hyena_cnt_1, hyena_cnt_2].axvline(1, color="red")
            axs[hyena_cnt_1, hyena_cnt_2].set_title(f"{hyena1} - {hyena2}", fontsize="x-small")
            
            hyena_cnt_2 += 1
            plt.savefig("temp.jpg")
        hyena_cnt_1 += 1
    plt.show()
    

def get_sync_in_hyena_activity_patterns(time_resolution=600):
    """
    Quantifies synchronisation in all dyads.
    Plots true synchronisation.
    Finds a null-hypothesis: sync-score expected just by chance, by shuffling the days of the second hyena in the dyad, 
    plots this null hypothesis too.
    Colours each dyad based on whether it is in sync.
    """

    fig, axs = plt.subplots(5,5, sharex=True, sharey=True)
    fig.tight_layout()
    hyena_cnt_1, hyena_cnt_2 = 0, 0

    considered_pairs = []
    for hyena1 in HYENAS:
        hyena_cnt_2 = 0
        hyena1_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena1}.csv")
        hyena1_hourly_activity_levels = []
        for time_state_list in list(hyena1_time_and_states.values()):
            hyena1_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))

        for hyena2 in HYENAS:
            if (hyena2, hyena1) in considered_pairs:
                axs[hyena_cnt_1, hyena_cnt_2].set_axis_off()
                hyena_cnt_2 += 1
                continue
            hyena2_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena2}.csv")
            hyena2_hourly_activity_levels = []
            List_h2 = list(hyena2_time_and_states.values())
            True_List_h2 = list(hyena2_time_and_states.values())
            for time_state_list in List_h2:
                hyena2_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))
            
            true_sync_score = _sync_between_two_lists(hyena1_hourly_activity_levels, hyena2_hourly_activity_levels)

            shuffled_syncs = []
            for count in range(100):
                print(f"{hyena1} - {hyena2}. N:{count}", end="\033[K\r")
                hyena2_hourly_activity_levels = []
                random.shuffle(List_h2)
                if List_h2 == True_List_h2:
                    random.shuffle(List_h2)

                for time_state_list in List_h2:
                    hyena2_hourly_activity_levels.extend(_get_hourly_activity_values(time_state_list))
                    
                sync_score = _sync_between_two_lists(hyena1_hourly_activity_levels, hyena2_hourly_activity_levels)

                shuffled_syncs.append(sync_score)
            shuffled_syncs = np.array(shuffled_syncs)
            axs[hyena_cnt_1, hyena_cnt_2].hist(shuffled_syncs, 20)
            axs[hyena_cnt_1, hyena_cnt_2].axvline(true_sync_score, color="red")
            axs[hyena_cnt_1, hyena_cnt_2].set_title(f"{hyena1} - {hyena2}", fontsize="x-small")

            if hyena2 == hyena1:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#b8c1d9')
            elif len(shuffled_syncs[shuffled_syncs < true_sync_score]) >= 95:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#b8d9c1')
            else:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#d9b8c1')
            
            hyena_cnt_2 += 1
            plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas.png")
            plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas.pdf")
            considered_pairs.append((hyena1, hyena2))
        hyena_cnt_1 += 1


def check_for_activity_compensation():
    """
    Generates a simple scatter plot of activity level on day i and day i+1.
    Also plots linear regressions separately for each hyena, and reports the R**2 values.
    """

    fig, ax = plt.subplots(1,1)

    for hyena in HYENAS:
        print(f"Working on activity compensation in {hyena}.")
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        daily_activity_levels = []

        for time_state_list in hyena_time_and_states.values():
            hourly_activities = _get_hourly_activity_values(time_state_list)
            total_daily_activity = sum(hourly_activities)/len(hourly_activities)
            daily_activity_levels.append(total_daily_activity)

        regression = stats.linregress(daily_activity_levels[:-1], daily_activity_levels[1:])
        scatter = ax.scatter(daily_activity_levels[:-1], daily_activity_levels[1:], label = f"{hyena} ($R^2$ = {regression.rvalue**2:.3f})")
        max_pt = max(daily_activity_levels)
        plt.draw()
        ax.axline((0, regression.intercept), (max_pt, max_pt*regression.slope + regression.intercept), color=scatter.get_facecolors()[0], lw=0.3)
        ax.set_xlabel("Active time proportion on day $i$")
        ax.set_ylabel("Active time proportion on day $i+1$")
        
    ax.legend(fontsize='small')
    fig.savefig(PROJECTROOT + FIGURES + "activity_compensation.pdf")
    fig.savefig(PROJECTROOT + FIGURES + "activity_compensation.png")

def _expand_list_of_lists(List):
    ret = []

    for element in List:
        if type(element) == list:
            ret.extend(element)
        else:
            ret.append(element)

    return ret

def get_sync_in_hyena_sleep_patterns(time_resolution=600):
    """
    Quantifies synchronisation in sleep (proportion of time in LYING state) in all dyads.
    Plots true synchronisation.
    Finds a null-hypothesis: sync-score expected just by chance, by shuffling the days of the second hyena in the dyad, 
    plots this null hypothesis too.
    Colours each dyad based on whether it is in sync.
    """

    fig, axs = plt.subplots(5,5, sharex=True, sharey=True)
    fig.tight_layout()
    hyena_cnt_1, hyena_cnt_2 = 0, 0

    considered_pairs = []
    for hyena1 in HYENAS:
        hyena_cnt_2 = 0
        hyena1_time_and_states = list(_load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena1}.csv").values())

        for hyena2 in HYENAS:
            if (hyena2, hyena1) in considered_pairs:
                axs[hyena_cnt_1, hyena_cnt_2].set_axis_off()
                hyena_cnt_2 += 1
                continue
            hyena2_time_and_states = list(_load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + f"{hyena2}.csv").values())
            hyena1_states = [state for time,state in _expand_list_of_lists(hyena1_time_and_states)]
            hyena2_states = [state for time,state in _expand_list_of_lists(hyena2_time_and_states)]
            true_sync_score = _sync_in_lying_states(hyena1_states, hyena2_states)

            shuffled_syncs = []
            for count in range(100):
                print(f"{hyena1} - {hyena2}. N:{count}", end="\033[K\r")
                hyena2_true = hyena2_time_and_states.copy()
                random.shuffle(hyena2_time_and_states)
                if hyena2_time_and_states == hyena2_true:
                    random.shuffle(hyena2_time_and_states)
                hyena2_states = [state for time,state in _expand_list_of_lists(hyena2_time_and_states)]

                sync_score = _sync_in_lying_states(hyena1_states, hyena2_states)

                shuffled_syncs.append(sync_score)
            shuffled_syncs = np.array(shuffled_syncs)
            axs[hyena_cnt_1, hyena_cnt_2].hist(shuffled_syncs, 20)
            axs[hyena_cnt_1, hyena_cnt_2].axvline(true_sync_score, color="red")
            axs[hyena_cnt_1, hyena_cnt_2].set_title(f"{hyena1} - {hyena2}", fontsize="x-small")

            if hyena2 == hyena1:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#b8c1d9')
            elif len(shuffled_syncs[shuffled_syncs < true_sync_score]) >= 95:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#b8d9c1')
            else:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#d9b8c1')
            
            hyena_cnt_2 += 1
            plt.savefig(PROJECTROOT + FIGURES + "sleep_sync_bw_hyenas.png")
            plt.savefig(PROJECTROOT + FIGURES + "sleep_sync_bw_hyenas.pdf")
            considered_pairs.append((hyena1, hyena2))
        hyena_cnt_1 += 1

def check_for_sleep_debt():
    """
    Generates a simple scatter plot of sleep (prop of time in LYING) on day i and day i+1.
    Also plots linear regressions separately for each hyena, and reports the R**2 values.
    """

    fig, ax = plt.subplots(1,1)

    for hyena in HYENAS:
        print(f"Working on sleep debt in {hyena}.")
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        daily_sleep_levels = []

        for time_state_list in hyena_time_and_states.values():
            daily_sleep_levels.append([state for time,state in time_state_list].count(LYING)/len(time_state_list))

        regression = stats.linregress(daily_sleep_levels[:-1], daily_sleep_levels[1:])
        scatter = ax.scatter(daily_sleep_levels[:-1], daily_sleep_levels[1:], label = f"{hyena} ($R^2$ = {regression.rvalue**2:.3f})")
        max_pt = max(daily_sleep_levels)
        plt.draw()
        ax.axline((0, regression.intercept), (max_pt, max_pt*regression.slope + regression.intercept), color=scatter.get_facecolors()[0], lw=0.3)
        ax.set_xlabel("Time spent in LYING on day $i$")
        ax.set_ylabel("Time spent in LYING on day $i+1$")
        
    ax.legend(fontsize='small')
    fig.savefig(PROJECTROOT + FIGURES + "sleep_debt.pdf")
    fig.savefig(PROJECTROOT + FIGURES + "sleep_debt.png")


#get_bout_duration_distributions()
#lying_to_lyup_bouts_histogram()
#generate_vedba_histograms()
#vedba_and_behaviour_correlations()
#day_vs_night_vigilance_behaviours()
#hourly_activity_patterns()
#daily_activity_patterns()
#get_circadian_rhythms()
#get_stackplot_for_states_in_day()
#get_activity_cross_correlations()
#get_sleep_debt_in_hyena_activity_patterns_pairwise()
#get_sync_in_hyena_activity_patterns()
#check_for_activity_compensation()
#get_sync_in_hyena_sleep_patterns()
#check_for_sleep_debt()

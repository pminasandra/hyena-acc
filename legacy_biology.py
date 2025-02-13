
import random
import datetime as dt
import math
import statistics
#matplotlib.use("Agg")

import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import powerlaw
from scipy import signal, stats
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import pandas as pd

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
            stateData = [statistics.mean(List) for List in stateData]
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
    Takes a list of time and state pairs, usually from the dict returned by _load_daywise_times_and_states(...). Returns hourly activity levels.
    """
    if len(list_of_time_and_states) != 86400/WINDOW_DURATION:
        raise ValueError("list_of_time_and_states needs to be one full day of data.")

    list_of_activity_levels = [0]*24
    data_count = [0]*24
    for time, state in list_of_time_and_states:
        if state in [WALK, LOPE]:
            list_of_activity_levels[time.hour] += 1*WINDOW_DURATION
            data_count[time.hour] += 1
        elif state in ['UNKNOWN']:
            pass
        elif state in [STAND, LYING, LYUP]:
            data_count[time.hour] += 1
        else:
            raise ValueError(f"State {state} not recognised.")

    for val in data_count:
        if val == 0:
            val = np.nan

    list_of_activity_levels = [list_of_activity_levels[i]/(data_count[i]*WINDOW_DURATION) for i in range(24)]        
    return list_of_activity_levels

def _sync_between_two_lists(list1, list2):#For hourly series of activity
    if len(list1) > len(list2):
        list1 = list1[:len(list2)]
    elif len(list2) > len(list1):
        list2 = list2[:len(list1)]

    list1, list2 = np.array(list1), np.array(list2)
    msd = (list1 - list2)**2
    return 1 - np.nanmean(msd)

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


def check_for_idiosyncrasies(metric="coef_of_var"):
    """
    Checks how the daily variance of activity levels within and between an individual differ across days.
    Args:
        metric (str): must be in ['var', 'std', 'coef_of_var', 'entropy']
    """

    assert metric in ['var', 'std', 'coef_of_var', 'entropy']
    
    x_axis_vals = list(range(12,24)) + list(range(0, 12))
    x_axis_vals = [str(x)+":00" for x in x_axis_vals]
    for i in range(len(x_axis_vals)):
        if len(x_axis_vals[i])== 4:
            x_axis_vals[i] = "0" + x_axis_vals[i]

    fig, ax = plt.subplots()
    ax.axvspan(6.5, 18.5, color="gray", alpha=0.5)
    #ax.set_ylim([0,4])
    summary_data_table = []

    if metric == "var":
        def metric(array):
            return array.var(axis=0)
    elif metric == "std":
        def metric(array):
            return array.std(axis=0)
    elif metric == "entropy":
        from scipy.stats import entropy
        def metric(array):
            return entropy(array, axis=0, nan_policy='omit')
    else:
        from scipy.stats import variation
        def metric(array):
            return variation(array, axis=0, nan_policy='omit')

    for hyena in HYENAS:
        print("check_for_idiosyncrasies: working on", hyena)
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        data_table = []

        for day in hyena_time_and_states:
            data_table.append(_get_hourly_activity_values(hyena_time_and_states[day]))

        data_table = np.array(data_table)
        data_table = data_table * (1 - data_table)
        summary_data_table.append(data_table.copy())

        mets = np.array(metric(data_table))
        mets_plot = np.array([])
        mets_plot = np.append(mets_plot, mets[12:]) 
        mets_plot = np.append(mets_plot, mets[:12])
        ax.plot(x_axis_vals, mets_plot, "o-", linewidth=1, label=hyena)


    mets = list(metric(np.concatenate(summary_data_table)))
    mets_plot = mets[12:] + mets[:12]
    ax.set_xticklabels(x_axis_vals, rotation='vertical')
    ax.plot(x_axis_vals, mets_plot, "o-", linewidth=2, color='black', label='All data')
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Coefficient of variation")
    ax.legend()

    fig.savefig(PROJECTROOT + FIGURES + "individual_idiosyncrasies.png")
    fig.savefig(PROJECTROOT + FIGURES + "individual_idiosyncrasies.pdf")
        
def check_for_individual_activity_pattern_similarity_umap():
    """
    Uses u-MAP (https://arxiv.org/pdf/1802.03426.pdf) to cluster 24-dimensional data representing entire days,
    and colours them by hyena ID. We expect that individual hyenas have more similar days.
    """

    import umap

    data_all = []
    for hyena in HYENAS:
        print("check_for_individual_activity_pattern_similarity_umap: working on", hyena)
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        data_table = []

        for day in hyena_time_and_states:
            data_table.append(_get_hourly_activity_values(hyena_time_and_states[day]))

        data_table = pd.DataFrame(data_table, columns=range(0,24))
        data_table['id'] = hyena 

        data_all.append(data_table)

    data_all = pd.concat(data_all)

    reducer = umap.UMAP()
    scaled_data = StandardScaler().fit_transform(data_all[range(0,24)])
    embedding = reducer.fit_transform(scaled_data)

    fig, axs = plt.subplots(1,2)
    axs[0].scatter(embedding[:,0], embedding[:,1], c=[sns.color_palette()[x] for x in data_all['id'].map({
    "WRTH":0,
    "BORA":1,
    "BYTE":2,
    "MGTA":3,
    "FAY":4
    })])
    axs[0].set_title("uMAP reduced data, coloured by individual")

    axs[1].scatter(embedding[:,0], embedding[:,1], c=data_all.index)
    axs[1].set_title("uMAP reduced data, coloured by date")
    plt.show()


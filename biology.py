import random
import datetime as dt
import numpy as np
import matplotlib
import math
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import powerlaw

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

#get_bout_duration_distributions()
#lying_to_lyup_bouts_histogram()
vedba_and_behaviour_correlations()

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

    plt.style.use('tableau-colorblind10')
    plt.bar(LEVELS, LYING_VEDBAS, 0.35, label=LYING)
    plt.bar(LEVELS, LYUP_VEDBAS, 0.35, label=LYUP, bottom=LYING_VEDBAS)
    plt.bar(LEVELS, STAND_VEDBAS, 0.35, label=STAND, bottom=LYING_VEDBAS + LYUP_VEDBAS)
    plt.bar(LEVELS, WALK_VEDBAS, 0.35, label=WALK, bottom = LYING_VEDBAS + LYUP_VEDBAS + STAND_VEDBAS)
    plt.bar(LEVELS, LOPE_VEDBAS, 0.35, label=LOPE, bottom = LYING_VEDBAS + LYUP_VEDBAS + WALK_VEDBAS + STAND_VEDBAS)

    plt.xlabel("VeDBA levels")
    plt.ylabel("Proportion of time in each behavioural state")
    plt.ylim(0,1.1)
    plt.legend(loc=(0.6, 0.5))

    plt.savefig(PROJECTROOT + FIGURES + "States_and_VeDBAs.png")
    plt.savefig(PROJECTROOT + FIGURES + "States_and_VeDBAs.pdf")


def _isDay(time):

    if 6 <= time.hour < 18:
        return True
    else:
        return False

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
    plt.style.use('tableau-colorblind10')
    fig, ax = plt.subplots()

    ax.axvspan(6.66, 18.8344, color="#bebebe") #6:40 to 18:50 approximately (night)
    ax.axvspan(5.33, 6.66, color="#dedede") #5:20 to 6:40 approximately (twilight)
    ax.axvspan(18.8344, 20.0833, color="#dedede") #6:40 to 18:50 approximately (twilight)


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


        hourly_activity_means = [statistics.mean(List) for List in hourly_activity_pattern]
        hourly_activity_stdevs = [statistics.stdev(List) for List in hourly_activity_pattern]

        hourly_activity_means = hourly_activity_means[12 - time_zone_shift:] + hourly_activity_means[:12 - time_zone_shift]
        hourly_activity_stdevs = hourly_activity_stdevs[12 - time_zone_shift:] + hourly_activity_stdevs[:12 - time_zone_shift]

        ax.plot(list(range(24)), hourly_activity_means, 'o-', markersize=2, label=hyena)

    ax.legend()
    ax.set_xticks(list(range(24)))
    ax.set_xticklabels(x_axis_vals, rotation='vertical')
    ax.set_ylabel("Fraction of time in active states")
    plt.savefig(PROJECTROOT + FIGURES + "circadian_rhythms.pdf")
    plt.savefig(PROJECTROOT + FIGURES + "circadian_rhythms.png")
        

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


def get_sync_in_hyena_activity_patterns(time_resolution=600):
    """
    Quantifies synchronisation in all dyads.
    Plots true synchronisation.
    Finds a null-hypothesis: sync-score expected just by chance, by shuffling the days of the second hyena in the dyad, 
    plots this null hypothesis too.
    Colours each dyad based on whether it is in sync.
    """

    fig, axs = plt.subplots(5,5, sharex=True, sharey=True, figsize=(4.8, 4.795))    
    for i in range(5):
        for j in range(5):
            ax = axs[i, j]
            ax.set_box_aspect(1.0)
            if (i, j) != (0, 0) and (i, j) != (4, 4):
                plt.setp(ax, xticks=[], yticks=[])
                ax.tick_params(axis=u'both', which=u'both',length=0)
            else:
                if (i, j) == (0, 0):
                    plt.setp(ax, xticks=[], yticks=[0, 10])
                    ax.set_yticks([0, 10])
                if (i, j) == (4, 4):
                    plt.setp(ax, xticks=[0.95, 1.0], yticks=[])

    fig.subplots_adjust(wspace=0, hspace=0, left=0.1, right=1-0.025, top=1-0.05, bottom=0.05)
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
                axs[hyena_cnt_1, hyena_cnt_2].spines['top'].set_visible(False)
                axs[hyena_cnt_1, hyena_cnt_2].spines['right'].set_visible(False)
                axs[hyena_cnt_1, hyena_cnt_2].spines['bottom'].set_visible(False)
                axs[hyena_cnt_1, hyena_cnt_2].spines['left'].set_visible(False)
                if hyena_cnt_2 == 0:
                    axs[hyena_cnt_1, hyena_cnt_2].set_ylabel(hyena1)
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
            #axs[hyena_cnt_1, hyena_cnt_2].set_title(f"{hyena1} - {hyena2}", fontsize="x-small")
            if hyena_cnt_1 == 0:
                axs[hyena_cnt_1, hyena_cnt_2].set_title(hyena2)
            if hyena_cnt_2 == 0:
                axs[hyena_cnt_1, hyena_cnt_2].set_ylabel(hyena1)
                if hyena_cnt_2 == hyena_cnt_1:
                    axs[hyena_cnt_1, hyena_cnt_2].set_yticks([0, 10])

            if hyena2 == hyena1:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#bfbfbf')
            elif len(shuffled_syncs[shuffled_syncs < true_sync_score]) >= 95:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#b8d9c1')
            else:
                axs[hyena_cnt_1, hyena_cnt_2].set_facecolor('#c1b8d9')
            
            hyena_cnt_2 += 1
            plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas.png")
            plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas.pdf")
            considered_pairs.append((hyena1, hyena2))
        hyena_cnt_1 += 1
    #axs[0, 0].set_yticklabels([0, 10])
    #axs[4, 4].set_xticklabels([0.9, 1.0])
    plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas_laststep.png")
    plt.savefig(PROJECTROOT + FIGURES + "sync_bw_hyenas_laststep.pdf")
    plt.show()


def check_for_activity_compensation():
    """
    Generates a simple scatter plot of activity level on day i and day i+1.
    Also plots linear regressions separately for each hyena, and reports the R**2 values.
    """

    plt.style.use('tableau-colorblind10')
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


def check_for_individual_activity_pattern_similarity_permutation_test(permutation_test=True, ttest=False):
    """
    Using a permutation test, plots the distribution of inter-individual distances.
    Args:
        permutation_test (bool): whether to perform a permutation test
        ttest (bool): whether to perform a t-test to compare between and across individuals
    """
    from scipy.spatial.distance import cdist
    from scipy.stats import ttest_ind

    plt.rcParams.update({"font.size": 15})

    def compute_distances(matrix1, matrix2):
        distances = cdist(matrix1, matrix2)
        if np.array_equal(matrix1, matrix2):
            distances = np.tril(distances, k=-1)
        else:
            distances[np.diag_indices(min(distances.shape[0], distances.shape[1]))] = 0.0

        return distances[distances > 0].ravel()

    def compute_within_ind_distances(list_of_tables):
        within_ind_distances = []
        for table in list_of_tables:
            within_ind_dist = compute_distances(table, table)
            within_ind_distances.extend(within_ind_dist)

        return np.array(within_ind_distances)

    def compute_across_ind_distances(list_of_tables):
        across_ind_distances = []
        count = 1
        for table in list_of_tables:
            if count == len(list_of_tables):
                return np.array(across_ind_distances)
            list_of_tables_2 = list_of_tables.copy()[count:]

            for table2 in list_of_tables_2:
                across_ind_distances.extend(compute_distances(table, table2))

            count += 1

    data_all = []
    for hyena in HYENAS:
        print("check_for_individual_activity_pattern_similarity_permutation_test: working on", hyena)
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        data_table = []

        for day in hyena_time_and_states:
            data_table.append(_get_hourly_activity_values(hyena_time_and_states[day]))

        data_table = np.array(data_table)
        data_all.append(data_table)

    within_ind_distances = compute_within_ind_distances(data_all)
    across_ind_distances = compute_across_ind_distances(data_all)

    fig, ax = plt.subplots(layout='tight')
    across_hist = ax.hist(across_ind_distances, 200, label="across pairs of hyenas", color="blue", alpha=0.6)
    within_hist = ax.hist(within_ind_distances, 200, label="within individual hyenas", color="red", alpha=0.6)

    ax.axvline(np.array(across_ind_distances).mean(), color="dodgerblue")
    ax.axvline(np.array(within_ind_distances).mean(), color="indianred")
    true_test_stat = np.array(across_ind_distances).mean() - np.array(within_ind_distances).mean()

    ax.legend()
    ax.set_xlabel("Variability in daily activity patterns")
    ax.set_ylabel("Frequency")

    if ttest:
        t, p = ttest_ind(within_ind_distances, across_ind_distances, equal_var=False)

        ax.text(0.5, 150, r"$t$-statistic = "+f"{t:.3f}")
        ax.text(0.5, 125, r"$p$-value = "+f"{p:.3f}")

    if permutation_test:
        NUM_PERMUTATIONS = 5000
        hyena_lengths = [len(x) for x in data_all]
        pool_of_days = np.concatenate(data_all)
        list_of_stats = []

        for i in range(NUM_PERMUTATIONS):
            pseudo_data_table = []
            ids = list(range(sum(hyena_lengths)))
            # First create pseudo-hyenas and populate them with a random set of days
            count = 0
            for l in hyena_lengths:
                pseudo_data_table.append([])
                id_l = random.sample(ids, l)
                id_l.sort()
                pseudo_data_table[count] = pool_of_days[id_l, :]

                for k in id_l:
                    ids.remove(k)

                count += 1

            # Then compute the test-statistic each time
            test_stat = compute_across_ind_distances(pseudo_data_table).mean() - compute_within_ind_distances(pseudo_data_table).mean()
            list_of_stats.append(test_stat)

        fig2, ax2 = plt.subplots(layout='tight')
        ax2.hist(list_of_stats, 200, label="Null distribution from permutations")
        ax2.axvline(true_test_stat, linestyle='dotted', color='black', label="Estimated value")
        ax2.set_xlabel('Individuality statistic')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        fig2.savefig(PROJECTROOT + FIGURES + "individuality_significance.png")
        fig2.savefig(PROJECTROOT + FIGURES + "individuality_significance.pdf")

        list_of_stats = np.array(list_of_stats)
        p = len(list_of_stats[list_of_stats >= true_test_stat])/NUM_PERMUTATIONS

        if p > 0.0:
            ax.text(0.5, 125, r"$p$-value = "+f"{p:.3f}")
        else:
            ax.text(0.5, 125, r"$p$-value < "+"$\\frac{1}{" + str(NUM_PERMUTATIONS) + "}$")

    fig.savefig(PROJECTROOT + FIGURES + "permutation_model.png")
    fig.savefig(PROJECTROOT + FIGURES + "permutation_model.pdf")

# Following functions contain analyses addressing reviewer comments
def individuality_through_variances():

    import random
    import matplotlib.colors as mcolors

    PERM_COUNT = 5000

    fig, ax = plt.subplots(tight_layout=True)
    colors = list(mcolors.TABLEAU_COLORS.values())

    data_all = []
    days_all = []
    for hyena in HYENAS:
        print("individuality_through_variances: loading data for", hyena)
        hyena_time_and_states = _load_daywise_times_and_states(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        data_table = []

        for day in hyena_time_and_states:
            data_table.append(_get_hourly_activity_values(hyena_time_and_states[day]))
            days_all.append(_get_hourly_activity_values(hyena_time_and_states[day]))

        data_table = np.array(data_table)
        data_all.append(data_table)

    def _normalise_activity_curve(dt):
        means = dt.mean(axis=0)
        dt2 = dt - means
        return dt2

    def _d2d_variation(dt):
        vars_ = dt.var(axis=0)
        total_var = vars_.sum()
        return total_var

    def _make_permutations(all_day_dat, n, count=PERM_COUNT):
        for i in range(count):
            days = random.sample(all_day_dat, n)
            yield np.array(days)

    hyena_cnt = 0
    for hyena in HYENAS:
        print("individuality_through_variances: processing", hyena)
        hyena_data = _normalise_activity_curve(data_all[hyena_cnt])
        hyena_var = _d2d_variation(hyena_data)
        hyena_num_days = hyena_data.shape[0]

        permuted_d2d_vars = []
        for perm in _make_permutations(days_all, hyena_num_days, PERM_COUNT):
            permuted_d2d_vars.append(_d2d_variation(perm))

        permuted_d2d_vars = np.array(permuted_d2d_vars)
        ax.hist(permuted_d2d_vars, 100, color=colors[hyena_cnt], alpha=0.6)
        ax.axvline(hyena_var, color=colors[hyena_cnt], label=hyena)
        ax.legend()
        ax.set_xlabel("Average total variability")
        ax.set_ylabel("Frequency")
        effect_size = permuted_d2d_vars.mean() - hyena_var
        p_val = (permuted_d2d_vars <= hyena_var).sum()/PERM_COUNT
        print(hyena, "alternate individuality score is:", effect_size, "p=", p_val)
        hyena_cnt += 1

    fig.savefig(PROJECTROOT + FIGURES + "alternate_individuality_score.png")
    fig.savefig(PROJECTROOT + FIGURES + "alternate_individuality_score.pdf")
#generate_vedba_histograms() #FIG 1
# Figure 2 is from analyses.py
#vedba_and_behaviour_correlations() #FIG 3
#get_circadian_rhythms() #FIG 4
#check_for_activity_compensation() #FIG 5
#check_for_individual_activity_pattern_similarity_permutation_test() # FIG 6
#get_sync_in_hyena_activity_patterns() #FIG 7a
# Figure 7b, Figure D1 are in gps.py
individuality_through_variances()

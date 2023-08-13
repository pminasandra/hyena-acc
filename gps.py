from config import *
from variables import *

import h5py
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

###
# CONFIG
proximity_threshold = 200
#
###

num_hyena_dict = {0:'WRTH', 1:'BORA', 2:'BYTE', 3:'MGTA', 4:'FAY'}
TargetDir = PROJECTROOT + DATA + "GPS_Data/"

def generate_csv_datasets():
    """
    Generates useful separate csv files with UTM locations for hyenas.
    This provides an advantage over the more difficult hdf5 file.
    """

    h5_open = h5py.File(TargetDir + "hyena_xy_level1.h5", "r")
    print("generate_csv_datasets: hdf5 file succesfully opened. Proceeding to initiate timestamp generation.")
    timestamps = np.array(h5_open['timestamps'])
    dt_get = lambda dtm: dt.datetime.fromisoformat(dtm.decode())
    dt_get = np.vectorize(dt_get)
    timestamps = dt_get(timestamps)
    print("generate_csv_datasets: timestamps generated.")

    for i in range(5):
        print(f"generate_csv_datasets: generating csv file for GPS data from {num_hyena_dict[i]}")
        xs = h5_open['xs'][:,i]
        ys = h5_open['ys'][:,i]

        dataframe = pd.DataFrame(np.array([timestamps, xs, ys]).T, columns=('timestamps', 'x', 'y'))
        dataframe.to_csv(TargetDir + num_hyena_dict[i] +"_GPS.csv", index = False, na_rep="nan")


def compute_proximity_network(proximity_threshold=proximity_threshold):
    """
    Generates a social network based on proximity among individuals.
    """

    proximity_network_matrix = np.zeros((5,5))

    for i in range(5):
        first_hyena_data = pd.read_csv(TargetDir + num_hyena_dict[i] + "_GPS.csv", header=0)
        first_hyena_data = np.array(first_hyena_data[['x', 'y']])

        for j in range(5):
            if j < i:
                proximity_network_matrix[i,j] = np.nan
                continue
            elif j == i:
                proximity_network_matrix[i,j] = -0.0001
                continue
            print(f"compute_proximity_network: now working on {num_hyena_dict[i]} -- {num_hyena_dict[j]}")
            second_hyena_data = pd.read_csv(TargetDir + num_hyena_dict[j] + "_GPS.csv", header=0)
            second_hyena_data = np.array(second_hyena_data[['x', 'y']]).T

            distances = []
            for count in range(len(first_hyena_data)):
                dist = sum((first_hyena_data[count,:] - second_hyena_data[:,count])**2)**0.5

                distances.append(dist)

            distances = np.array(distances)
            available_data = sum(~np.isnan(distances))/len(distances)
            distances_wo_nan = distances[~np.isnan(distances)]
            proximity_metric = sum(distances_wo_nan < proximity_threshold)/len(distances_wo_nan)

            proximity_network_matrix[i,j] = proximity_metric

    #proximity_network_matrix = proximity_network_matrix[:-1,:]
    positive_cmap = cm.get_cmap('viridis').copy()
    from matplotlib.colors import LinearSegmentedColormap
    negative_cmap = LinearSegmentedColormap.from_list('NegativeColorMap', ['gray', 'gray'])
    cmap = plt.cm.colors.ListedColormap(['gray'] + [positive_cmap(i) for i in np.linspace(0,1,256)])
    cmap.set_bad('w')
    fig, ax = plt.subplots(1,1)
    im = ax.imshow(proximity_network_matrix, cmap=cmap, vmin=0.0, vmax=0.4) # vmin and vmax fixed for the paper
    fig.colorbar(im)
    ticklabels = list(TAG_LOOKUP.keys())
    ax.set_yticklabels(ticklabels, rotation=90)
    ax.set_yticks(range(5))
    ax.xaxis.tick_top()
    ax.set_xticks(range(5))
    ax.set_xticklabels(ticklabels)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.tick_params(axis=u'both', which=u'both',length=0)
    fig.tight_layout()
    fig.savefig(PROJECTROOT + FIGURES + f"ProximityNetwork_{proximity_threshold}.pdf")
    fig.savefig(PROJECTROOT + FIGURES + f"ProximityNetwork_{proximity_threshold}.png")

#generate_csv_datasets()
compute_proximity_network(proximity_threshold = 50)
compute_proximity_network(proximity_threshold = 100)
compute_proximity_network(proximity_threshold = 200)
compute_proximity_network(proximity_threshold = 300)
compute_proximity_network(proximity_threshold = 500)

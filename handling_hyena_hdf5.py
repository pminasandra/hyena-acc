###     This code helps easily extract relevant metadata from the hyena hdf5 files

import h5py
import datetime as dt
from variables import *

def hdf5_ListsOfVariables(hdf5_file_path):
        """
        Extracts data from hdf5 file.
        USE CAREFULLY. MIGHT EAT UP RAM.

        Args:
                hdf5_file_path (str): /path/to/hdf5/file.h5. Typically the output of hdf5_file_path .

        Returns:
                (list): List of numpy arrays containing all data from hdf5 file.
        """
        openfile = h5py.File(hdf5_file_path, "r")
        surge, sway, heave, vedba, UTC, freq = openfile['A'][0],\
                                                openfile['A'][1],\
                                                openfile['A'][2],\
                                                openfile['vedba'][0],\
                                                dt.datetime(*[int(x[0]) for x in openfile['UTC']]),\
                                                openfile['fs'][0][0]
        del openfile
        return [surge, sway, heave, vedba, UTC, freq]

def hdf5_file_path(hyena_name, freq):
        """
        Easy way to obtain /path/to/hdf5/files

        Args:
                hyena_name (str): for now from WRTH, BORA, BYTE, MGTA, FAE
                freq (int): frequency of accelerometer data in hertz.

        Returns:
                (str): /path/to/hdf5/file.h5
        """
        return HDD_MNT_PNT +D_hdf5 +TAG_LOOKUP[hyena_name]+ "_A_" + str(freq) + "Hz.h5"

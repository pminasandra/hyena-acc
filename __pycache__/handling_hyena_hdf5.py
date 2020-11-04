# uncompyle6 version 3.7.4
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.5 (default, Jul 28 2020, 12:59:40) 
# [GCC 9.3.0]
# Embedded file name: /media/pranav/Data1/Personal/Projects/Strandburg-Peshkin 2019-20/code/handling_hyena_hdf5.py
# Compiled at: 2019-07-31 12:19:05
# Size of source mod 2**32: 1898 bytes
import h5py, datetime as dt
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
    openfile = h5py.File(hdf5_file_path, 'r')
    surge, sway, heave, vedba, UTC, freq = (openfile['A'][0],
     openfile['A'][1],
     openfile['A'][2],
     openfile['vedba'][0],
     dt.datetime(openfile['UTC'][0], openfile['UTC'][1], openfile['UTC'][2], openfile['UTC'][3], openfile['UTC'][4], openfile['UTC'][5]),
     openfile['fs'][0][0])
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
    return HDD_MNT_PNT + D_hdf5 + TAG_LOOKUP[hyena_name] + '_A_' + str(freq) + 'Hz.h5'
# okay decompiling handling_hyena_hdf5.cpython-38.pyc

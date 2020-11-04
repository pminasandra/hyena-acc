# uncompyle6 version 3.7.4
# Python bytecode 3.5 (3350)
# Decompiled from: Python 3.8.5 (default, Jul 28 2020, 12:59:40) 
# [GCC 9.3.0]
# Embedded file name: /media/pranav/Data1/Personal/Projects/Strandburg-Peshkin 2019-20/code/crawler.py
# Compiled at: 2020-01-26 18:03:44
# Size of source mod 2**32: 6478 bytes
import os, h5py
from variables import *
from handling_hyena_hdf5 import *
import datetime as dt, numpy as np
from errors import *

class crawler:
    __doc__ = '\n        Class crawler, a way to read an n second interval and update fast.\n        Please construct all future feature extraction and classification functions with this object as an argument.\n\n        Attributes:\n                surge   (numpy array):|\n                sway    (numpy array):|__       contains respective accelerometer data over the time spanned by the crawler.\n                heave   (numpy array):|\n                vedba   (numpy array):|\n                \n        '

    def __init__(self, ListOfLists, initialise_time, window_duration):
        """
                Class crawler init function

                Args:
                        ListOfLists (list): A List containing numpy arrays from an hdf5 file. Output of hdf5_ListsOfVariables from handling_hyena_hdf5.py
                        initialise_time (datetime.datetime): What time point should the crawler begin at.
                        window_duration (int or float): How large a duration should the crawler occupy (in seconds).

                Returns: 
                        None

                Raises:
                        TimeQueryError
                        CrawlerEncounteredNANsError
                """
        self._window_duration = window_duration
        self.ListOfLists = ListOfLists
        self._frequency = self.ListOfLists[5]
        self.datalogger_start_time = self.ListOfLists[4]
        if initialise_time < self.datalogger_start_time or initialise_time + dt.timedelta(seconds=self._window_duration) > self.datalogger_start_time + dt.timedelta(seconds=len(self.ListOfLists[0]) / self._frequency):
            raise TimeQueryError('Crawler received unacceptable initialise_time.')
        self.num_points_considered = int(window_duration * self._frequency)
        self.init_point = int((initialise_time - self.datalogger_start_time).total_seconds() * self._frequency)
        self.endpoint = self.init_point + int(window_duration * self._frequency)
        self.surge, self.sway, self.heave, self.vedba = (self.ListOfLists[0][self.init_point:self.init_point + self.num_points_considered],
         self.ListOfLists[1][self.init_point:self.init_point + self.num_points_considered],
         self.ListOfLists[2][self.init_point:self.init_point + self.num_points_considered],
         self.ListOfLists[3][self.init_point:self.init_point + self.num_points_considered])
        try:
            self.validate()
        except CrawlerEncounteredNANsError:
            self.surge = self.surge[(~np.isnan(self.surge))]
            self.heave = self.heave[(~np.isnan(self.heave))]
            self.sway = self.sway[(~np.isnan(self.sway))]
            self.vedba = self.vedba[(~np.isnan(self.vedba))]

    def validate(self):
        """
                Validates current situation of crawler, and raises errors if necessary.
                """
        if sum(np.isnan(self.surge)) > 0:
            raise CrawlerEncounteredNANsError('Surge has NaNs!')
        else:
            if sum(np.isnan(self.heave)) > 0:
                raise CrawlerEncounteredNANsError('Heave has NaNs!')
            else:
                if sum(np.isnan(self.sway)) > 0:
                    raise CrawlerEncounteredNANsError('Sway has NaNs!')
                elif sum(np.isnan(self.vedba)) > 0:
                    raise CrawlerEncounteredNANsError('VeDBA has NaNs!')

    def update(self, duration):
        """
                Updates time window occupied by crawler (move crawler forward or backward through time)

                Args:
                        duration (int or float): How much to move the crawler. Negative numbers are supported.

                Returns:
                        None

                Raises:
                        TimeQueryError
                        CrawlerEncounteredNANsError
                """
        if self.init_point / self._frequency + duration < 0 or self.endpoint / self._frequency + duration > len(self.ListOfLists[0]):
            raise TimeQueryError('Crawler updated to unacceptable time.')
        self.surge, self.sway, self.heave, self.vedba = (self.surge[int(duration * self._frequency):],
         self.sway[int(duration * self._frequency):],
         self.heave[int(duration * self._frequency):],
         self.vedba[int(duration * self._frequency):])
        self.init_point += int(duration * self._frequency)
        self.surge = np.append(self.surge, self.ListOfLists[0][self.endpoint:self.endpoint + int(duration * self._frequency)])
        self.sway = np.append(self.sway, self.ListOfLists[1][self.endpoint:self.endpoint + int(duration * self._frequency)])
        self.heave = np.append(self.heave, self.ListOfLists[2][self.endpoint:self.endpoint + int(duration * self._frequency)])
        self.vedba = np.append(self.vedba, self.ListOfLists[3][self.endpoint:self.endpoint + int(duration * self._frequency)])
        self.endpoint += int(duration * self._frequency)

    def __repr__(self):
        return '<crawler object of {} seconds currently spanning {} to {}>'.format(self._window_duration, self.datalogger_start_time + dt.timedelta(seconds=self.init_point / self._frequency), self.datalogger_start_time + dt.timedelta(seconds=self.endpoint / self._frequency))

    def __str__(self):
        return self.__repr__()
# okay decompiling crawler.cpython-35.pyc

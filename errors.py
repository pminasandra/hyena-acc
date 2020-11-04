""" 
This file contains a bunch of errors frequently encountered throughout this project.
"""

###########################################################################################################################################################

class HyenaProjectException(Exception):
        """
        Base error on which all others in this file are based.
        """
        def __init__(self, message=None):
                self.message = message
        def __str__(self):
                if self.message == None:
                        return ""
                else:
                        return repr(message)

###########################################################################################################################################################

class TimeQueryError(HyenaProjectException):
        """
        A query is made for time prior to beginning of accelerometer data recording, or after accelerometer data recording has ended.
        """

class CrawlerEncounteredNANsError(HyenaProjectException):
        """
        Crawler fields contain NaNs.
        """

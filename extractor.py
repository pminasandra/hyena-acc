### This file will eventually be converted to main.py, where the feature extraction, and eventually classification will happen.
### Eventually will be standalone code.

import features
import types
import os
import datetime as dt
from inspect import getmembers
from variables import *
from crawler import crawler
from handling_hyena_hdf5 import *
from read_audits import *
from config import *
import datetime as dt

####################################################################################################################################################
### PRELIM SETUP
old_print = print
def print(x, *args, **kwargs):
        old_print(x, *args, **kwargs, flush=True)

####################################################################################################################################################

### Will now get list containing all non-internal functions in features.py

list_of_feature_functions = [f[1] for f in getmembers(features) if type(f[1]) == types.FunctionType and f[1].__name__[0] != "_"] #Last statement excludes both built-ins and internals

print("\033[1;32mFollowing features will be extracted:\033[0;39m")
for f in list_of_feature_functions:
        print("\t- ", f.__name__)

### Will get list of all audits
print("")
AllAudits = os.listdir(DROPBOXROOT + AUDITS)
AllAudits.remove('.dropbox')
AllAudits = [name[0:9] for name in AllAudits]

print("\033[1;32mAudits are available for the following hyenas:\033[1;33m")
for hyena in AllAudits:
        print("\t-", IND_LOOKUP[hyena])
print("")

print("\033[1;32mSHOWING ALL DATA TO BE ANALYSED:\n\033[0;39m")
for hyena in AllAudits:
        print("\033[1;33m", IND_LOOKUP[hyena], "\n___\033[0;39m", sep="")
        LoadedAuditFile = load_audit_file(DROPBOXROOT +AUDITS +hyena +'behaud.txt')
        SOAs, EOAs = indices_of_audit_starts_and_ends(LoadedAuditFile)
        
        print("{} audits are available".format(len(SOAs)))
        
        if len(SOAs) == 1:
                print("AUDIT 1:\t", str(dt.timedelta(seconds=LoadedAuditFile[EOAs[0]][0] - LoadedAuditFile[SOAs[0]][0]).total_seconds()).split()[0].split('.')[0])

        if len(SOAs) > 1:
                total_timed = dt.timedelta(seconds=0)
                i = 1
                for i in range(len(SOAs)):
                        total_timed += dt.timedelta(seconds = LoadedAuditFile[EOAs[i]][0] - LoadedAuditFile[SOAs[i]][0])
                        print("AUDIT {}:\t".format(i+1), str(dt.timedelta(seconds=LoadedAuditFile[EOAs[i]][0] - LoadedAuditFile[SOAs[i]][0])).split()[0].split('.')[0])
                        i += 1
                print("TOTAL:\t\t {} ".format(str(total_timed).split()[0].split('.')[0]))
        print("")

#######################
# EXTRA  FEATURES  HERE
#######################
#       TODO Read extra features not in features.py from here
#       TODO Implement this functionality in this thing
#######################

print("\033[1;32mBEGINNING FEATURE EXTRACTION:\n\033[0;39m")
for hyena in AllAudits:
        hyena_LoLs = hdf5_ListsOfVariables(HDD_MNT_PNT+D_hdf5+hyena+"_A_25hz.h5")
        hyena_start_time = hyena_LoLs[4]
        LoadedAuditFile = load_audit_file(DROPBOXROOT +AUDITS +hyena +'behaud.txt')
        SOAs, EOAs = indices_of_audit_starts_and_ends(LoadedAuditFile)
        AuditIndices = list(zip(SOAs, EOAs))  ## Each element in this list is start and end **INDEX in LoadedAuditFile** of each audit

        Num_Audit = 1
        for audit in AuditIndices:
                csvfile = open(PROJECTROOT+DATA+"ExtractedFeatures/"+IND_LOOKUP[hyena]+"_AUD_"+str(Num_Audit)+".csv", "w")
                csvfile.write("time,state,")
                for func in list_of_feature_functions:
                        csvfile.write(func.__name__)
                        csvfile.write(",") 
                csvfile.write("\n")
                CurrData = LoadedAuditFile[audit[0]:audit[1]] #Excludes the last "EOA" line
                
                CrawlerPlans = [[], [], []] ### CrawlerPlans is a list of 3 lists, 1) Start times for crawler, 2) Number of crawler updates, 3) State of hyena
                for line in CurrData:
                        if line[2]in STATES:
                                print("{} was in state \033[0;33m{}\033[0;39m for duration {} seconds. ".format(IND_LOOKUP[hyena], line[2], line[1]))
                                num_crawler_updates = line[1]//WINDOW_DURATION
                                if (line[1]%WINDOW_DURATION)/WINDOW_DURATION > CRAWLER_OVERHANG_TOLERANCE:
                                        num_crawler_updates += 1
                                CrawlerPlans[0].append(hyena_start_time + dt.timedelta(seconds=line[0]))
                                CrawlerPlans[1].append(int(num_crawler_updates))
                                CrawlerPlans[2].append(line[2])
                
                Num_Audit += 1
                print("\033[1;32mInitialising crawler for above data at\033[0;39m", dt.datetime.now())
                for run in enumerate(CrawlerPlans[0]):
                        Crawler = crawler(hyena_LoLs, CrawlerPlans[0][run[0]], WINDOW_DURATION)
                        for i in range(CrawlerPlans[1][run[0]]):
                                csvfile.write(str(hyena_start_time + dt.timedelta(seconds = Crawler.init_point/Crawler._frequency))+",")
                                csvfile.write(str(CrawlerPlans[2][run[0]])+",")
                                for func in list_of_feature_functions:
                                        csvfile.write(str(func(Crawler))+",")
                                csvfile.write("\n")
                                Crawler.update(CRAWLER_UPDATE_DURATION)
                print("\033[1;32mCrawler run complete at\033[0;39m", dt.datetime.now())
                csvfile.close()
                del CrawlerPlans
                del CurrData
                del Crawler
        del hyena_LoLs
        del LoadedAuditFile
        del SOAs
        del EOAs

####################################################################################################################################################
###     CLEANUP
####################################################################################################################################################

all_audit_extractions = [x for x in os.listdir(PROJECTROOT + DATA + "ExtractedFeatures/") if x[-4:]==".csv"]
print(all_audit_extractions)

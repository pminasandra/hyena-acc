###     This file is to contain ALL feature extraction code
###     Write carefully. Ensure that every actual feature function takes a crawler object as an argument.

########################################        BASIC  FUNCTIONS        ###################################################################################
import numpy as np

def _avg(List):
        return sum(List)/len(List)

def _var(List):
        AVG = _avg(List)
        VAR = 0
        for x in List:
                VAR += (x-AVG)**2
        return VAR/(len(List)-1)

########################################        FEATURE  FUNCTIONS        ##################################################################################

def surge_mean(crawler_obj):
        return _avg(crawler_obj.surge[~np.isnan(crawler_obj.surge)])

def surge_var(crawler_obj):
        return _var(crawler_obj.surge[~np.isnan(crawler_obj.surge)])

def surge_max(crawler_obj):
        return max(crawler_obj.surge[~np.isnan(crawler_obj.surge)])

def surge_min(crawler_obj):
        return min(crawler_obj.surge[~np.isnan(crawler_obj.surge)])

def heave_mean(crawler_obj):
        return _avg(crawler_obj.heave[~np.isnan(crawler_obj.heave)])

def heave_var(crawler_obj):
        return _var(crawler_obj.heave[~np.isnan(crawler_obj.heave)])

def heave_max(crawler_obj):
        return max(crawler_obj.heave[~np.isnan(crawler_obj.heave)])

def heave_min(crawler_obj):
        return min(crawler_obj.heave[~np.isnan(crawler_obj.heave)])

def sway_mean(crawler_obj):
        return _avg(crawler_obj.sway[~np.isnan(crawler_obj.sway)])

def sway_var(crawler_obj):
        return _var(crawler_obj.sway[~np.isnan(crawler_obj.sway)])

def sway_max(crawler_obj):
        return max(crawler_obj.sway[~np.isnan(crawler_obj.sway)])

def sway_min(crawler_obj):
        return min(crawler_obj.sway[~np.isnan(crawler_obj.sway)])

def vedba_mean(crawler_obj):
        return _avg(crawler_obj.vedba[~np.isnan(crawler_obj.vedba)])

def vedba_var(crawler_obj):
        return _var(crawler_obj.vedba[~np.isnan(crawler_obj.vedba)])

def vedba_max(crawler_obj):
        return max(crawler_obj.vedba[~np.isnan(crawler_obj.vedba)])

def vedba_min(crawler_obj):
        return min(crawler_obj.vedba[~np.isnan(crawler_obj.vedba)])

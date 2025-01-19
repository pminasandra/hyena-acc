# Pranav Minasandra
# pminasandra.github.io
# Jan 16, 2024
# Wow I've gotten so much better at coding now

import os
import os.path

import config
import crawler
import handling_hyena_hdf5
import read_audits
from variables import *

AllAudits = os.listdir(DROPBOXROOT + AUDITS)
AllAudits = [name[0:9] for name in AllAudits]

for hyena in AllAudits:
    hyena_LoLs = handling_hyena_hdf5.hdf5_ListsOfVariables(
                        HDD_MNT_PNT+D_hdf5+hyena+"_A_25hz.h5"
                        )
    hyena_start_time = hyena_LoLs[4]
    LoadedAuditFile = read_audits.load_audit_file(DROPBOXROOT +AUDITS +hyena +'behaud.txt')
    SOAs, EOAs = read_audits.indices_of_audit_starts_and_ends(LoadedAuditFile)
    AuditIndices = list(zip(SOAs, EOAs))
    print(hyena, '\n', LoadedAuditFile)
## Each element in this list is start and end **INDEX in LoadedAuditFile** of each audit

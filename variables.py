
###     Navigating the file system to do stuff

# NOTE: All directories are stings ending with "/" (or "\" on windows)
# HDD_MNT_PNT + D_hdf5 needs to point to the folder with hdf5 files
# DROPBOXROOT + AUDITS needs to point to the folder with .behaud files
# Sorry for this horrible way of doing things.
# Back then I didn't know much about os.path
# And files were still coming to me when the code was being written


#       Directories on the HDD
HDD_MNT_PNT = '/media/pranav/pranav/'    #Change to appropriate path
D_hdf5 = 'from_ari/acc_lowres/'
## acc_lowres contains the hdf5 files. Modify the variable appropriately, so that HDD_MNT_PNT/D_hdf5/ is pointed to your hdf5 files


#       Directories on computer
PROJECTROOT = '/media/pranav/Data1/Personal/Projects/Completed/Strandburg-Peshkin 2019-20/'
FIGURES = 'Figures/'
DATA = 'Data/'
TEMP = 'temp/'
## These directories will contain all the code and the results

#       Directories on Dropbox
DROPBOXROOT = '/home/pranav/Dropbox/'
AUDITS = 'playback audit output/'
# Point to the location of your own audits. Need not necessarily be on dropbox.
###########################################################################################################################################################

###     HYENA NAMES

WRTH = "WRTH"
BORA = "BORA"
BYTE = "BYTE"
MGTA = "MGTA"
FAY  = "FAY"

###     CORRESPONDING TAGS

TAG_LOOKUP = {
WRTH : 'cc16_352a',
BORA : 'cc16_352b',
BYTE : 'cc16_354a',
MGTA : 'cc16_360a',
FAY : 'cc16_366a'
}

IND_LOOKUP = {b:a for a,b in TAG_LOOKUP.items()}##      Inverted dictionary.

###     STATES (FROM AUDIT)

LYING   = "LYING"
LYUP    = "LYUP"
SIT     = "SIT"
STAND   = "STAND"
WALK    = "WALK"
WANSNF  = "WANSNF"
LOPE    = "LOPE"
GALLOP  = "GALLOP"

STATES  = [LYING, LYUP, STAND, WALK, LOPE]

###     EVENTS (FROM AUDIT)

FEED    = "FEED"
LUNGE   = "LUNGE"
GREET   = "GREET"
POOP    = "POOP"
PEE     = "PEE"
GRMSELF = "GRMSELF"
GRMOTH  = "GRMOTH"
SNFGRND = "SNFGRND"
HB      = "HB"
PASTE   = "PASTE"
DIG     = "DIG"
ROLL    = "ROLL"
CHASE   = "CHASE"
CAR     = "CAR"
SCRATCH = "SCRATCH"
BITESHAKE      = "BITE-SHAKE"
VOMIT   = "VOMIT"
BOW     = "BOW"
PAWGRND = "PAWGRND"
MOUNT   = "MOUNT"
DRAG    = "DRAG"
CARPALCRAWL    = "CARPAL-CRAWL"
START   = "SOA"
END     = "EOA" 

EVENTS  = [FEED, LUNGE, GREET, POOP, PEE, GRMSELF, GRMOTH, SNFGRND, HB, PASTE, DIG, ROLL, CHASE,\
                CAR, SCRATCH, BITESHAKE, VOMIT, BOW, PAWGRND, MOUNT, DRAG, CARPALCRAWL, START, END, WANSNF, GALLOP, SIT]

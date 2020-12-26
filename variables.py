
###     Navigating the file system to do stuff

#       Directories on the HDD
HDD_MNT_PNT = '/media/pranav/pranav/'    #Change to appropriate path
D1 = 'cc16/'    #Where to find folders containing appropriate files for each tagged animal. Set to cc16 unless edited.
## Note that D2 (within D1) are directories with the names given in TAG_LOOKUP
D_hdf5 = 'from_ari/acc_lowres/'

#       Directories on computer
PROJECTROOT = '/media/pranav/Data1/Personal/Projects/Strandburg-Peshkin 2019-20/'
FIGURES = 'Figures/'
DATA = 'Data/'
TEMP = 'temp/'

#       Directories on Dropbox
DROPBOXROOT = '/home/pranav/Dropbox/'
AUDITS = 'playback audit output/'
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

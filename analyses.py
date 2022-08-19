# This file performs analyses of classifiers wrt training data

import sklearn
from sklearn.metrics import plot_confusion_matrix, precision_recall_fscore_support, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import random
import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import datetime as dt

from classifier import *
from variables import *
from config import *
from read_audits import *


ALL_FEATURES_DIR = PROJECTROOT + DATA + "FeaturesInTotal/"
GROUNDTRUTH_FEATURES_DIR = PROJECTROOT + DATA + "ExtractedFeatures/"

ALL_CLASSIFICATIONS_DIR = PROJECTROOT + DATA + "ClassificationsInTotal/"

HYENAS = [hyena for (hyena, tag) in TAG_LOOKUP.items()]
AUDITS = [File for File in os.listdir(GROUNDTRUTH_FEATURES_DIR) if File[-3:] == "csv" if File not in ["TrainingData.csv", "TestData.csv", "AllData.csv"]]


def _read_features_and_states_from_groundtruth_csv(csvfile):
    LoadedLines = [x.rstrip("\n") for x in open(csvfile, "r")][1:]
    Classes = [Line.split(",")[1] for Line in LoadedLines]
    Features = [[float(x) for x in Line.split(",")[2:]] for Line in LoadedLines]
    return np.array(Features), np.array(Classes)

def _read_features_from_alldata_csv(csvfile):
    LoadedLines = [x.rstrip("\n") for x in open(csvfile, "r")][1:]
    Features = [[float(x) for x in Line.split(",")[1:]] for Line in LoadedLines]
    return np.array(Features)

    
def generate_combined_data_files(prop, seed):
    """
    Generates the files TrainingData.csv, TestData.csv, and AllData.csv in the directory
    PROJECTROOT/DATA/ExtractedFeatures. The data in these files is obtained by random 
    shuffling and retains none of the original temporal order of each time window.

    Args:
        prop (float): Proportion of data to be reserved as Testing Data, in 0-1.
        seed (int | str | float): seed to use for the random number generator.
            In this project I used "the infinite devourer who guards the void between the realms" because
            in the dark, illuminated only by this screen, you never really know what is lurking around.
    """

    TotalList = []
    for audit in AUDITS:
        TotalList.extend([Line for Line in open(GROUNDTRUTH_FEATURES_DIR + audit)][1:])

    random.seed(seed)
    random.shuffle(TotalList)

    TrainingList = TotalList[int(prop * len(TotalList)):]
    TestList = TotalList[:int(prop * len(TotalList))]

    Titles = [x for x in open(GROUNDTRUTH_FEATURES_DIR + AUDITS[0])][0]

    with open(GROUNDTRUTH_FEATURES_DIR + "AllData.csv", "w") as AllDataFile:
        AllDataFile.write(Titles)
        for Line in TotalList:
            AllDataFile.write(Line)
        
    with open(GROUNDTRUTH_FEATURES_DIR + "TrainingData.csv", "w") as TrainingDataFile:
        TrainingDataFile.write(Titles)
        for Line in TrainingList:
            TrainingDataFile.write(Line)

    with open(GROUNDTRUTH_FEATURES_DIR + "TestData.csv", "w") as TestDataFile:
        TestDataFile.write(Titles)
        for Line in TestList:
            TestDataFile.write(Line)


def get_metrics_for_randomised_testing():
    """
    Generates figures and tables that describe the performance of SVM, k-NN, and Random Forest classifiers trained on
    TrainingData.csv and tested on TestData.csv generated in generate_combined_data_files.

    Args:
        none
    """

    Omninode_Dict = {x:x for x in STATES}
    Bundle = ClassifierBundle("Omninode", STATES, Omninode_Dict, "SVM,k-NN,RF")

    TrainingFeatures, TrainingClasses = _read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + "TrainingData.csv")
    TestFeatures, TestClasses = _read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + "TestData.csv")

    Bundle.train(TrainingFeatures, TrainingClasses)
    Predictions = Bundle.classify(TestFeatures)

    plot_confusion_matrix(Bundle.ClassifiersToUse[0], TestFeatures, TestClasses, normalize='true', cmap='Reds', labels=STATES)
    plt.title("SVM Confusion Matrix for randomised testing")
    plt.savefig(PROJECTROOT + FIGURES + "SVM_Randomised_Testing_ConfusionMatrix.png")
    plt.savefig(PROJECTROOT + FIGURES + "SVM_Randomised_Testing_ConfusionMatrix.pgf")
    with open(PROJECTROOT + DATA + "ClassifierPerformanceResults/" + "SVM_Randomised_Testing_Results.txt", "w") as ResultsLog:
        precision, recall, fscore, support = precision_recall_fscore_support(TestClasses, Predictions['SVM'], labels=STATES)
        accuracy = accuracy_score(TestClasses, Predictions['SVM'])

        ResultsLog.write("Classifications for an SVM classifier.\n\n")
        ResultsLog.write("Precision Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in precision]) + "\n\n")

        ResultsLog.write("Recall Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in recall]) + "\n\n")

        ResultsLog.write("Accuracy Score: %.2f\n\n" % accuracy)

        ResultsLog.write("LaTeX usable code provided here:\n\n")
        ResultsLog.write("\\begin{tabular}{*%dc}\n" % len(STATES))
        ResultsLog.write("- & " + " & ".join(STATES) + "\\\\\n")
        ResultsLog.write("Precision & " + " & ".join(["%.2f"%x for x in precision]) + "\\\\\n")
        ResultsLog.write("Recall & " + " & ".join(["%.2f"%x for x in recall]) + "\\\\\n")
        ResultsLog.write("\\end{tabular}\n")
        ResultsLog.close()

    plt.cla()
    plot_confusion_matrix(Bundle.ClassifiersToUse[1], TestFeatures, TestClasses, normalize='true', cmap='Reds', labels=STATES)
    plt.title("k-NN Confusion Matrix for randomised testing")
    plt.savefig(PROJECTROOT + FIGURES + "k-NN_Randomised_Testing_ConfusionMatrix.png")
    plt.savefig(PROJECTROOT + FIGURES + "k-NN_Randomised_Testing_ConfusionMatrix.pgf")
    with open(PROJECTROOT + DATA + "ClassifierPerformanceResults/" + "k-NN_Randomised_Testing_Results.txt", "w") as ResultsLog:
        precision, recall, fscore, support = precision_recall_fscore_support(TestClasses, Predictions['k-NN'], labels=STATES)
        accuracy = accuracy_score(TestClasses, Predictions['k-NN'])

        ResultsLog.write("Classifications for an k-NN classifier.\n\n")
        ResultsLog.write("Precision Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in precision]) + "\n\n")

        ResultsLog.write("Recall Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in recall]) + "\n\n")

        ResultsLog.write("Accuracy Score: %.2f\n\n" % accuracy)

        ResultsLog.write("LaTeX usable code provided here:\n\n")
        ResultsLog.write("\\begin{tabular}{*%dc}\n" % len(STATES))
        ResultsLog.write("- & " + " & ".join(STATES) + "\\\\\n")
        ResultsLog.write("Precision & " + " & ".join(["%.2f"%x for x in precision]) + "\\\\\n")
        ResultsLog.write("Recall & " + " & ".join(["%.2f"%x for x in recall]) + "\\\\\n")
        ResultsLog.write("\\end{tabular}\n")
        ResultsLog.close()

    plt.cla()
    plot_confusion_matrix(Bundle.ClassifiersToUse[2], TestFeatures, TestClasses, normalize='true', cmap='Reds', labels=STATES)
    plt.title("RF Confusion Matrix for randomised testing")
    plt.savefig(PROJECTROOT + FIGURES + "RF_Randomised_Testing_ConfusionMatrix.png")
    plt.savefig(PROJECTROOT + FIGURES + "RF_Randomised_Testing_ConfusionMatrix.pgf")
    with open(PROJECTROOT + DATA + "ClassifierPerformanceResults/" + "RF_Randomised_Testing_Results.txt", "w") as ResultsLog:
        precision, recall, fscore, support = precision_recall_fscore_support(TestClasses, Predictions['RF'], labels=STATES)
        accuracy = accuracy_score(TestClasses, Predictions['RF'])

        ResultsLog.write("Classifications for an RF classifier.\n\n")
        ResultsLog.write("Precision Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in precision]) + "\n\n")

        ResultsLog.write("Recall Table:\n")
        ResultsLog.write("\t".join(STATES) + "\n")
        ResultsLog.write("\t".join(["%.2f"%x for x in recall]) + "\n\n")

        ResultsLog.write("Accuracy Score: %.2f\n\n" % accuracy)

        ResultsLog.write("LaTeX usable code provided here:\n\n")
        ResultsLog.write("\\begin{tabular}{*%dc}\n" % len(STATES))
        ResultsLog.write("- & " + " & ".join(STATES) + "\\\\\n")
        ResultsLog.write("Precision & " + " & ".join(["%.2f"%x for x in precision]) + "\\\\\n")
        ResultsLog.write("Recall & " + " & ".join(["%.2f"%x for x in recall]) + "\\\\\n")
        ResultsLog.write("\\end{tabular}\n")
        ResultsLog.close()


def get_metrics_for_auditwise_testing():
    """
    Generates figures and tables that describe the performance of SVM, k-NN, and Random Forest classifiers trained by leaving
    out individual audits on which the testing occurs.

    Args:
        none
    """

    Omninode_Dict = {x:x for x in STATES}
    Bundle = ClassifierBundle("Omninode", STATES, Omninode_Dict, "SVM,k-NN,RF")
    TempPredictions = []
    AllTestClasses = []

    for audit in AUDITS:
        AUDITS2 = [x for x in AUDITS.copy() if x != audit]
        TrainingFeatures, TrainingClasses = [], []
        for Audit in AUDITS2:
            TrainingFeatures.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[0])
            TrainingClasses.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[1])
        TestFeatures, TestClasses = _read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + audit)
        AllTestClasses.extend(list(TestClasses))

        Bundle.train(TrainingFeatures, TrainingClasses)
        TempPredictions.append(Bundle.classify(TestFeatures))

    AllTestPredictions = {}
    for Classifier in ['SVM','k-NN','RF']:
        AllTestPredictions[Classifier] = []
        for x in TempPredictions:
            AllTestPredictions[Classifier].extend(list(x[Classifier]))


    for Classifier in ['SVM','k-NN','RF']:
        cm = confusion_matrix(AllTestClasses, AllTestPredictions[Classifier], normalize='true', labels=STATES)
        plt.cla()
        disp = ConfusionMatrixDisplay(cm, display_labels=STATES)
        disp.plot(cmap='Reds')
        plt.title("{} Confusion Matrix for auditwise testing".format(Classifier))
        plt.savefig(PROJECTROOT + FIGURES + "{}_Auditwise_Testing_ConfusionMatrix.png".format(Classifier))
        plt.savefig(PROJECTROOT + FIGURES + "{}_Auditwise_Testing_ConfusionMatrix.pgf".format(Classifier))
        with open(PROJECTROOT + DATA + "ClassifierPerformanceResults/" + "{}_Auditwise_Testing_Results.txt".format(Classifier), "w") as ResultsLog:
            precision, recall, fscore, support = precision_recall_fscore_support(AllTestClasses, AllTestPredictions[Classifier], labels=STATES)
            accuracy = accuracy_score(AllTestClasses, AllTestPredictions[Classifier])

            ResultsLog.write("Classifications for {} classifier.\n\n".format(Classifier))
            ResultsLog.write("Precision Table:\n")
            ResultsLog.write("\t".join(STATES) + "\n")
            ResultsLog.write("\t".join(["%.2f"%x for x in precision]) + "\n\n")

            ResultsLog.write("Recall Table:\n")
            ResultsLog.write("\t".join(STATES) + "\n")
            ResultsLog.write("\t".join(["%.2f"%x for x in recall]) + "\n\n")

            ResultsLog.write("Accuracy Score: %.2f\n\n" % accuracy)

            ResultsLog.write("LaTeX usable code provided here:\n\n")
            ResultsLog.write("\\begin{tabular}{*%dc}\n" % len(STATES))
            ResultsLog.write("- & " + " & ".join(STATES) + "\\\\\n")
            ResultsLog.write("Precision & " + " & ".join(["%.2f"%x for x in precision]) + "\\\\\n")
            ResultsLog.write("Recall & " + " & ".join(["%.2f"%x for x in recall]) + "\\\\\n")
            ResultsLog.write("\\end{tabular}\n")
            ResultsLog.close()

def get_metrics_for_individualwise_testing():
    """
    Generates figures and tables that describe the performance of SVM, k-NN, and Random Forest classifiers trained by leaving
    out individual hyenas, on whose data the testing occurs.

    Args:
        none
    """

    Omninode_Dict = {x:x for x in STATES}
    Bundle = ClassifierBundle("Omninode", STATES, Omninode_Dict, "SVM,k-NN,RF")
    TempPredictions = []
    AllTestClasses = []
    
    HYENAS_AUDITS_AVAILABLE = list(set([x.split("_")[0] for x in AUDITS]))
    HYENAS_AUDITS_AVAILABLE.sort()
    for hyena in HYENAS_AUDITS_AVAILABLE:
        AUDITS_TRAINING = [x for x in AUDITS if x.split("_")[0] != hyena]
        AUDITS_TESTING = [x for x in AUDITS if x not in AUDITS_TRAINING]
        TrainingFeatures, TrainingClasses = [], []
        TestingFeatures, TestingClasses = [], []
        for Audit in AUDITS_TRAINING:
            TrainingFeatures.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[0])
            TrainingClasses.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[1])
        for Audit in AUDITS_TESTING:
            TestingFeatures.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[0])
            TestingClasses.extend(_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + Audit)[1])
        AllTestClasses.extend(list(TestingClasses))

        Bundle.train(TrainingFeatures, TrainingClasses)
        TempPredictions.append(Bundle.classify(TestingFeatures))

    AllTestPredictions = {}
    for Classifier in ['SVM','k-NN','RF']:
        AllTestPredictions[Classifier] = []
        for x in TempPredictions:
            AllTestPredictions[Classifier].extend(list(x[Classifier]))
    print(len(AllTestPredictions['SVM']))


    for Classifier in ['SVM','k-NN','RF']:
        cm = confusion_matrix(AllTestClasses, AllTestPredictions[Classifier], normalize='true', labels=STATES)
        plt.cla()
        disp = ConfusionMatrixDisplay(cm, display_labels=STATES)
        disp.plot(cmap='Reds')
        plt.title("{} Confusion Matrix for individualwise testing".format(Classifier))
        plt.savefig(PROJECTROOT + FIGURES + "{}_Individualwise_Testing_ConfusionMatrix.png".format(Classifier))
        plt.savefig(PROJECTROOT + FIGURES + "{}_Individualwise_Testing_ConfusionMatrix.pgf".format(Classifier))
        with open(PROJECTROOT + DATA + "ClassifierPerformanceResults/" + "{}_Individualwise_Testing_Results.txt".format(Classifier), "w") as ResultsLog:
            precision, recall, fscore, support = precision_recall_fscore_support(AllTestClasses, AllTestPredictions[Classifier], labels=STATES)
            accuracy = accuracy_score(AllTestClasses, AllTestPredictions[Classifier])

            ResultsLog.write("Classifications for {} classifier.\n\n".format(Classifier))
            ResultsLog.write("Precision Table:\n")
            ResultsLog.write("\t".join(STATES) + "\n")
            ResultsLog.write("\t".join(["%.2f"%x for x in precision]) + "\n\n")

            ResultsLog.write("Recall Table:\n")
            ResultsLog.write("\t".join(STATES) + "\n")
            ResultsLog.write("\t".join(["%.2f"%x for x in recall]) + "\n\n")

            ResultsLog.write("Accuracy Score: %.2f\n\n" % accuracy)

            ResultsLog.write("LaTeX usable code provided here:\n\n")
            ResultsLog.write("\\begin{tabular}{*%dc}\n" % len(STATES))
            ResultsLog.write("- & " + " & ".join(STATES) + "\\\\\n")
            ResultsLog.write("Precision & " + " & ".join(["%.2f"%x for x in precision]) + "\\\\\n")
            ResultsLog.write("Recall & " + " & ".join(["%.2f"%x for x in recall]) + "\\\\\n")
            ResultsLog.write("\\end{tabular}\n")
            ResultsLog.close()


def classify_all_available_data():
    """
    Reads all extracted features from PROJECTROOT/DATA/FeaturesInTotal/, and classifies them based on learning
    from AllData.csv generated from generate_combined_data_files. Stores these classifications in PROJECTROOT/DATA/ClassificationsInTotal/ .
    
    Args:
        none
    """

    for hyena in HYENAS:
        Features = _read_features_from_alldata_csv(ALL_FEATURES_DIR + hyena + ".csv")
        TimeStamps = [Line.split(",")[0] for Line in open(ALL_FEATURES_DIR + hyena + ".csv")][1:]

        Omninode_Dict = {x:x for x in STATES}
        Bundle = ClassifierBundle("Omninode", STATES, Omninode_Dict, "SVM,k-NN,RF")

        try:
            Bundle.train(*_read_features_and_states_from_groundtruth_csv(GROUNDTRUTH_FEATURES_DIR + "AllData.csv"))
        except FileNotFoundError as e:
            print("Run generate_combined_data_files() first!")
            print(e)

        AllClasses = Bundle.classify(Features)['RF'] #Random Forest was the best for us. Use the get_metrics_ function to decide your best, or use DecideBestClassifier in classifier.py
        with open(ALL_CLASSIFICATIONS_DIR + hyena + ".csv", "w") as File:
            File.write("time,state\n")
            for (TimeStamp, Classification) in zip(TimeStamps, AllClasses):
                File.write(",".join([TimeStamp, Classification])+"\n")

def _check_for_missing_data(filename):
    lines = [line.strip().split(",") for line in open(filename)][1:]
    TimeAndStates = [(dt.datetime.fromisoformat(line[0]).astimezone(tz=dt.timezone(dt.timedelta(hours=3))), line[1]) for line in lines]

    Date = TimeAndStates[0][0].date()

    time_1 = TimeAndStates[0][0] - dt.timedelta(seconds=WINDOW_DURATION)

    MissingTimesAndDurations = []
    for time, state in TimeAndStates:
        if time - time_1 != dt.timedelta(seconds = WINDOW_DURATION):
            MissingTimesAndDurations.append((time_1, (time-time_1).total_seconds()))
        time_1 = time

    return MissingTimesAndDurations

def generate_missing_data_report():
    """
    Looks for all points where the time skip between lines is not equal to config.WINDOW_DURATION
    """
    for hyena in HYENAS:
        report = open(PROJECTROOT + DATA + "MissingDataReport/" + hyena + ".csv", "w")
        MissingData = _check_for_missing_data(ALL_CLASSIFICATIONS_DIR + hyena + ".csv")
        report.write("timepoint,missing_dur\n")

        for point in MissingData:
            report.write(str(point[0])+ "," + str(point[1]) + "\n")

        report.close()
        
#generate_combined_data_files(0.15, "the infinite devourer who guards the void between the realms")
#get_metrics_for_randomised_testing()
#get_metrics_for_auditwise_testing()
#get_metrics_for_individualwise_testing()
#classify_all_available_data() #Check for nans in the AllFeature files first.
generate_missing_data_report()

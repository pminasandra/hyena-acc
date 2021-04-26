# uncompyle6 version 3.7.4
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.5 (default, Jul 28 2020, 12:59:40) 
# [GCC 9.3.0]
# Embedded file name: /media/pranav/Data1/Personal/Projects/Strandburg-Peshkin 2019-20/code/classifier.py
# Compiled at: 2020-03-13 17:22:47
# Size of source mod 2**32: 8496 bytes
from config import *
from errors import *
from variables import *
import os, random
from sklearn import svm
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from joblib import dump, load
import numpy as np
from matplotlib import pyplot as plt

def load_svm():
    from sklearn import svm
    return svm.SVC(gamma='scale')


def load_knn():
    from sklearn import neighbors
    return neighbors.KNeighborsClassifier(NEAREST_NEIGHBOUR_CLASSIFIER_K)


def load_RandomForest():
    from sklearn import ensemble
    return ensemble.RandomForestClassifier()


ClassifiersDictionary = {'SVM':load_svm, 
                        'k-NN':load_knn,
                        'RF':load_RandomForest}

class ClassifierBundle:
    """Class ClassifierBundle, one of several nodes in a hierarchical tree of nodes, whose class is TODO.   
                    Attributes are:

                    Functions are:
                                    classify: Takes features and returns classification.
                                    train: Takes features and classification, trains the learning algorithm.
                                    SaveLearning: Saves .joblib files [FUNCTIONALITY REMOVED]
                                    LoadLearning: Loads .joblib files [FUNCTIONALITY REMOVED]
                    Errors associated are: #TODO
                    """

    def __init__(self, NodeName, StatesConsidered, GroupedOutputs, ClassifiersToUse='RF'):
        """
        Init function for class ClassifierNode.
        Args:
                Nodename (str):      A string identifier for the node.
                StatesConsidered (list):A list of all states this classifier will have to consider.
                GroupedOutputs (dict):  A dictionary with desired outputs mapped to non-intersecting tuples
                                        that fall under those outputs. For example DYNAMIC could map to
                                        (WALK, LOPE).
                ClassifiersToUse (str): A string containing comma-separated keys from ClassifierDictionary.
                                        Represents what classifier(s) this node engages for classification.
        Returns:
               None, for now.
        Raises:
               None, for now.
        """
        self.StatesConsidered = StatesConsidered
        self.GroupedOutputs = GroupedOutputs
        self.ClassifiersToUse = [ClassifiersDictionary[Classifier.lstrip().rstrip()]() for Classifier in ClassifiersToUse.split(',')]
        self.ClassifierNames = ClassifiersToUse.split(',')

    def classify(self, FeatureTuple):
        """
        classification function for class ClassifierNode.
        Args:
                FeatureTuple (numpy.array):  A numpy.array containing all necessary features.
        Returns:
                Classification (dict):   Each element is a str:numpy.array. The str needs to be one of the elements of
                ClassifiersToUse. For example, to get the results of the Random Forest classification, use
                >>>> classify(<...>)['RF']
        Raises:
                None, for now.
        """
        Mat = []
        for Classifier in self.ClassifiersToUse:
            Mat.append(Classifier.predict(FeatureTuple))
        return {self.ClassifierNames[i]:Mat[i] for i in range(len(self.ClassifierNames))}

    def train(self, FeaturesForTraining, ClassificationsForTraining):
        """
                train function to implement learning in ClassifierNode, trains all available classifiers and deletes all but the best one.
                Args:
                        FeaturesForTraining (numpy.array):   A numpy array containing all features, such that len(FeatureTuple[i])
                                                is the same for every run on this node.
                        Classification (numpy.array):   A numpy array of strings indicating the true classification. All strings should be members of 
                                                self.GroupedOutputs (items!!!!).
                Returns:
                       None, for now.
                Raises:
                       None, for now.
                """
        for Classifier in self.ClassifiersToUse:
                Classifier.fit(X=FeaturesForTraining, y=ClassificationsForTraining)

    def UseBestClassifier(self, FeaturesForTraining, ClassificationsForTraining):
        if CLASSIFIER_SELECTION_HEURISTIC == 'ACCURACY':
            BestClassifier = self.ClassifiersToUse[0]
            TrainedClassifiers = self.ClassifiersToUse
            BestAccuracy = accuracy_score(BestClassifier.predict(FeaturesForTraining), ClassificationsForTraining)
            for TrainedClassifier in TrainedClassifiers:
                if accuracy_score(TrainedClassifier.predict(FeaturesForTraining), ClassificationsForTraining) > BestAccuracy:
                    BestClassifier = TrainedClassifier
                    BestAccuracy = accuracy(BestClassifier.predict(FeaturesForTraining), ClassificationsForTraining)

        return BestClassifier


    def _ShowTrainingForAllClassifiers(self, FeaturesForTraining, ClassificationsForTraining, FeaturesForTesting, ClassificationsForTesting):
        self.train(FeaturesForTraining, ClassificationsForTraining)
        BarGraph_x_pos = np.arange(len(self.ClassifiersToUse))
        BarGraph_y_vals = []
        i = 0
        for Classifier in self.ClassifiersToUse:
            print('\x1b[1;32m', Classifier, '\x1b[0;39m:')
            print('\nConfusion Matrix:')
            print('For the states: ', STATES)
            print(confusion_matrix(ClassificationsForTesting, (self.classify(FeaturesForTesting)[i]), labels=STATES, normalize=True))
            print('\nClassification Report:')
            print(classification_report(ClassificationsForTesting, self.classify(FeaturesForTesting)[i]))
            i += 1
        for results in self.classify(FeaturesForTesting):
            BarGraph_y_vals.append(accuracy_score(ClassificationsForTesting, results))
        plt.bar(BarGraph_x_pos, BarGraph_y_vals, color='black', tick_label=(self.ClassifierNames), width=0.4)
        plt.axis([-0.5, 2.5, 0.0, 1])
        plt.xlabel('Classifiers used')
        plt.ylabel('Fraction of results accurately predicted')
        plt.show()


class ClassifierTree:
    """A tree of ClassifierNode architectures that can perform a classification."""

    def __init__(self):
        pass

    def classify():
        pass

    def train():
        pass
# okay decompiling classifier.cpython-38.pyc

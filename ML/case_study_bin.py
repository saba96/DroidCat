# Import all classification package
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier

from sklearn.cross_validation import cross_val_score
from sklearn.metrics import precision_score,recall_score,f1_score,roc_auc_score,accuracy_score
from sklearn import cross_validation

from sklearn.metrics import confusion_matrix

import numpy
import random
import os
import sys
import string

from configs import *
from featureLoader import *

# 10-fold cross-validation
def cv(model, features, labels):
    sr=len(features)
    #sr=features.shape[0]
    #k=10
    k=sr
    subsize = sr/k
    subsamples=list()
    sublabels=list()

    for k in range(0, len(labels)):
        if labels[k].lower() != "benign":
            labels[k] = "MALICIOUS"

    predicted_labels=list()
    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    for j in range(0,k):
        subsamples.append( (features[j*subsize:(j+1)*subsize]) )
        sublabels.append( (labels[j*subsize:(j+1)*subsize]) )

    for j in range(0,k):
        testFeatures = subsamples[j]
        testLabels = sublabels[j]

        trainFeatures = list()
        trainLabels = list()
        for r in range(0,k):
            if r==j:
                continue
            #trainFeatures.append( subsamples[r] )
            #trainLabels.append( sublabels[r] )
            for fl in subsamples[r]:
                trainFeatures.append(fl)
            for lal in sublabels[r]:
                trainLabels.append( lal )

        model.fit( trainFeatures, trainLabels )
        y_pred = model.predict( testFeatures )
        #if testLabels[0].lower() == "fakeinst":
        #if j in [47, 166, 209]:
        #if j in [85, 114, 121, 175, 188, 197, 209, 235, 240]:
        #if j in [88, 118, 183, 206, 219, 251]:
        if j in [8, 43, 12, 156]:
            print >> sys.stderr, "j=%d, testLabels: %s" % (j, str(testLabels))
            print >> sys.stderr, "j=%d, predicted: %s" % (j, str(y_pred))

        predicted_labels.append ( y_pred )

    return [0]

def selectFeatures(features, selection):
    featureSelect=[idx-1 for idx in selection]
    selectedfeatures=list()
    for featureRow in features:
        selectedfeatures.append ( featureRow[ featureSelect ] )
    return selectedfeatures

if __name__=="__main__":

    (features, labels, Testfeatures, Testlabels) = getTrainingData( False, pruneMinor=False)

    models = (RandomForestClassifier(n_estimators = 100),)#, SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())
    #models = (SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())

    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    fh = file ('/tmp/temp', 'w')
    print >> fh, '\t'.join(uniqLabels)

    for model in models:
        #for fset in (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_Y, FSET_YY, FSET_YYY):
        for fset in (FSET_YYY,):
            print >> fh, 'model ' + str(model) + "\t" + "feature set " + str(fset)
            ret = cv (model, selectFeatures( features, fset ), labels)

    fh.flush()
    fh.close()

    sys.exit(0)

# hcai: set ts=4 tw=100 sts=4 sw=4

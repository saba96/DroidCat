# Import all classification package
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier, BaggingClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import precision_score,recall_score,f1_score,roc_auc_score,accuracy_score

from sklearn.metrics import confusion_matrix

#from sklearn.mixture import GaussianMixture
#from sklearn.mixture import BayesianGaussianMixture
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

import numpy
import random
import os
import sys
import string

import inspect, re

from configs import *
from featureLoader import *
from common import *

g_binary = False # binary or multiple-class classification

HOLDOUT_RATE=0.33

def varname(p):
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)

# hold-out 20% evaluation
def holdout(model, features, labels):
    sr=len(features)
    assert sr==len(labels)

    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    lab2idx=dict()
    for k in range(0, sr):
        lab = labels[k]
        if lab not in lab2idx.keys():
            lab2idx[lab] = list()
        lab2idx[lab].append (k)

    testfeatures=list()
    testlabels=list()

    allidx2rm=list()
    for lab in lab2idx.keys():
        sz = len(lab2idx[lab])
        nrm = int(sz*HOLDOUT_RATE);
        idxrm = set()
        while len(idxrm) < nrm:
            t = random.randint(0,sz-1)
            idxrm.add ( lab2idx[lab][t] )
        for idx in idxrm:
            testfeatures.append ( features[idx] )
            testlabels.append ( labels[idx] )
            allidx2rm.append(idx)

    trainfeatures=list()
    trainlabels=list()
    for l in range(0, sr):
        if l in allidx2rm:
            continue
        trainfeatures.append(features[l])
        trainlabels.append(labels[l])

    trainfeatures, testfeatures  = processingFeatures(model, trainfeatures, trainlabels, testfeatures, testlabels)

    print >> sys.stdout, "%d samples for training, %d samples  held out will be used for testing" % (len (trainfeatures), len(testfeatures))

    predicted_labels=list()
    model.fit ( trainfeatures, trainlabels )

    for j in range(0, len(testlabels)):
        y_pred = model.predict( [testfeatures[j]] )
        #print >> sys.stderr, "j=%d, testLabels: %s" % (j, str(testlabels[j]))
        #print >> sys.stderr, "j=%d, predicted: %s" % (j, str(y_pred))

        predicted_labels.append ( y_pred )

    '''
    for i in range(0, len(predicted_labels)):
        #print type(predicted_labels[i])
        if predicted_labels[i][0] not in big_families:
            predicted_labels[i] = numpy.array(['MALICIOUS'])
    '''

    #print "%s\n%s\n" % (str(sublabels), str(predicted_labels))
    #big_families=["DroidKungfu", "ProxyTrojan/NotCompatible/NioServ", "GoldDream", "Plankton", "FakeInst", "BENIGN", "MALICIOUS"]

    y_pred = predicted_labels

    if g_binary:
        prec=precision_score(testlabels, y_pred, average='binary', pos_label='MALICIOUS')
        rec=recall_score(testlabels, y_pred, average='binary', pos_label='MALICIOUS')
        f1=f1_score(testlabels, y_pred, average='binary', pos_label='MALICIOUS')

    else:
        prec=precision_score(testlabels, y_pred, average='weighted')
        rec=recall_score(testlabels, y_pred, average='weighted')
        f1=f1_score(testlabels, y_pred, average='weighted')

    '''
    cvprec = cross_val_score(estimator=model, X=features, y=labels, cv=10, scoring='precision_weighted')
    cvrec = cross_val_score(estimator=model, X=features, y=labels, cv=10, scoring='recall_weighted')
    cvf1 = cross_val_score(estimator=model, X=features, y=labels, cv=10, scoring='f1_weighted')
    '''


    acc=accuracy_score( testlabels, y_pred )

    #print "precision=%f, recall=%f, f1=%f, acc=%f" % (prec, rec, f1, acc)

    #return confusion_matrix(testlabels, predicted_labels, labels=list(uniqLabels))
    #return confusion_matrix(sublabels, predicted_labels, labels=big_families)
    return (prec, rec, f1, acc)
    #return (numpy.average(cvprec), numpy.average(cvrec), numpy.average(cvf1), acc)

def loadFeatures(datatag, label):
    sample_features = {}
    sample_labels = {}

    for line in file(datatag+'.txt', 'r').readlines():
        items = string.split(line.lstrip().rstrip())
        apk = items[0]
        fvec = [float(f) for f in items[1:]]
        sample_features[apk] = fvec
        sample_labels[apk] = label

    print >> sys.stderr, 'loaded static features from %s: %d feature vectors' % (datatag, len (sample_features))
    return (sample_features, sample_labels)

def mergeStaticToDroidspan(mf, ml, smf, sml):
    orgkeys = mf.keys()
    for key in orgkeys:
        if key in smf.keys():
            mf[key] = mf[key] + smf[key]
        else:
            del mf[key]
            del ml[key]


def selectFeatures(features, selection):
    featureSelect=[idx-1 for idx in selection]
    selectedfeatures=list()
    for featureRow in features:
        selectedfeatures.append ( featureRow[ featureSelect ] )
    return selectedfeatures

def predict(f, l, fh):
    (features, labels) = adapt (f, l)

    print "======== in dataset ======="
    l2c = malwareCatStat(labels)
    for lab in l2c.keys():
        print "%s\t%s" % (lab, l2c[lab])

    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    #models = (RandomForestClassifier(n_estimators = 128, random_state=0), GaussianProcessClassifier(), ExtraTreesClassifier(n_estimators=120), AdaBoostClassifier(n_estimators=120), GradientBoostingClassifier(n_estimators=120), BaggingClassifier (n_estimators=120), SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())
    #models = (ExtraTreesClassifier(n_estimators=128, random_state=0),  AdaBoostClassifier(n_estimators=120), GradientBoostingClassifier(n_estimators=120), BaggingClassifier (n_estimators=120), )#SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())
    #models = (SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())

    #models = (RandomForestClassifier(n_estimators = 128, random_state=0), )#SVC(kernel='rbf'), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), GaussianNB(), MultinomialNB(), BernoulliNB())

    #models = (RandomForestClassifier(n_estimators = 120, random_state=0), ExtraTreesClassifier(n_estimators=100), )#GradientBoostingClassifier(n_estimators=120), BaggingClassifier (n_estimators=120), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), MultinomialNB())
    models = (RandomForestClassifier(n_estimators = 222, random_state=0), ExtraTreesClassifier(n_estimators=222), )#GradientBoostingClassifier(n_estimators=120), BaggingClassifier (n_estimators=120), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), MultinomialNB())

    #fsets = (FSET_FULL,FSET_NOICC, FSET_MIN, FSET_YYY_G, FSET_FULL_TOP, FSET_YYY_TOP, FSET_FULL_TOP_G, FSET_YYY_TOP_G)
    #fsets = (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_Y, FSET_YY, FSET_YYY):

    #fsets = (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_YYY, FSET_FULL_TOP, FSET_YYY_TOP, FSET_FULL_TOP_G, FSET_YYY_TOP_G)
    #fsets = (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_YYY, FSET_FULL_TOP_G, FSET_YYY_TOP_G)
    #fsets = (FSET_NOICC, FSET_G, FSET_SEC)
    #fsets = (FSET_FULL, FSET_G, FSET_SEC)
    #fsets = (FSET_FULL, FSET_SEC)
    fsets = (FSET_FULL, )

    #fh = file ('confusion_matrix_formajorfamilyonly_holdout_all.txt', 'w')
    print >> fh, '\t'.join(uniqLabels)

    model2ret={}
    for model in models:
        #for fset in (FSET_FULL, FSET_G, FSET_ICC, FSET_SEC, FSET_Y, FSET_YY, FSET_YYY):
        #for fset in (FSET_FULL, FSET_YYY, FSET_G):
        #for fset in (FSET_FULL,FSET_NOICC, FSET_MIN, FSET_YYY_G, FSET_FULL_TOP, FSET_YYY_TOP, FSET_FULL_TOP_G, FSET_YYY_TOP_G):
        for fset in fsets:
        #for fset in (FSET_G,):
            print >> fh, 'model ' + str(model) + "\t" + "feature set " + FSET_NAMES[str(fset)]
            ret = holdout(model, features, labels)
            model2ret[str(model)+str(fset)] = ret

    tlabs=('precision', 'recall', 'F1', 'accuracy')
    for i in (0,1,2,3):
        print tlabs[i]
        cols=list()
        for model in models:
            #print 'model ' + str(model)
            col=list()
            for fset in fsets:
                ret = model2ret[str(model)+str(fset)]
                col.append(ret[i])
            cols.append(col)
        for r in range(0,len(cols[0])):
            for c in range(0,len(cols)):
                print >> fh, "%s\t" % cols[c][r],
            print >> fh

if __name__=="__main__":
    if len(sys.argv)>=2:
        g_binary = sys.argv[1].lower()=='true'

    #bPrune = g_binary
    bPrune = True

    '''
    datasets = [ {"benign":["zoobenign-2010"], "malware":["zoo-2010"]},
                  {"benign":["zoobenign-2011"], "malware":["zoo-2011"]} ]

    datasets = [ {"benign":["zoobenign-2010"], "malware":["zoo-2010"]},
                  {"benign":["zoobenign-2011"], "malware":["zoo-2011"]},
                  {"benign":["zoobenign-2012"], "malware":["zoo-2012", "malware-2013"]},
                  {"benign":["zoobenign-2013"], "malware":["zoo-2013", "vs-2013", "drebin"]},
                  {"benign":["zoobenign-2014", "benign-2014"], "malware":["zoo-2014", "vs-2014"]},
                  {"benign":["zoobenign-2015"], "malware":["zoo-2015", "vs-2015"]},
                  {"benign":["zoobenign-2016"], "malware":["zoo-2016", "vs-2016"]},
                  {"benign":["benign-2017"], "malware":["zoo-2017", "malware-2017"]} ]
    datasets = [ {"benign":["zoobenign-2010"], "malware":["zoo-2010"]},
                  {"benign":["zoobenign-2011"], "malware":["zoo-2011"]},
                  {"benign":["zoobenign-2012"], "malware":["malware-2013"]},
                  {"benign":["zoobenign-2013"], "malware":["drebin"]},
                  {"benign":["zoobenign-2014", "benign-2014"], "malware":["vs-2014"]},
                  {"benign":["zoobenign-2015"], "malware":["vs-2015"]},
                  {"benign":["zoobenign-2016"], "malware":["vs-2016"]},
                  {"benign":["benign-2017"], "malware":["zoo-2017", "malware-2017"]} ]

    datasets = [ {"benign":["zoobenign-2010"], "malware":["zoo-2010"]},
                  {"benign":["zoobenign-2011"], "malware":["zoo-2011"]},
                  {"benign":["zoobenign-2012"], "malware":["zoo-2012"]},
                  {"benign":["zoobenign-2013"], "malware":["zoo-2013", "vs-2013"]},
                  {"benign":["zoobenign-2014"], "malware":["zoo-2014", "vs-2014"]},
                  {"benign":["zoobenign-2015"], "malware":["zoo-2015", "vs-2015"]},
                  {"benign":["zoobenign-2016"], "malware":["zoo-2016", "vs-2016"]},
                  {"benign":["benign-2017"], "malware":["zoo-2017"]} ]
    '''

    datasets = [ {"benign":["zoobenign2010"], "malware":["zoo2010"]},
                  {"benign":["zoobenign2011"], "malware":["zoo2011"]},
                  {"benign":["zoobenign2012"], "malware":["zoo2012"]},
                  {"benign":["zoobenign2013"], "malware":["vs2013"]},
                  {"benign":["zoobenign2014"], "malware":["vs2014"]},
                  {"benign":["zoobenign2015"], "malware":["vs2015"]},
                  {"benign":["zoobenign2016"], "malware":["vs2016"]},
                  {"benign":["benign2017"], "malware":["zoo2017"]} ]

    '''
    datasets = [  {"benign":["zoobenign2016"], "malware":["vs2016"]} ]
    '''

    fh = sys.stdout
    #fh = file ('confusion_matrix_formajorfamilyonly_holdout_all.txt', 'w')

    for i in range(0, len(datasets)):
        print "work on %s ... " % ( datasets[i] )
        (bft, blt) = ({}, {})
        for k in range(0, len(datasets[i]['benign'])):
            (bf, bl) = loadBenignData("features_droidcat/"+datasets[i]['benign'][k])
            (sbf, sbl) = loadFeatures("features_droidcat/static/"+datasets[i]['benign'][k], "BENIGN")
            mergeStaticToDroidspan(bf, bl, sbf, sbl)

            bft.update (bf)
            blt.update (bl)
        for k in range(0, len(datasets[i]['malware'])):
            (mf, ml) = loadMalwareNoFamily("features_droidcat/"+datasets[i]['malware'][k])
            (smf, sml) = loadFeatures("features_droidcat/static/"+datasets[i]['malware'][k], "MALICIOUS")
            mergeStaticToDroidspan(mf, ml, smf, sml)

            bft.update (mf)
            blt.update (ml)

        for i in range(0,10):
            predict(bft,blt, fh)

    fh.flush()
    fh.close()

    sys.exit(0)

# hcai: set ts=4 tw=120 sts=4 sw=4

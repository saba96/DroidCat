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
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler

import numpy
import random
import os
import sys
import string

import inspect, re

#from classes.sample import Sample
import pickle
import copy
from sklearn.feature_selection import SelectFromModel

HOLDOUT_RATE=0.90
#HOLDOUT_RATE=0.33

g_binary = False # binary or multiple-class classification
featureframe = {}
g_fnames = set()
tagprefix="/home/hcai/Downloads/droidsieve/static.pickle."

def get_families(path_md5_families):
    families = {}
    metainfo = open(path_md5_families)
    for line in metainfo.readlines():
        split = line.split()
        if len(split) == 2:
            md5 = str(split[0]).strip()
            date = str(split[1]).strip()
            families[md5] = date
    return families

def varname(p):
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)

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

    print >> sys.stdout, "%d samples for training, %d samples held out will be used for testing" % (len (trainfeatures), len(testfeatures))

    features = numpy.concatenate ( (trainfeatures, testfeatures), axis=0 )
    print "before feature scaling and selection: %d samples each with %d features" % (len(features), len(features[0]))
    print features[0]

    scaled_features = StandardScaler().fit_transform( features )

    sfm = SelectFromModel(model, threshold = 'median')
    sfm.fit( trainfeatures, trainlabels )
    selected_features = sfm.transform ( scaled_features )

    print "after feature scaling and selection: %d samples each with %d features" % (len(selected_features), len(selected_features[0]))
    print selected_features[0]

    _trainfeatures = numpy.zeros( shape=(len(trainfeatures), len(selected_features[0])) )
    _testfeatures = numpy.zeros( shape=(len(testfeatures), len(selected_features[0])) )

    for k in range(0, len(trainfeatures)):
        _trainfeatures[k] = selected_features[k]

    for k in range(0, len(testfeatures)):
        _testfeatures[k] = selected_features[k+len(trainfeatures)]

    trainfeatures = _trainfeatures
    testfeatures = _testfeatures

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

    if False and g_binary:
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


def selectFeatures(features, selection):
    featureSelect=[idx-1 for idx in selection]
    selectedfeatures=list()
    for featureRow in features:
        selectedfeatures.append ( featureRow[ featureSelect ] )
    return selectedfeatures

def malwareCatStat(labels):
    l2c={}
    for lab in labels:
        if lab not in l2c.keys():
            l2c[lab]=0
        l2c[lab]=l2c[lab]+1
    return l2c

def predict(f, l, fh):
    (features, labels) = adapt (f, l)

    print "======== in training dataset ======="
    l2c = malwareCatStat(labels)
    for lab in l2c.keys():
        print "%s\t%s" % (lab, l2c[lab])

    uniqLabels = set()
    for item in labels:
        uniqLabels.add (item)

    models = (ExtraTreesClassifier(n_estimators=1000), )#GradientBoostingClassifier(n_estimators=120), BaggingClassifier (n_estimators=120), SVC(kernel='linear'), DecisionTreeClassifier(random_state=None), KNeighborsClassifier(n_neighbors=5), MultinomialNB())

    print >> fh, '\t'.join(uniqLabels)

    model2ret={}
    for model in models:
        print >> fh, 'model ' + str(model)
        ret = holdout(model, features, labels)
        model2ret[str(model)] = ret

    tlabs=('precision', 'recall', 'F1', 'accuracy')
    for i in (0,1,2,3):
        print >> fh, tlabs[i]
        cols=list()
        for model in models:
            #print 'model ' + str(model)
            col=list()
            ret = model2ret[str(model)]
            col.append(ret[i])
            cols.append(col)
        for r in range(0,len(cols[0])):
            for c in range(0,len(cols)):
                print >> fh, "%s\t" % cols[c][r],
            print >> fh

def _loadFeatures(datatag):
    global g_fnames
    f = open(tagprefix+datatag, 'rb')
    sample_features = {}
    sample_labels = {}

    md5list=[]
    for line in file ('../ML/samplelists/md5.apks.'+datatag).readlines():
        md5list.append (line.lstrip('\r\n').rstrip('\r\n'))

    while 1:
        try:
            sample = pickle.load(f)
            if sample.md5 not in md5list:
                #print "md5: %s not in the list; skipped" % (sample.md5)
                continue

            #sample.pprint()
            fnames = [ft.name.lstrip().rstrip().encode('ascii','replace') for ft in sample.features]
            #print sorted(fnames)
            #print len(fnames)
            '''
            if 'com.zws.inventorymng.permission.JPUSH_MESSAGE' in fnames:
                print "got it: %s" % (sorted(fnames))
                sys.exit(2)
            for fname in fnames:
                g_fnames.add (fname)
            '''
            g_fnames = g_fnames.union (set(fnames))

            fdict={}
            for ft in sample.features:
                fdict [ft.name.lstrip().rstrip().encode('ascii','replace')] = ft.freq
            sample_features [ sample.md5 ] = fdict
            if sample.malicious:
                sample_labels [sample.md5] = sample.cli_classification.gt
            else:
                sample_labels [sample.md5] = 'BENIGN'
        except (EOFError, pickle.UnpicklingError):
            break
    f.close()
    print >> sys.stderr, 'loaded from %s: %d feature vectors, %d labels, each sample having %d features' % (datatag, len (sample_features), len(sample_labels), len(g_fnames))
    #print sorted(g_fnames)
    return sample_features, sample_labels

def _regularizeFeatures(rawfeatures):
    ret={}
    for md5 in rawfeatures.keys():
        newfdict = copy.deepcopy(featureframe)
        for fname in rawfeatures[md5].keys():
            #assert fname in newfdict.keys()
            newfdict[fname] = rawfeatures[md5][fname]
        ret[md5] = newfdict
    return ret

def _getfvec(fdict):
    fvecs=dict()
    for md5 in fdict.keys():
        #print md5
        #fnames = [fname for fname in fdict[md5].keys()]
        fvalues = [freq for freq in fdict[md5].values()]
        #print len(fnames), len(fvalues)
        fvecs[md5] = fvalues
    return fvecs

def adapt (featureDict, labelDict):
    r=0
    c=None
    for app in featureDict.keys():
        r+=1
        if c==None:
            c = len (featureDict[app])
            print "feature vector length=%d" % (c)
            continue
        if c != len (featureDict[app]):
            print "inconsistent feature vector length for app: %s --- %d" % (app, len(featureDict[app]))
        assert c == len (featureDict[app])

    features = numpy.zeros( shape=(r,c) )
    labels = list()
    k=0
    for app in featureDict.keys():
        features[k] = featureDict[app]
        labels.append (labelDict[app])
        k+=1

    return (features, labels)

def resetframe():
    global featureframe
    featureframe={}
    for name in g_fnames:
        featureframe[name] = 0.0

def loadFeatures(datatag, label):
    _features, _labels  = _loadFeatures ( datatag )
    '''
    for md5 in _labels.keys():
        _labels[md5] = label
    '''

    return (_features, _labels)

if __name__=="__main__":
    if len(sys.argv)>=2:
        g_binary = sys.argv[1].lower()=='true'

    '''
    datasets = [ {"benign":["zoo-benign-2010"], "malware":["zoo-2010"]},
                  {"benign":["zoo-benign-2011"], "malware":["zoo-2011"]},
                  {"benign":["zoo-benign-2012"], "malware":["zoo-2012", "malware-2013"]},
                  {"benign":["zoo-benign-2013"], "malware":["zoo-2013", "vs-2013", "malware-drebin"]},
                  {"benign":["zoo-benign-2014", "benign-2014"], "malware":["zoo-2014", "vs-2014"]},
                  {"benign":["zoo-benign-2015"], "malware":["zoo-2015", "vs-2015"]},
                  {"benign":["zoo-benign-2016"], "malware":["zoo-2016", "vs-2016"]},
                  {"benign":["benign-2017"], "malware":["zoo-2017", "malware-2017"]} ]
    '''

    datasets = [  {"benign":["zoobenign2010"], "malware":["zoo2010"]},
                  {"benign":["zoobenign2011"], "malware":["zoo2011"]},
                  {"benign":["zoobenign2012"], "malware":["zoo2012"]},
                  {"benign":["zoobenign2013"], "malware":["vs2013"]},
                  {"benign":["zoobenign2014"], "malware":["vs2014"]},
                  {"benign":["zoobenign2015"], "malware":["vs2015"]},
                  {"benign":["zoobenign2016"], "malware":["vs2016"]},
                  {"benign":["benign2017"], "malware":["zoo2017","malware-2017-more"]},
                  #{"benign":["benign2017"], "malware":["zoo2017"]},
                ]

    '''
    datasets = [ \
                {"benign":["zoobenign2016", "benign2017"], "malware":["obfmg"]},
                {"benign":["zoobenign2015", "zoobenign2016"], "malware":["obfmg"]},
                {"benign":["zoobenign2013","zoobenign2014"], "malware":["obfmg"]},]
                #{"benign":["zoobenign2011","zoobenign2012"], "malware":["obfmg"]} ]

    datasets = [  {"benign":["zoo2011", "zoobenign2014","zoobenign2015", "zoobenign2016"], "malware":["zoo2010","zoo2011"]},
                  {"benign":["benign2017","zoobenign2014"], "malware":["vs2016","vs2015"]} ]

    datasets = [ \
                {"benign":["zoobenign2012", "zoobenign2013"], "malware":["obfmg"]},
                {"benign":["zoobenign2014", "zoobenign2015"], "malware":["obfmg"]},
                {"benign":["zoobenign2016", "benign2017"], "malware":["obfmg"]},
                ]
    datasets = [  \
                {"benign":["benign2017"], "malware":["zoo2017","malware-2017-more"]},
               ]
    '''

    #bPrune = g_binary
    bPrune = True

    fh = sys.stdout
    #fh = file ('confusion_matrix_formajorfamilyonly_holdout_all.txt', 'w')
    blacklist = []
    for app in file('/home/hcai/Downloads/AndroZoo/malware-2017/md5.non-malware-list.txt').readlines():
        blacklist.append (app.lstrip().rstrip())

    for i in range(7, len(datasets)):
        g_fnames=set()
        (bft, blt) = ({}, {})
        print "work on %s ... " % ( datasets[i] )
        for k in range(0, len(datasets[i]['benign'])):
            (bf, bl) = loadFeatures(datasets[i]['benign'][k], "BENIGN")
            if g_binary:
                bft.update (bf)
                blt.update (bl)
        for k in range(0, len(datasets[i]['malware'])):
            (mf, ml) = loadFeatures(datasets[i]['malware'][k], "MALICIOUS")
            for app in mf.keys():
                if app in blacklist:
                    del mf[app]
                    del ml[app]
            bft.update (mf)
            if g_binary:
                for md5 in ml.keys():
                    #print "%s\t%s" % (md5, ml[md5])
                    if ml[md5] != "BENIGN":
                        ml[md5] = "MALICIOUS"
            '''
            else:
                mfam = get_families ("../ML/md5families/"+datasets[i]['malware'][k]+".txt")
                newfam  = ml
                for a in ml.keys():
                    if a in mfam.keys():
                        newfam[a] = mfam[a]
                #print newfam
                blt.update ( newfam )
            '''
            blt.update (ml)

        resetframe()

        _bft = _regularizeFeatures ( bft )

        predict(_getfvec(_bft),blt, fh)

    fh.flush()
    fh.close()

    sys.exit(0)

# hcai: set ts=4 tw=120 sts=4 sw=4

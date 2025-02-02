# Import all classification package
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier, BaggingClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import precision_score,recall_score,f1_score,roc_auc_score,accuracy_score,auc,roc_curve

from sklearn.metrics import confusion_matrix

#from sklearn.mixture import GaussianMixture
#from sklearn.mixture import BayesianGaussianMixture
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import label_binarize

import matplotlib.pyplot as plt

import numpy as np
import random
import os
import sys
import string

import inspect, re
import pickle

from configs import *
from featureLoader_wdate import *

import numpy as np
import matplotlib.pyplot as plt

g_binary = False # binary or multiple-class classification

def plot_one(plt, fncurve, label_txt, **kwargs):
    f = open(fncurve, 'rb')

    try:
        (fpr, tpr, roc_auc) = pickle.load (f)
        #print fpr, tpr, roc_auc
        f.close()
    except (EOFError, pickle.UnpicklingError):
        print >> sys.stderr, "error loading data from %s " % fncurve
        return

    #plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve for %s (area = %0.4f)' % (fncurve, roc_auc))
    #plt.plot(fpr, tpr, lw=2, label='%s (RUC=%0.4f)' % (label_txt, roc_auc), **kwargs)
    plt.plot(fpr, tpr, lw=2, label='%s (%0.4f)' % (label_txt, roc_auc), **kwargs)

if __name__=="__main__":
    if len(sys.argv)>=2:
        g_binary = sys.argv[1].lower()=='true'

    plt.figure(figsize=(4,5))
    plt.rc('font', size=9)

    #print "categorization"
    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO_full.cat", 'D1617', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP_full.cat", 'D1415', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidcat_DRGP_full.cat", 'D1213', color='green', ls='dashdot')
    plot_one (plt, "roc_curves/pickle.droidcat_MGGP.cat", 'D0911', color='magenta', ls='dotted')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO.cat", 'D1617', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP.cat", 'D1415', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidcat_DRGP.cat", 'D1213', color='green', ls='dashdot')
    plot_one (plt, "roc_curves/pickle.droidcat_MGGP.cat", 'D0911', color='magenta', ls='dotted')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO.cat", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_ZOZO.cat", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_ZOZO.cat", 'DroidSieve', color='green', ls='dashdot')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP.cat", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_VSGP.cat", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_VSGP.cat", 'DroidSieve', color='green', ls='dashdot')
    '''

    plot_one (plt, "roc_curves/pickle.droidcat_PRZO.cat", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_PRZO.cat", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO.cat", 'DroidSieve', color='green', ls='dashdot')


    '''
    plot_one (plt, "roc_curves/pickle.droidcat_PRZO.cat")

    plot_one (plt, "roc_curves/pickle.afonso_PRZO.cat")
    plot_one (plt, "roc_curves/pickle.afonso_VSGP.cat")
    plot_one (plt, "roc_curves/pickle.afonso_ZOZO.cat")

    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO.cat")
    plot_one (plt, "roc_curves/pickle.droidsieve_VSGP.cat")
    plot_one (plt, "roc_curves/pickle.droidsieve_ZOZO.cat")
    '''

    #print "detection"
    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO_full.det", 'D1617', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP_full.det", 'D1415', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidcat_DRGP_full.det", 'D1213', color='green', ls='dashdot')
    plot_one (plt, "roc_curves/pickle.droidcat_MGGP_full.det", 'D0911', color='magenta', ls='dotted')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO.det", 'D1617', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP.det", 'D1415', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidcat_DRGP.det", 'D1213', color='green', ls='dashdot')
    plot_one (plt, "roc_curves/pickle.droidcat_MGGP.det", 'D0911', color='magenta', ls='dotted')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_ZOZO.det", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_ZOZO.det", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_ZOZO.det", 'DroidSieve', color='green', ls='dashdot')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_VSGP.det", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_VSGP.det", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_VSGP.det", 'DroidSieve', color='green', ls='dashdot')
    '''

    '''
    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1617.det", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1617.det", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1617.det", 'DroidSieve', color='green', ls='dashdot')

    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1415.det", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1415.det", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1415.det", 'DroidSieve', color='green', ls='dashdot')

    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1213.det", 'DroidCat', color='black', ls='solid')
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1213.det", 'Afonso', color='blue', ls='dashed')
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1213.det", 'DroidSieve', color='green', ls='dashdot')
    '''


    '''
    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1213.det")
    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1415.det")
    plot_one (plt, "roc_curves/pickle.droidcat_PRZO1617.det")
    '''

    '''
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1213.det")
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1415.det")
    plot_one (plt, "roc_curves/pickle.afonso_PRZO1617.det")
    plot_one (plt, "roc_curves/pickle.afonso_VSGP.det")
    plot_one (plt, "roc_curves/pickle.afonso_ZOZO.det")

    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1213.det")
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1415.det")
    plot_one (plt, "roc_curves/pickle.droidsieve_PRZO1617.det")
    plot_one (plt, "roc_curves/pickle.droidsieve_VSGP.det")
    plot_one (plt, "roc_curves/pickle.droidsieve_ZOZO.det")
    '''

    plt.plot([0, 1], [0, 1], color='red', lw=1, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    #plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.show()

    sys.exit(0)

# hcai: set ts=4 tw=120 sts=4 sw=4

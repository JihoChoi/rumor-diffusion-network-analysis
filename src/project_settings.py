import os
import sys
import csv
import math
import random
import datetime
import time
import re
import json
import pickle
import operator

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

import tweepy


# =========================
# Project Settings
# =========================

# Root Directory
# ROOT = '../'  # Suppose main() is called from ./src directory
ROOT = '../../'  # Suppose script is called from ./src/*/ directory
# ROOT = os.path.abspath(ROOT) + '/'
print("ROOT PATH:", ROOT)


# Detect Rumors in Microblog Posts Using Propagation Structure via Kernel Learning (ACL 2017)
'''
    Statistic               Twitter15       Twitter16
    # of users              276,663         173,487
    # of source tweets      1,490           818
    # of threads            331,612         204,820
    # of non-rumors         374             205
    # of false rumors       370             205
    # of true rumors        372             205
    # of unverified rumors  374             203
    Avg. time length/tree   1,337 Hours     848 Hours
    Avg. # of posts/tree    223             251
    Max # of posts/tree     1,768           2,765
    Min # of posts/tree     55              81
'''
# Dataset Information
'''
    - Twitter 15:
        - 1490 cascades {'true': 372, 'false': 370, 'non-rumor': 374, 'unverified': 374}

    - Twitter 16:
        - 0818 cascades {'true': 207, 'false': 205, 'non-rumor': 205, 'unverified': 201}
'''

# '''Available Datasets'''

# DATASET = 'twitter15/'
# DATASET = 'twitter16/'
DATASETS = ['twitter15/', 'twitter16/']
DATASET = DATASETS[1]


# Input (Raw) data path
DATA_PATH = ROOT + 'data/rumor_detection_acl2017/' + DATASET

# ====================
#   Input File Paths
# ====================

RAW_DATA_PATH = ROOT + 'data/rumor_detection_acl2017/' + DATASET
INTERIM_DATA_PATH = ROOT + 'data/interim/' + DATASET
# SOCIAL_DATA_PATH = ROOT + 'data/social/' + DATASET
PROCESSED_DATA_PATH = ROOT + 'data/processed/' + DATASET

# TODO
#   'data/social/' + DATASET
#   -> 'data/' + DATASET + 'social/'


# Output file path
OUT_PATH = ROOT + 'out/' + DATASET


# Result file path
# TODO

# =====================
#   Output File Paths
# =====================
PLOTS_OUT_PATH = ROOT + 'out/' + DATASET + 'plots/'


# Test data path (Sampled dataset)
SAMPLE_DATA_PATH = ROOT + 'temp/rumor_detection_acl2017/' + DATASET


# Cache results (temporal savings, pickles)
CACHE_PATH = ROOT + 'temp/cache/'

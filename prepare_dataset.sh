#!/bin/bash

# ===================
#
#   Prepare Dataset
#
# ===================

: '
--------------------------------------------------------------------------------------------------
    Jiho Choi (jihochoi@snu.ac.kr)
        - https://github.com/JihoChoi

    References
    * Detect Rumors in Microblog Posts Using Propagation Structure via Kernel Learning (ACL 2017)
    * Rumor Detection on Twitter with Tree-structured Recursive Neural Networks (ACL 2018)
        - Papers    : https://aclweb.org/anthology/papers/P/P17/P17-1066/
                    : https://aclweb.org/anthology/papers/P/P18/P18-1184/
        - Dataset   : https://www.dropbox.com/s/7ewzdrbelpmrnxu/rumdetect2017.zip?dl=0
--------------------------------------------------------------------------------------------------
'

if [ ! -d ./data/ ]
then
    echo 'CREATE ./data directory'
    mkdir ./data/
fi


# Remove Old Raw Input Directory
if [ -d ./data/rumor_detection_acl2017 ]
then
    echo 'REMOVE ./data/rumor_detection_acl2017 directory'
    rm -rf ./data/rumor_detection_acl2017
fi


echo "------------------"
echo "  START DOWNLOAD  "
echo "------------------"
wget -O ./data/rumdetect2017.zip https://www.dropbox.com/s/7ewzdrbelpmrnxu/rumdetect2017.zip\?dl\=1

echo "---------"
echo "  UNZIP  "
echo "---------"
unzip data/rumdetect2017.zip -d data/
rm data/rumdetect2017.zip

# Remove Duplicate Lines
# sort 760109079133990912.txt | uniq -d

echo "--------------------------"
echo "  REMOVE DUPLICATE LINES  "
echo "--------------------------"
cd ./src/data_preparation
python3 ./remove_duplicate_lines.py


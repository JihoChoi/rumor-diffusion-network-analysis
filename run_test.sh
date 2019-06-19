: '
--------------------------------------------------------------------------------------------------
    Jiho Choi (jihochoi@snu.ac.kr)
        - https://github.com/JihoChoi
--------------------------------------------------------------------------------------------------
'

cd ./src

: '
'

cd ./feature-extraction
python3 ./structural_feature_extraction.py
python3 ./temporal_feature_extraction.py
python3 ./social_feature_extraction.py
cd ..


cd ./classification
python3 ./aggregation.py
python3 ./classifications.py
cd ..


cd ..

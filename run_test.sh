: '
--------------------------------------------------------------------------------------------------
    Jiho Choi (jihochoi@snu.ac.kr)
        - https://github.com/JihoChoi
--------------------------------------------------------------------------------------------------
'

cd ./scripts





cd ./feature-extraction
python3 ./structural_feature_extraction.py
python3 ./temporal_feature_extraction.py
python3 ./social_feature_extraction.py
python3 ./structural_temporal_feature_extraction.py


# TODO struct_temp_feature

cd ..


cd ./classification
python3 ./aggregation.py
python3 ./classifications.py
cd ..


cd ..

import sys
sys.path.append('..')
from utils import *


def aggregate_feature_sets():
    # ------------------------
    # Load latest feature sets
    # ------------------------
    latest_feature_set_timestamp = {'structural': time.strftime('0'),
                                    'temporal': time.strftime('0'),
                                    'social': time.strftime('0'),
                                    'struct_temp': time.strftime('0')}

    for index, file in enumerate(os.listdir(OUT_PATH)):
        if file.endswith(".csv"):
            file_name = os.path.splitext(file)[0].split('_')

            if file.startswith("structural_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['structural']:
                    latest_feature_set_timestamp['structural'] = timestamp
            elif file.startswith("temporal_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['temporal']:
                    latest_feature_set_timestamp['temporal'] = timestamp
            elif file.startswith("social_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['social']:
                    latest_feature_set_timestamp['social'] = timestamp
            elif file.startswith("struct-temp_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['struct_temp']:
                    latest_feature_set_timestamp['struct_temp'] = timestamp

    print(latest_feature_set_timestamp)

    # -----------------
    # Load Feature Sets
    # -----------------

    # TODO Error Handling
    structural_features_path = OUT_PATH + 'structural_analysis_' + latest_feature_set_timestamp['structural'] + ".csv"
    structural_pd = pd.read_csv(structural_features_path)

    temporal_features_path = OUT_PATH + 'temporal_analysis_' + latest_feature_set_timestamp['temporal'] + ".csv"
    temporal_pd = pd.read_csv(temporal_features_path)

    social_features_path = OUT_PATH + 'social_analysis_' + latest_feature_set_timestamp['social'] + ".csv"
    social_pd = pd.read_csv(social_features_path)

    struct_temp_features_path = OUT_PATH + 'struct-temp_analysis_' + latest_feature_set_timestamp['struct_temp'] + ".csv"
    struct_temp_pd = pd.read_csv(struct_temp_features_path)


    # struct-temp_features_path = OUT_PATH + "struct-temp_analysis_20190605_143358.csv"
    # struct-temp_pd = pd.read_csv(struct-temp_features_path)

    # ------------------
    # Aggregate Features
    # ------------------
    combined_pd = pd.merge(structural_pd, temporal_pd, on=['tweet_id', 'label'])
    combined_pd = pd.merge(combined_pd, social_pd, on=['tweet_id', 'label'])
    combined_pd = pd.merge(combined_pd, struct_temp_pd, on=['tweet_id', 'label'])
    print(combined_pd.shape)

    # comb_pd = pd.merge(combined_pd, struct-temp_pd, on=['tweet_id', 'label'])
    # print(comb_pd.shape)

    #
    out_file = OUT_PATH + 'comb_dataset_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
    combined_pd.to_csv(out_file, sep=',', index=False)


def main():
    aggregate_feature_sets()


print("=============================")
print("     Feature Aggregation     ")
print("=============================")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

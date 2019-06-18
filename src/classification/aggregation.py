import sys
sys.path.append('..')
from util import *


def aggregate_feature_sets():
    # ------------------------
    # Load latest feature sets
    # ------------------------
    latest_feature_set_times = {'structural': time.strftime('0'), 'temporal': time.strftime('0'), 'social': time.strftime('0')}
    for index, file in enumerate(os.listdir(OUT_PATH)):
        if file.endswith(".csv"):
            file_name = os.path.splitext(file)[0].split('_')
            if file.startswith("structural_analysis_"):
                timestamp = file_name[2] + '_' +  file_name[3]
                if timestamp > latest_feature_set_times['structural']:
                    latest_feature_set_times['structural'] = timestamp
            if file.startswith("temporal_analysis_"):
                timestamp = file_name[2] + '_' +  file_name[3]
                if timestamp > latest_feature_set_times['temporal']:
                    latest_feature_set_times['temporal'] = timestamp
            if file.startswith("social_analysis_"):
                timestamp = file_name[2] + '_' +  file_name[3]
                if timestamp > latest_feature_set_times['social']:
                    latest_feature_set_times['social'] = timestamp

    print(latest_feature_set_times)

    structural_features_path = OUT_PATH + 'structural_analysis_' + latest_feature_set_times['structural'] + ".csv"
    temporal_features_path = OUT_PATH + 'temporal_analysis_' + latest_feature_set_times['temporal'] + ".csv"
    social_features_path = OUT_PATH + 'social_analysis_' + latest_feature_set_times['social'] + ".csv"
    # struct_temp_features_path = OUT_PATH + "struct_temp_analysis_20190605_143358.csv"

    struct_pd = pd.read_csv(structural_features_path)
    temp_pd = pd.read_csv(temporal_features_path)
    comb_pd = pd.merge(struct_pd, temp_pd, on=['tweet_id', 'label'])

    soc_pd = pd.read_csv(social_features_path)
    comb_pd = pd.merge(comb_pd, soc_pd, on=['tweet_id', 'label'])
    print(comb_pd.shape)

    # struct_temp_pd = pd.read_csv(struct_temp_features_path)
    # comb_pd = pd.merge(comb_pd, struct_temp_pd, on=['tweet_id', 'label'])
    # print(comb_pd.shape)

    out_file = OUT_PATH + 'comb_dataset_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
    comb_pd.to_csv(out_file, sep=',', index=False)


def main():
    aggregate_feature_sets()


print("=============================")
print("     Feature Aggregation     ")
print("=============================")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

import sys
sys.path.append('..')
from utils import *

from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn import ensemble
from sklearn.metrics import f1_score
import statistics as st
from xgboost import XGBClassifier

def aggregate_feature_sets():  # temporal + struct_temp
    # ------------------------
    # Load latest feature sets
    # ------------------------
    latest_feature_set_timestamp = {'temporal': time.strftime('0'),
                                    'struct_temp': time.strftime('0')}

    for index, file in enumerate(os.listdir(OUT_PATH)):
        if file.endswith(".csv"):
            file_name = os.path.splitext(file)[0].split('_')
            if file.startswith("temporal_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['temporal']:
                    latest_feature_set_timestamp['temporal'] = timestamp
            elif file.startswith("struct-temp_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['struct_temp']:
                    latest_feature_set_timestamp['struct_temp'] = timestamp
    print(latest_feature_set_timestamp)

    # -----------------
    # Load Feature Sets
    # -----------------
    temporal_features_path = OUT_PATH + 'temporal_analysis_' + latest_feature_set_timestamp['temporal'] + ".csv"
    temporal_pd = pd.read_csv(temporal_features_path)
    struct_temp_features_path = OUT_PATH + 'struct-temp_analysis_' + latest_feature_set_timestamp['struct_temp'] + ".csv"
    struct_temp_pd = pd.read_csv(struct_temp_features_path)

    # Aggregate Features
    # ------------------
    combined_pd = pd.merge(temporal_pd, struct_temp_pd, on=['tweet_id', 'label'])
    print(combined_pd.shape)
    out_file = OUT_PATH + 'comb-temporal_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
    combined_pd.to_csv(out_file, sep=',', index=False)


def test_classification_tasks():
    # ------------------------
    # Load latest feature sets
    # ------------------------
    latest_feature_set_timestamp = {'structural': time.strftime('0'),
                                    'comb-temporal': time.strftime('0'),
                                    'social': time.strftime('0')}

    for index, file in enumerate(os.listdir(OUT_PATH)):
        if file.endswith(".csv"):
            file_name = os.path.splitext(file)[0].split('_')
            if file.startswith("structural_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['structural']:
                    latest_feature_set_timestamp['structural'] = timestamp
            elif file.startswith("comb-temporal_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['comb-temporal']:
                    latest_feature_set_timestamp['comb-temporal'] = timestamp
            elif file.startswith("social_analysis_"):
                timestamp = file_name[2] + "_" + file_name[3]
                if timestamp > latest_feature_set_timestamp['social']:
                    latest_feature_set_timestamp['social'] = timestamp

    structural_features_path = OUT_PATH + 'structural_analysis_' + latest_feature_set_timestamp['structural'] + ".csv"
    structural_df = pd.read_csv(structural_features_path)

    temporal_features_path = OUT_PATH + 'comb-temporal_analysis_' + latest_feature_set_timestamp['comb-temporal'] + ".csv"
    temporal_df = pd.read_csv(temporal_features_path)

    social_features_path = OUT_PATH + 'social_analysis_' + latest_feature_set_timestamp['social'] + ".csv"
    social_df = pd.read_csv(social_features_path)

    feature_sets = {'structural': structural_df, 'temporal': temporal_df, 'social': social_df}
    classifiers = {'RF': ensemble.RandomForestClassifier(),
                   'XGB': XGBClassifier(),
                   'ADAB': ensemble.AdaBoostClassifier(),
                   'GRADB': ensemble.GradientBoostingClassifier()}

    for feature_set_name in feature_sets.keys():
        df = feature_sets[feature_set_name]
        df = df.fillna(0)
        X = df.drop(columns=['tweet_id', 'label'])
        y = df['label']

        print("===========================" * 3)
        print(feature_set_name)
        print("===========================" * 3)

        for classifier_name in list(classifiers.keys()):

            accuracy_results = []
            f1_macro_results = []
            f1_micro_results = []

            max_accuracy = 0

            for i in range(100):
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20)  # 5-fold cross validation

                clf = classifiers[classifier_name]
                clf.fit(X_train, y_train)

                y_pred = clf.predict(X_test)  # predictions

                accuracy = metrics.accuracy_score(y_test, y_pred)
                f1_macro = f1_score(y_test, y_pred, average='macro')
                f1_micro = f1_score(y_test, y_pred, average='micro')

                # print("#{}: Accuracy={} F1-macro={} F1-micro={}".format(i, accuracy, round(f1_macro, 4), round(f1_micro, 4)))
                accuracy_results.append(accuracy)
                f1_macro_results.append(f1_macro)
                f1_micro_results.append(f1_micro)

                if accuracy > max_accuracy:
                    max_accuracy = accuracy
                    feature_importances = pd.DataFrame(clf.feature_importances_, index=X_train.columns,
                                                       columns=['importance']).sort_values('importance', ascending=False)

            print('\n\n' + classifier_name)
            print('MEAN    \t STD\t MEDIAN')
            print('ACC     \t', round(st.mean(accuracy_results), 4), '+-', round(st.pstdev(accuracy_results), 4))
            print('F1-macro\t', round(st.mean(f1_macro_results), 4), '+-', round(st.pstdev(f1_macro_results), 4))
            print('F1-micro\t', round(st.mean(f1_micro_results), 4), '+-', round(st.pstdev(f1_micro_results), 4))
            print(max_accuracy)
            # print(feature_importances)
            print("==========================="*3)




def main():
    print("==============================================")
    print("     Feature Aggregation (Ablation Study)     ")
    print("==============================================")  # temp + sturct_temp -> comb-temp
    aggregate_feature_sets()

    print("========================")
    print("     Ablation Study     ")
    print("========================")
    test_classification_tasks()


if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time



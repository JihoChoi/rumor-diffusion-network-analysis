import sys
sys.path.append('..')
from utils import *

from sklearn.model_selection import train_test_split
# from sklearn import datasets
from sklearn import metrics
# from sklearn import linear_model
# from sklearn import tree
# from sklearn import svm
# from sklearn import multiclass
from sklearn import ensemble

# https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html
from sklearn.metrics import f1_score
import statistics as st
from xgboost import XGBClassifier


def test_classification_tasks():
    # ------------------------
    # Load latest feature sets
    # ------------------------
    latest_feature_set_time = time.strftime('0')
    for index, file in enumerate(os.listdir(OUT_PATH)):
        if file.startswith("comb_dataset_") and file.endswith(".csv"):
            file_name = os.path.splitext(file)[0].split('_')
            timestamp = file_name[2] + '_' + file_name[3]
            if timestamp > latest_feature_set_time:
                latest_feature_set_time = timestamp

    print(latest_feature_set_time)
#   features_path = OUT_PATH + 'comb_dataset_' + latest_feature_set_time + ".csv"
    features_path = OUT_PATH + 'structural_analysis_20190705_095032.csv'
    features_path = OUT_PATH + 'temporal_analysis_20190701_174001.csv'
    features_path = OUT_PATH + 'social_analysis_20190701_175006.csv'
    df = pd.read_csv(features_path, sep=',')
    # df = pd.read_csv(OUT_PATH + 'dataset_20190513_115505.csv', sep=',')

    # feature_set = ['structural', 'temporal', 'social']
    # label_set = ['true', 'false', 'unverified', 'non-rumor']

    # print(df.dtypes)
    df = df.fillna(0)

    # ----------------
    #   DROP COLUMNS
    # ----------------
    # if 'temporal___longest_length' in df:
    #     df = df.drop(columns=['temporal___longest_length'])
    # if 'temp_longest_length' in df:
    #     df = df.drop(columns=['temp_longest_length'])

    # ---------------------
    #   DROP ROWS (label)
    # ---------------------
    # df = df[df.label != 'unverified']
    # df = df[df.label != 'non-rumor']

    X = df.drop(columns=['tweet_id', 'label'])
    y = df['label']

    # print(df.shape, df['label'].value_counts().to_dict())
    # print(df.info())

    classifiers = {'RF': ensemble.RandomForestClassifier(),
                   'XGB': XGBClassifier(),
                   'ADAB': ensemble.AdaBoostClassifier(),
                   'GRADB': ensemble.GradientBoostingClassifier()}

    for classifier_name in list(classifiers.keys()):

        accuracy_results = []
        f1_macro_results = []
        f1_micro_results = []

        for i in range(10):
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

        print('\n\n' + classifier_name)
        print('MEAN    \t STD\t MEDIAN')
        print('ACC     \t', round(st.mean(accuracy_results), 4), '+-', round(st.pstdev(accuracy_results), 4))
        print('F1-macro\t', round(st.mean(f1_macro_results), 4), '+-', round(st.pstdev(f1_macro_results), 4))
        print('F1-micro\t', round(st.mean(f1_micro_results), 4), '+-', round(st.pstdev(f1_micro_results), 4))

        # print('\n\n' + str(list(df.columns)))
        feature_importances = pd.DataFrame(clf.feature_importances_, index=X_train.columns,
                                            columns=['importance']).sort_values('importance', ascending=False)

        print(feature_importances)
        print("==========================="*3)


def main():
    test_classification_tasks()


print("==============================")
print("     Rumor Classification     ")
print("==============================")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

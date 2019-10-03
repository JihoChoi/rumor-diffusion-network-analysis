import sys
sys.path.append('..')
from utils import *


class Cascade:

    # --------------------------
    #      Initiate Cascade
    # --------------------------
    def __init__(self, root_tweet_id, cascade_path, label=None):
        self.file_id = root_tweet_id
        self.root_tweet_id = root_tweet_id
        self.root_user_id = 0
        self.root_tweet_time = 0
        self.cascade_path = cascade_path
        self.label = label

        # ------------
        # Load Cascade
        # ------------
        self.load_cascade()
        # self.load_cascade(root_tweet_id, cascade_path)

    def load_cascade(self):
        G = nx.DiGraph()
        diffusion_time_from_src_list = []
        diffusion_time_from_root_list = []
        retweet_diff_time_from_src_list = []
        retweet_diff_time_from_root_list = []
        reply_diff_time_from_src_list = []
        reply_diff_time_from_root_list = []
        retweet_count = 0
        reply_count = 0

        with open(self.cascade_path, 'r') as file:
            # SET ROOT
            for index, line in enumerate(file):
                elem_list = [x.strip() for x in re.split(r"[\'\,\->\[\]]", line.strip()) if x.strip()]
                if elem_list[0] == 'ROOT' and elem_list[1] == 'ROOT':
                    self.root_user_id = elem_list[3]
                    self.root_tweet_time = float(elem_list[5])
                    if index != 0:
                        print('ROOT {} by {} @ line # {}'.format(elem_list[4], self.root_user_id, index))
                    break

            if self.root_tweet_id != elem_list[4]:  # cascade ID != root_tweet_id
                print('\t file_id:{1} -> root_tweet_id:{2} ({0}) '.format(self.label, self.root_tweet_id, elem_list[4]))
                self.root_tweet_id = elem_list[4]

            # Load Cascade

            for index, line in enumerate(file):  # Trace
                elem_list = re.split(r"[\'\,\->\[\]]", line.strip())
                elem_list = [x.strip() for x in elem_list if x.strip()]  # remove empty elements

                # Error data handling
                if float(elem_list[2]) >= float(elem_list[5]):
                    continue

                src_user_id, src_tweet_id, src_tweet_time, dst_user_id, dst_tweet_id, dst_tweet_time = elem_list
                diffusion_time_from_src = float(dst_tweet_time) - float(src_tweet_time)
                diffusion_time_from_root = float(src_tweet_time) - self.root_tweet_time

                diffusion_time_from_src_list.append(diffusion_time_from_src)
                diffusion_time_from_root_list.append(diffusion_time_from_root)
                if src_tweet_id == dst_tweet_id:  # Retweet
                    retweet_diff_time_from_src_list.append(diffusion_time_from_src)
                    retweet_diff_time_from_root_list.append(diffusion_time_from_root)
                    retweet_count += 1
                else:
                    reply_diff_time_from_src_list.append(diffusion_time_from_src)
                    reply_diff_time_from_root_list.append(diffusion_time_from_root)
                    reply_count += 1


        # TODO:
        #     Load method only do load
        #     Separate load with feature calculation (extraction)

        CascadeAnalyzer.feature_df = CascadeAnalyzer.feature_df.append({
            'tweet_id': self.root_tweet_id, 'label': self.label,
            'temporal___avg_diff_time_from_src': pd.Series(diffusion_time_from_src_list).mean(),
            'temporal___avg_diff_time_from_root': pd.Series(diffusion_time_from_root_list).mean(),
            'temporal___avg_retweet_time_from_src': pd.Series(retweet_diff_time_from_src_list).mean(),
            'temporal___avg_retweet_time_from_root': pd.Series(retweet_diff_time_from_root_list).mean(),
            'temporal___avg_reply_time_from_src': pd.Series(reply_diff_time_from_src_list).mean(),
            'temporal___avg_reply_time_from_root': pd.Series(reply_diff_time_from_root_list).mean(),
        }, ignore_index=True)


class CascadeAnalyzer(object):
    feature_df = pd.DataFrame()   # output

    def __init__(self):
        self.meta_df = pd.DataFrame()   # key: root_tweet_id
        self.cascades_dict = {}         # key: root_tweet_id, value: Graph
        self.retrieve_cascade_labels()
        self.load_cascades()

    def retrieve_cascade_labels(self):
        column_names = ['label', 'tweet_id']
        labels_df = pd.read_csv(DATA_PATH + "label.txt", sep=':', names=column_names, converters={'tweet_id': str})
        print("==================")
        print(labels_df.info())
        print("==================")
        # labels_df = labels_df.sort_values(['label'], ascending=True)
        print(labels_df.shape, labels_df['label'].value_counts().to_dict())
        print(labels_df.head())
        self.meta_df = labels_df

    # TODO: @staticmethod
    def find_label(self, root_tweet_id):
        # TODO change tweet_id type
        return self.meta_df.loc[self.meta_df['tweet_id'] == root_tweet_id, 'label'].item()

    def load_cascades(self):
        # Iterate tweet trees
        for index, file in enumerate(os.listdir(DATA_PATH + 'tree_u')):
            if not file.endswith('.txt'):
                print("Unexpected Input File:", file)
                continue
            root_tweet_id = file.replace('.txt', '')
            cascade_path = os.path.join(DATA_PATH + 'tree_u', file)
            label = self.find_label(root_tweet_id)
            # label = self.meta_df.loc[self.meta_df['tweet_id'] == root_tweet_id, 'label'].item()
            self.cascades_dict[root_tweet_id] = Cascade(root_tweet_id, cascade_path, label)

    def cascade_to_csv(self):  # CascadeAnalyzer
        out_file_name = OUT_PATH + 'temporal_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
        out_file = open(out_file_name, 'w', encoding='utf-8', newline='')
        self.feature_df.to_csv(out_file, sep=',', index=False)


def main():
    analyzer = CascadeAnalyzer()
    analyzer.cascade_to_csv()


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
print("=====================================")
print("     Temporal Feature Extraction     ")
print("=====================================")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

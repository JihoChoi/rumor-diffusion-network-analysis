import sys
sys.path.append('..')
from utils import *

# from project_settings import *


class Cascade:

    # Class Variables
    # root_tweet_count = 0
    # --------------------------
    #      Initiate Cascade
    # --------------------------
    def __init__(self, root_tweet_id, cascade_path, label=None):
        self.file_id = root_tweet_id        # For label.txt
        self.root_tweet_id = root_tweet_id  # Tweet ID with ROOT Keyword (May updated)
        self.cascade_path = cascade_path
        self.label = label
        self.root_user_id = 0
        self.network = nx.DiGraph()
        self.load_cascade()

    def load_cascade(self):
        with open(self.cascade_path, 'r') as file:
            # ---------------------
            # Set Root: User, Tweet
            # ---------------------
            for index, line in enumerate(file):
                elem_list = [x.strip() for x in re.split(r"[\'\,\->\[\]]", line.strip()) if x.strip()]
                if elem_list[0] == 'ROOT' and elem_list[1] == 'ROOT':
                    self.root_user_id = elem_list[3]
                    if index != 0:
                        print('ROOT TWEET {} by {} @ line # {}'.format(elem_list[4], self.root_user_id, index))
                    break

            if self.root_tweet_id != elem_list[4]:  # Assert file_id == root_tweet_id
                print('\t file_id:{1} -> root_tweet_id:{2} ({0}) '.format(self.label, self.root_tweet_id, elem_list[4]))
                self.root_tweet_id = elem_list[4]

            # ------------
            # Load Cascade
            # ------------
            for index, line in enumerate(file):  # Trace
                elem_list = re.split(r"[\'\,\->\[\]]", line.strip())
                elem_list = [x.strip() for x in elem_list if x.strip()]  # Remove empty elements

                # Error data handling
                if float(elem_list[2]) >= float(elem_list[5]):
                    continue

                src_user_id, src_tweet_id, src_tweet_time, dst_user_id, dst_tweet_id, dst_tweet_time = elem_list

                # NetworkX Graph
                self.network.add_weighted_edges_from(
                    [(src_user_id, dst_user_id, float(dst_tweet_time) - float(src_tweet_time))]
                )

    # =============================
    #      Hop - Time Analysis
    # =============================
    def calc_structural_features(self):
        G = self.network

        one_hop_diff_times = []
        two_hop_diff_times = []
        for one_hop_node in G.neighbors(self.root_user_id):
            one_hop_diff_times.append(G.get_edge_data(self.root_user_id, one_hop_node)['weight'])

            for two_hop_node in G.neighbors(one_hop_node):
                if two_hop_node == self.root_user_id:
                    continue
                two_hop_diff_times.append(G.get_edge_data(one_hop_node, two_hop_node)['weight'])

        # features to data frame
        CascadeAnalyzer.feature_df = CascadeAnalyzer.feature_df.append({
                'tweet_id': self.root_tweet_id, 'label': self.label,
                'struct_temp_1_hop_neighbor_mean_time': mean_of_list(one_hop_diff_times),
                'struct_temp_1_hop_neighbor_max_time': max_of_list(one_hop_diff_times),
                'struct_temp_1_hop_neighbor_median_time': median_of_list(one_hop_diff_times),
                'struct_temp_2_hop_neighbor_mean_time': mean_of_list(one_hop_diff_times),
                'struct_temp_2_hop_neighbor_max_time': max_of_list(one_hop_diff_times),
                'struct_temp_2_hop_neighbor_median_time': median_of_list(two_hop_diff_times),
            }, ignore_index=True)


class CascadeAnalyzer(object):
    feature_df = pd.DataFrame()   # output

    def __init__(self):
        self.meta_df = pd.DataFrame()   # labels / key: root_tweet_id
        self.cascades_dict = {}         # key: root_tweet_id, value: Cascade()
        self.retrieve_cascade_labels()
        self.load_cascades()

    def retrieve_cascade_labels(self):
        column_names = ['label', 'tweet_id']
        labels_df = pd.read_csv(DATA_PATH + "label.txt", sep=':', names=column_names, converters={'tweet_id': str})
        print("-------------------------------------")
        print(labels_df.info())
        print("-------------------------------------" * 2)
        print(labels_df.shape, labels_df['label'].value_counts().to_dict())
        print("-------------------------------------" * 2)
        print(labels_df.head())
        print("-------------------------------------\n")

        # labels_df = labels_df.sort_values(['label'], ascending=True)
        # labels_df = labels_df.sort_values(['tweet_id'], ascending=True)
        self.meta_df = labels_df

    # TODO: handle pickle data
    def load_cascades(self):
        # iterate tweet trees
        for index, file in enumerate(os.listdir(DATA_PATH + 'tree_u')):
            if not file.endswith('.txt'):
                print("Unexpected Input File:", file)
                continue

            root_tweet_id = file.replace('.txt', '')  # file_id
            cascade_path = os.path.join(DATA_PATH + 'tree_u', file)

            label = self.meta_df.loc[self.meta_df['tweet_id'] == root_tweet_id, 'label'].item()  # find label
            self.cascades_dict[root_tweet_id] = Cascade(root_tweet_id, cascade_path, label)

    # Main Outer loop
    def iterate_cascades(self):
        for index, row in self.meta_df.iterrows():
            tweet_id = row['tweet_id']
            cascade = self.cascades_dict[tweet_id]

            print('#', index, row['tweet_id'], row['label'])
            cascade.calc_structural_features()

    def cascade_to_csv(self):  # CascadeAnalyzer
        # File Out dataframe to csv
        out_file_name = OUT_PATH + 'struct-temp_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
        out_file = open(out_file_name, 'w', encoding='utf-8', newline='')
        self.feature_df.to_csv(out_file, sep=',', index=False)


def main():
    # CascadeAnalyzer -> Overall / Cascade -> Individual
    analyzer = CascadeAnalyzer()
    analyzer.iterate_cascades()
    analyzer.cascade_to_csv()


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids

print("==========================")
print("     Cascade Analysis     ")
print("==========================\n\n")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("\nElapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

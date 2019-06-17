# import sys
# sys.path.append('..')
from util import *


class Cascade:

    # --------------------------
    #      Initiate Cascade
    # --------------------------
    def __init__(self, root_tweet_id, cascade_path, label=None):
        self.file_id = root_tweet_id  # For label.txt
        self.root_tweet_id = root_tweet_id  # Tweet ID with ROOT Keyword (May updated)
        self.root_user_id = 0
        self.cascade_path = cascade_path
        self.label = label

        # ------------
        # Load Cascade
        # ------------
        self.trace_count = None
        self.src_users = set()
        self.dst_users = set()
        self.retweet_users = set()
        self.reply_users = set()
        self.retweet_count = 0
        self.reply_count = 0
        self.network = nx.DiGraph()
        self.network_features = {}
        self.load_cascade()

        # -----------------
        # Calculate Cascade
        # -----------------
        self.src_user_count = None
        self.dst_user_count = None
        self.avg_depth = 0
        self.max_depth = 0

    def load_cascade(self):
        with open(self.cascade_path, 'r') as file:
            # ---- -----------------
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
                self.src_users.add(src_user_id)
                self.dst_users.add(dst_user_id)
                # Different types of Tweets - https://help.twitter.com/en/using-twitter/types-of-tweets
                if src_tweet_id == dst_tweet_id:
                    self.retweet_count += 1
                    self.retweet_users.add(dst_user_id)
                else:
                    self.reply_count += 1
                    self.reply_users.add(dst_user_id)
                # NetworkX Graph
                self.network.add_weighted_edges_from(
                    [(src_user_id, dst_user_id, float(dst_tweet_time) - float(src_tweet_time))])
        # Store computed cascade information
        self.trace_count = index

    # =============================
    #      Structural Analysis
    # =============================
    def calc_structural_features(self):
        G = self.network
        # root_user_id = self.root_user_id
        self.src_user_count = len(self.src_users)
        self.dst_user_count = len(self.dst_users)
        hops = []
        max_hop_count = 10
        for i in range(max_hop_count):
            hops.append(len(nx.single_source_shortest_path_length(G, self.root_user_id, cutoff=i)))

        # print(self.retweet_count, self.response_count)
        # print("leaf:", nx.dag_to_branching(G))
        # print('\t root_to_all_depth_length: ', len(nx.single_source_shortest_path_length(G, self.root_user_id)))
        # print('\t user_count:', len(G.nodes()))  # root + dst_user_count
        print('\t depth: ', nx.dag_longest_path(G))  # weight - temporal feature
        print('\t src_user_count: ', self.src_user_count)
        print('\t dst_user_count: ', self.dst_user_count)
        print('\t root_to_all_depth_sum: ', sum(nx.single_source_shortest_path_length(G, self.root_user_id).values()))
        print('\t root_to_all_depth_max: ', max(nx.single_source_shortest_path_length(G, self.root_user_id).values()))
        print('\t one_hop_neighbors:', len(list(G.neighbors(self.root_user_id))))
        print('\t', "user count by hop(s): ", hops[1] - hops[0], hops[2] - hops[1], hops[3] - hops[2],
                                              hops[4] - hops[3], hops[5] - hops[4], hops[6] - hops[5],
                                              hops[7] - hops[6], hops[8] - hops[7], hops[9] - hops[8])

        # df.loc[df['tweet_id'] == root_tweet_id, 'src_user_count'] = len(src_users)
        shortest_path_dict = nx.single_source_shortest_path_length(G, self.root_user_id)
        self.avg_depth = sum(shortest_path_dict.values()) / len(shortest_path_dict)
        self.max_depth = max(shortest_path_dict.values())

        for i in range(max_hop_count - 1):
            self.network_features[str(i) + "_hop_neighbor_count"] = hops[i + 1] - hops[i]

        # features to data frame
        CascadeAnalyzer.feature_df = CascadeAnalyzer.feature_df.append({
            'tweet_id': self.root_tweet_id, 'label': self.label,
            'structural_trace_count': self.trace_count,
            'structural_retweet_count': self.retweet_count,
            'structural_reply_count': self.reply_count,
            'structural_src_user_count': self.src_user_count,
            'structural_dst_user_count': self.dst_user_count,
            'structural_retweet_reply_percent': self.retweet_count / (self.retweet_count + self.reply_count),
            'structural_src_dst_user_percent': self.src_user_count / (self.src_user_count + self.dst_user_count),  # <--
            'structural_retweet_users_count': len(self.retweet_users),
            'structural_reply_users_count': len(self.reply_users),
            'structural_root_to_all_depth_sum': sum(nx.single_source_shortest_path_length(G, self.root_user_id).values()),
            'structural_root_to_all_depth_max': max(nx.single_source_shortest_path_length(G, self.root_user_id).values()),
            'structural_1_hop_neighbor_count': self.network_features['1_hop_neighbor_count'],
            'structural_2_hop_neighbor_count': self.network_features['2_hop_neighbor_count'],
            'structural_3_hop_neighbor_count': self.network_features['3_hop_neighbor_count'],
            'structural_4_hop_neighbor_count': self.network_features['4_hop_neighbor_count'],
            'structural_5_hop_neighbor_count': self.network_features['5_hop_neighbor_count'],
            'structural_6_hop_neighbor_count': self.network_features['6_hop_neighbor_count'],
            'structural_7_hop_neighbor_count': self.network_features['7_hop_neighbor_count'],
            'structural_8_hop_neighbor_count': self.network_features['8_hop_neighbor_count'],
            'structural_avg_depth': self.avg_depth,
            'structural_max_depth': self.max_depth
        }, ignore_index=True)


# TODO: Class Inheritance
class CascadeAnalyzer(object):
    feature_df = pd.DataFrame()  # output

    def __init__(self):
        self.meta_df = pd.DataFrame()  # labels / key: root_tweet_id
        self.cascades_dict = {}  # key: root_tweet_id, value: Cascade()
        self.retrieve_cascade_labels()
        self.load_cascades()

    def retrieve_cascade_labels(self):
        column_names = ['label', 'tweet_id']
        self.meta_df = pd.read_csv(DATA_PATH + "label.txt", sep=':', names=column_names, converters={'tweet_id': str})
        print("-------------------------------------")
        print(self.meta_df.info())
        print("-------------------------------------" * 2)
        print(self.meta_df.shape, self.meta_df['label'].value_counts().to_dict())
        print("-------------------------------------" * 2)
        print(self.meta_df.head())
        print("-------------------------------------\n")

    def load_cascades(self):
        # TODO: handle pickle data
        # iterate tweet trees
        for index, file in enumerate(os.listdir(DATA_PATH + 'tree_u')):
            if not file.endswith('.txt'):
                print("Unexpected Input File:", file)
                continue
            root_tweet_id = file.replace('.txt', '')  # file_id
            cascade_path = os.path.join(DATA_PATH + 'tree_u', file)
            label = self.meta_df.loc[self.meta_df['tweet_id'] == root_tweet_id, 'label'].item()  # label
            self.cascades_dict[root_tweet_id] = Cascade(root_tweet_id, cascade_path, label)

    # Main Outer loop
    def iterate_cascades(self):
        for index, row in self.meta_df.iterrows():
            tweet_id = row['tweet_id']
            cascade = self.cascades_dict[tweet_id]
            print('#', index, row['tweet_id'], row['label'])
            cascade.calc_structural_features()

    def cascade_to_csv(self):  # CascadeAnalyzer
        ensure_directory(OUT_PATH)
        out_file_name = OUT_PATH + 'structural_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
        out_file = open(out_file_name, 'w', encoding='utf-8', newline='')
        self.feature_df.to_csv(out_file, sep=',', index=False)


def main():
    # CascadeAnalyzer -> Overall / Cascade -> Individual
    analyzer = CascadeAnalyzer()
    analyzer.iterate_cascades()
    analyzer.cascade_to_csv()


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
print("=============================")
print("     Structural Analysis     ")
print("=============================\n\n")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("\nElapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

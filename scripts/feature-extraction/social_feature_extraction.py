import sys
sys.path.append('..')
from utils import *


class Cascade:

    # --------------------------
    #      Initiate Cascade
    # --------------------------
    total_user_not_found_counter = 0
    total_user_found_counter = 0

    def __init__(self, root_tweet_id, cascade_path, label=None):
        self.file_id = root_tweet_id
        self.root_tweet_id = root_tweet_id
        self.root_user_id = 0
        self.cascade_path = cascade_path
        self.label = label
        self.user_not_found_counter = 0
        self.user_found_counter = 0

        self.delta_followers_count_list = []
        self.delta_friends_count_list = []
        self.delta_followers_count_up_count = 0
        self.delta_followers_count_down_count = 0
        self.delta_followers_count_equal_count = 0

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

        self.src_users = set()
        self.dst_users = set()
        self.retweet_users = set()
        self.reply_users = set()
        self.retweet_count = 0
        self.reply_count = 0

    def load_cascade(self):
        with open(self.cascade_path, 'r') as file:
            # Set Root User, Tweet
            for index, line in enumerate(file):
                elem_list = [x.strip() for x in re.split(r"[\'\,\->\[\]]", line.strip()) if x.strip()]
                if elem_list[0] == 'ROOT' and elem_list[1] == 'ROOT':
                    self.root_user_id = elem_list[3]
                    if index != 0:
                        print('ROOT TWEET {} by {} @ line # {}'.format(elem_list[4], self.root_user_id, index))
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

                self.src_users.add(src_user_id)
                self.dst_users.add(dst_user_id)

                # Different types of Tweets
                if src_tweet_id == dst_tweet_id:
                    self.retweet_count += 1
                    self.retweet_users.add(dst_user_id)
                else:
                    self.reply_count += 1
                    self.reply_users.add(dst_user_id)

                # TODO: Move to Social Calculation
                try:
                    src_user = Cascade.get_user_info(self.file_id, src_user_id)
                    dst_user = Cascade.get_user_info(self.file_id, dst_user_id)
                    delta_followers_count = dst_user.followers_count - src_user.followers_count
                    if delta_followers_count > 0:
                        self.delta_followers_count_up_count += 1
                    elif delta_followers_count < 0:
                        self.delta_followers_count_down_count += 1
                    else:
                        self.delta_followers_count_equal_count += 1

                    delta_friends_count = dst_user.friends_count - src_user.friends_count
                    self.delta_followers_count_list.append(delta_followers_count)
                    self.delta_friends_count_list.append(delta_friends_count)
                except FileNotFoundError as e:
                    pass
                except EOFError as e:  # Empty File
                    # print(self.file_id, src_user_id, dst_user_id)
                    pass

                # NetworkX Graph
                self.network.add_weighted_edges_from([(src_user_id, dst_user_id, float(dst_tweet_time) - float(src_tweet_time))])


        # Store computed cascade information
        self.trace_count = index
        # print(self.root_tweet_id, self.cascade_path)
        # print(index, self.src_user_count, self.dst_user_count)

    # ==============================
    #      Social Info Analysis
    # ==============================

    @staticmethod
    def get_user_info(root_tweet_id, user_id):
        pickle_file = open(INTERIM_DATA_PATH + 'user_info/' + root_tweet_id + '/' + user_id + '.pkl', 'rb')
        user = pickle.load(pickle_file)
        return user

    def calc_social_features(self):
        G = self.network
        follower_count_list = []
        friend_count_list = []
        listed_count_list = []
        favourites_count_list = []
        statuses_count_list = []
        is_verified_list = []

        for node in G.nodes():
            try:
                # user = Cascade.get_user_info(self.root_tweet_id, node)
                user = Cascade.get_user_info(self.file_id, node)
                self.user_found_counter += 1
                Cascade.total_user_found_counter += 1
                follower_count_list.append(user.followers_count)
                friend_count_list.append(user.friends_count)

                # Behavior
                listed_count_list.append(user.listed_count)
                favourites_count_list.append(user.favourites_count)
                statuses_count_list.append(user.statuses_count)
                is_verified_list.append(user.verified)

            except Exception as e:
                self.user_not_found_counter += 1
                Cascade.total_user_not_found_counter += 1

        avg_follower_count, max_follower_count = mean_max_of_list(follower_count_list)
        avg_friend_count, max_friend_count = mean_max_of_list(friend_count_list)
        avg_listed_count, max_listed_count = mean_max_of_list(listed_count_list)

        avg_favourites_count, max_favourites_count = mean_max_of_list(favourites_count_list)
        avg_statuses_count, max_statuses_count = mean_max_of_list(statuses_count_list)
        verified_user_percent = is_verified_list.count(True) / (is_verified_list.count(True) + is_verified_list.count(False))

        avg_delta_followers_count, max_delta_followers_count = mean_max_of_list(self.delta_followers_count_list)
        avg_delta_friends_count, max_delta_friends_count = mean_max_of_list(self.delta_friends_count_list)

        print("-----------" * 4) if not self.user_not_found_counter else 0
        print("\tUser not found: {} / {} = {:3.2}".format(self.user_not_found_counter,
                                                          self.user_not_found_counter + self.user_found_counter,
                                                          self.user_not_found_counter / (self.user_not_found_counter + self.user_found_counter)))
        print('\tFollower Max:{:10}, Avg:{}'.format(max_follower_count, avg_follower_count))
        print('\tFriend   Max:{:10}, Avg:{}'.format(max_friend_count, avg_friend_count))

        # TODO : Activation node count
        # features to data frame
        CascadeAnalyzer.feature_df = CascadeAnalyzer.feature_df.append({
            'tweet_id': self.root_tweet_id, 'label': self.label,  # Key
            'social_____max_follower': max_follower_count,
            'social_____avg_follower': avg_follower_count,
            'social_____max_friend': max_friend_count,
            'social_____avg_friend': avg_friend_count,
            'social_____max_listed': max_listed_count,
            'social_____avg_listed': avg_listed_count,
            'social_____max_favourites': max_favourites_count,  # favorites
            'social_____avg_favourites': avg_favourites_count,
            'social_____max_statuses': max_statuses_count,
            'social_____avg_statuses': avg_statuses_count,
            'social_____verified_percent': verified_user_percent,
            'social_____max_delta_follower': max_delta_followers_count,
            'social_____avg_delta_follower': avg_delta_followers_count,
            'social_____max_delta_friend': max_delta_friends_count,
            'social_____avg_delta_friend': avg_delta_friends_count,
            'social_____delta_followers_count_up': self.delta_followers_count_up_count,
            'social_____delta_followers_count_down': self.delta_followers_count_down_count,
            'social_____delta_followers_count_else': self.delta_followers_count_equal_count,
            'social_____delta_followers_count_up_percent': self.delta_followers_count_up_count / (
                        self.delta_followers_count_up_count + self.delta_followers_count_down_count + self.delta_followers_count_equal_count),
        }, ignore_index=True)

        # print(CascadeAnalyzer.feature_df.tail(1))


class CascadeAnalyzer(object):
    # meta_df = None  # metadata for trees

    feature_df = pd.DataFrame()  # output

    def __init__(self):
        self.meta_df = pd.DataFrame()  # labels / key: root_tweet_id
        self.cascades_dict = {}  # key: root_tweet_id, value: Cascade()
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

    def load_cascades(self):
        # TODO: handle pickle data
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
            # cascade.calc_structural_features()
            cascade.calc_social_features()

        print("Total not_found:{}, found:{}, {} not_found".format(
            Cascade.total_user_not_found_counter, Cascade.total_user_found_counter,
            Cascade.total_user_not_found_counter / (Cascade.total_user_found_counter + Cascade.total_user_not_found_counter)))

    def cascade_to_csv(self):  # CascadeAnalyzer
        out_file_name = OUT_PATH + 'social_analysis_' + time.strftime("%Y%m%d_%H%M%S") + ".csv"
        out_file = open(out_file_name, 'w', encoding='utf-8', newline='')

        self.feature_df.to_csv(out_file, sep=',', index=False)

    # Iterate root tweets (Retrieve metadata)

    # TODO:
    '''
    def graph_info_to_dataframe(self):

        df = self.meta_df
        cascade_dict = self.cascades_dict

        for index, row in df.iterrows():
            tweet_id = row['tweet_id']
            G = cascade_dict[tweet_id].network
            print(tweet_id, row['label'], len(G.nodes()), len(G.edges()))
            # print(tweet_id, row['label'], len(G.nodes()))
            if index == 10:
                break
        self.meta_df = df
    '''


def main():
    # CascadeAnalyzer -> Overall / Cascade -> Individual
    # print(os.getcwd())
    analyzer = CascadeAnalyzer()
    analyzer.iterate_cascades()
    analyzer.cascade_to_csv()


# Rumor Diffusion Analysis Project

# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids

print("===================================")
print("     Social Feature Extraction     ")
print("===================================\n\n")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("\nElapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

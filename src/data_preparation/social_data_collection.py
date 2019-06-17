from util import *

"""
Social Information Collector using Twitter API
"""


# User Profile Collection
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup


# ==========================
#      InputDataBuilder
# ==========================
class InputDataBuilder:
    def __init__(self):
        self.stat = {}  # statistics: stat[tweet_id] = (src_count, dst_count)
        self.root_users = set()
        self.all_src_users = set()
        self.all_dst_users = set()
        self.all_users = set()  # aggregated

    # @staticmethod
    def prepare_user_id_list(self, root_tweet_id):
        cascade_path = os.path.join(RAW_DATA_PATH + 'tree_u', root_tweet_id + '.txt')
        # print("PATH: ", cascade_path)
        src_users = set()
        dst_users = set()
        with open(cascade_path, 'r') as file:
            line = next(file)  # To handle ['ROOT', 'ROOT', '0.0']
            elem_list = [x.strip() for x in re.split(r"[\'\,\->\[\]]", line.strip()) if x.strip()]
            root_user_id = elem_list[3]
            src_users.add(root_user_id)
            self.root_users.add(root_user_id)
            for index, line in enumerate(file):
                # ex. ['918346674', '779633844680962048', '0.0']->['2885555216', '779634034859249666', '0.75']
                elem_list = re.split(r"[\'\,\->\[\]]", line.strip())
                elem_list = [x.strip() for x in elem_list if x.strip()]  # remove empty elements
                if float(elem_list[2]) < float(elem_list[5]):
                    src_users.add(elem_list[0])
                    dst_users.add(elem_list[3])
            all_users = src_users | dst_users
            self.all_src_users.update(src_users)
            self.all_dst_users.update(dst_users)
            self.all_users.update(all_users)
            # print('\t', len(src_users), len(dst_users), len(all_users))
            print('\t', len(src_users), len(dst_users), len(all_users))
            self.stat[root_tweet_id] = (src_users, dst_users, all_users)

        # Out Text / Pickle Files
        ensure_directory(INTERIM_DATA_PATH + 'user_set/')
        out_txt_file = open(INTERIM_DATA_PATH + 'user_set/' + root_tweet_id + '.txt', 'w')
        out_txt_file.write(str(all_users))
        out_pickle_file = open(INTERIM_DATA_PATH + 'user_set/' + root_tweet_id + '.pkl', 'wb')
        pickle.dump(all_users, out_pickle_file)

    # load_tweets
    def iterate_tweet_trees(self):
        root_tweet_id_list = []
        for index, file in enumerate(os.listdir(RAW_DATA_PATH + 'tree_u')):
            root_tweet_id = file.replace('.txt', '')
            root_tweet_id_list.append(root_tweet_id)

        # TEMP
        # root_tweet_id_list = ['656834590779289600']  # 5 135 136
        for index, root_tweet_id in enumerate(root_tweet_id_list):
            # print("Tweet ID: ", root_tweet_id)
            print("Tweet ID: ", root_tweet_id, end=' ')
            self.prepare_user_id_list(root_tweet_id)

        print(len(self.root_users), len(self.all_src_users), len(self.all_dst_users), len(self.all_users))
        print(len(self.stat))


# =============================
#      SocialInfoCollector
# =============================

# Twitter API:
#   - GET users/lookup:
#   https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
#   - User Object: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object
# Tweepy:
#   - https://tweepy.readthedocs.io/en/v3.5.0/api.html#user-methods

class SocialInfoCollector():
    def __init__(self, name=None):
        self.name = name
        self.load_settings()
        self.api = None
        self.connect_twitter_api()
        self.request_count = 0
        self.config = None
        self.keys = None

    # Hard coded settings - config, API keys
    def load_settings(self):
        try:
            self.config = json.load(open(ROOT + "settings/config.json"))
            self.keys = json.load(open(ROOT + "settings/keys.json"))
        except IOError:
            print("Error - Loading Settings")
            raise

    def connect_twitter_api(self):
        auth = tweepy.OAuthHandler(self.keys['api_key'], self.keys['api_secret_key'])
        auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])
        self.api = tweepy.API(auth)

    def get_user_info_api(self, root_tweet_id):
        # Input File Path / Output Directory Path
        # user_set_path = os.path.join(INTERIM_DATA_PATH + 'user_set', root_tweet_id + '.txt')

        # Input
        pickle_file = open(INTERIM_DATA_PATH + 'user_set/' + root_tweet_id + '.pkl', 'rb')
        id_list = list(pickle.load(pickle_file))

        # Output
        user_info_dir = INTERIM_DATA_PATH + 'user_info/' + root_tweet_id + '/'
        ensure_directory(user_info_dir)

        out_txt_file = open(user_info_dir + '_info.txt', 'w')
        out_txt_file.write(str(id_list))

        n = 100  # batch size
        batch_id_list = [id_list[i * n:(i + 1) * n] for i in range((len(id_list) + n - 1) // n)]

        num_request_required = len(batch_id_list)
        for index, id_list in enumerate(batch_id_list):

            try:
                users_list = self.api.lookup_users(user_ids=id_list)
                self.request_count += 1

            except tweepy.error.TweepError:  # TODO: No user found
                print("\n\n")
                print("Tweepy has hit its rate limit (" + time.strftime("%Y%m%d-%H%M%S") + ")")
                time.sleep(60 * 15)  # Wait for 15 minutes
                users_list = self.api.lookup_users(user_ids=id_list)  # redo

            print("\n==================================================")
            print("REQUEST_COUNT:{} {}/{}, len={}".format(
                self.request_count, index, num_request_required, len(users_list)))
            print(id_list)
            print("--------------------------------------------------\n")

            for user in users_list:
                # print(dir(user))
                print(user.screen_name, user.id, end=' ')
                # print(user._json)

                # Out Text / Pickle Files
                out_txt_file = open(user_info_dir + str(user.id) + '.txt', 'w')
                out_txt_file.write(str(user))
                out_pickle_file = open(user_info_dir + str(user.id) + '.pkl', 'wb')
                pickle.dump(user, out_pickle_file)

    def iterate_user_sets(self):
        root_tweet_id_list = []
        for index, file in enumerate(os.listdir(INTERIM_DATA_PATH + 'user_set')):
            if file.endswith('.txt'):
                root_tweet_id = file.replace('.txt', '')
                root_tweet_id_list.append(root_tweet_id)

        # TEMP
        # root_tweet_id_list = ['767462297270968321', '775672628493357057', '524646141938647043', '523026678419714048', '510908595144519680', '532276693931945984', '514148279601606656', '516395112201736192', '553008832784642048', '693855615618322432', '407205404075376640', '407262953533353984', '356310469390245888', '407159686786732032', '516411927506206721', '407209892013821952', '692854695262445568', '537976883150077952', '524950507023245313', '552816020403269632', '693912520923295745', '678277910537588737', '688520025754304512', '407290084593913856', '387021726007042051', '665317131597291520', '553099685888790528', '553461741917863936', '516804849619705859', '524946179390701568', '555003887753494528', '532275347413544961', '326137285450018817', '655432919595548672', '692453106622275585', '552821069036670976', '528341588867416064', '525040767317082113', '507634536176300032', '532275383430041600', '514495841600811009', '522692223952228353', '559787890402541568', '521882110789824512', '522782267215982592', '689549346875031552', '692925163994796033', '531634492528939008']
        out_txt_file = open(INTERIM_DATA_PATH + "root_tweet_id_list" + time.strftime("%Y%m%d-%H%M%S") + ".txt", 'w')
        out_txt_file.write(str(root_tweet_id_list))

        for index, root_tweet_id in enumerate(root_tweet_id_list):
            # print("Tweet ID: ", root_tweet_id)
            print("\n")
            print("=============================")
            print("Tweet ID: ", root_tweet_id)
            print("=============================")
            self.get_user_info_api(root_tweet_id)

        print("REQUEST_COUNT:", self.request_count)


def main():
    # Retrieve user ID set
    # input_builder = InputDataBuilder()
    # input_builder.iterate_tweet_trees()
    collector = SocialInfoCollector("UserInfo")  # FollowerFriend
    collector.iterate_user_sets()
    return 0


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
print("======================================")
print("     Social Information Retriever     ")
print("======================================")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("Elapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

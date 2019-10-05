import sys
sys.path.append('..')
from utils import *

from networkx.readwrite import json_graph
import json


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
        self.network = nx.DiGraph()
        self.load_cascade()

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

                # NetworkX Graph
                self.network.add_weighted_edges_from(
                    [(src_user_id, dst_user_id, float(dst_tweet_time) - float(src_tweet_time))])

    # =============================
    #      Structural Analysis
    # =============================
    def nework_to_json(self):
        G = self.network
        json_obj = json_graph.node_link_data(G, {'link': 'links', 'source': 'source', 'target': 'target'})
        # print(json_obj)
        # print("=============================")
        json_str = json.dumps(json_obj)
        # print(json_str)

        ensure_directory(OUT_PATH + 'json/')
        out_file_name = OUT_PATH + 'json/' + self.root_tweet_id + '_' + self.label + '.json'
        print(out_file_name)

        # out_file = open(out_file_name, 'w', encoding='utf-8', newline='')
        # json.dump(json_str, out_file)

        with open(out_file_name, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f)
            # json.dump(json_str, f, ensure_ascii=False, indent=4)




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

            print(self.cascades_dict[root_tweet_id].root_tweet_id)
            # break  # temporal

    # Main Outer loop
    def iterate_cascades(self):
        for index, row in self.meta_df.iterrows():
            tweet_id = row['tweet_id']
            # tweet_id = '553588178687655936'  # temporal
            cascade = self.cascades_dict[tweet_id]
            print('#', index, row['tweet_id'], row['label'])
            cascade.nework_to_json()
            # break  # temporal



def main():
    # CascadeAnalyzer -> Overall / Cascade -> Individual
    analyzer = CascadeAnalyzer()
    analyzer.iterate_cascades()


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
print("==============")
print("     JSON     ")
print("==============\n\n")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("\nElapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

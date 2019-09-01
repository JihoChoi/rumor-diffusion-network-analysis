import sys
sys.path.append('..')
from utils import *


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

        self.network = nx.DiGraph()
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

                weight = float(dst_tweet_time) - float(src_tweet_time)
                self.network.add_weighted_edges_from([(src_user_id, dst_user_id, 1/weight)])

    # =============================
    #      Structural Analysis
    # =============================
    def plot_circular_tree(self):
        # import pygraphviz
        from networkx.drawing.nx_agraph import graphviz_layout

        G = self.network
        label = self.label
        pos = graphviz_layout(G, prog='twopi', args='')

        if label == 'true':
            nc = 'blue'
        elif label == 'false':
            nc = 'red'
        elif label == 'unverified':
            nc = 'yellow'
        elif label == 'non-rumor':
            nc = 'green'
        else:
            nc = 'black'

        nx.draw(G, pos, node_size=20, alpha=0.5, node_color=nc, with_labels=False)

        out_dir_path = PLOTS_OUT_PATH + 'circular_tree_plot/'
        ensure_directory(out_dir_path)

        plt.savefig(out_dir_path + str(self.root_tweet_id) + ".png")
        plt.clf()


    def plot_diff_network(self):
        from networkx.drawing.nx_agraph import graphviz_layout

        G = self.network
        label = self.label
        # pos = graphviz_layout(G, prog='twopi', args='')
        pos = nx.spring_layout(G, weight='weight')

        if label == 'true':
            nc = 'blue'
        elif label == 'false':
            nc = 'red'
        elif label == 'unverified':
            nc = 'yellow'
        elif label == 'non-rumor':
            nc = 'green'
        else:
            nc = 'black'

        nx.draw(G, pos, node_size=20, alpha=0.5, node_color=nc, with_labels=False)
        nx.draw_networkx_edge_labels(G, pos)

        out_dir_path = PLOTS_OUT_PATH + 'diff_network_plot_2/'
        ensure_directory(out_dir_path)

        plt.savefig(out_dir_path + str(self.root_tweet_id) + ".png")
        plt.clf()



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
        print("-------------------------------------" * 2)
        print(self.meta_df.shape, self.meta_df['label'].value_counts().to_dict())
        print("-------------------------------------" * 2)

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

            # cascade.plot_circular_tree()

            cascade.plot_diff_network()


def main():
    # CascadeAnalyzer -> Overall / Cascade -> Individual
    analyzer = CascadeAnalyzer()
    analyzer.iterate_cascades()


# Rumor Diffusion Analysis Project
# https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
print("===============================")
print("     Network Visualization     ")
print("===============================\n\n")

if __name__ == '__main__':
    start_time = time.time()  # Timer Start
    main()
    print("\nElapsed Time: {0} seconds".format(round(time.time() - start_time, 3)))  # Execution time

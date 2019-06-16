from project_settings import *


def ensure_directory(path):
    # TODO: try-except
    if not os.path.exists(path):
        os.makedirs(path)
    # return path


def mean_max_of_list(list):
    if len(list) == 0:
        return 0, 0
    mean_v = sum(list) / len(list)
    max_v = max(list)
    return mean_v, max_v


def save_pickle_file(path, file_name, data):
    with open(path + file_name + '.pkl', 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


def load_pickle_file(file_path):
    with open(file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data

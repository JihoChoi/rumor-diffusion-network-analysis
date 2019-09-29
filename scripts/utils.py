from project_settings import *


def ensure_directory(path):
    # TODO: try-except
    if not os.path.exists(path):
        os.makedirs(path)
    # return path


def mean_max_of_list(l):
    # if not len(list):
    #     return 0, 0
    # mean_v = sum(list) / len(list)
    # max_v = max(list)
    # return mean_v, max_v
    avg_v = sum(l) / len(l) if len(l) else 0
    max_v = max(l) if l else 0
    return avg_v, max_v


def mean_of_list(l):
    return sum(l) / len(l) if len(l) else 0


def max_of_list(l):
    return max(l) if l else 0


def median_of_list(l):
    # if len(l):
    #     print(l)
    #     return statistics.median(l)
    # else:
    #     return 0

    return statistics.median(l) if len(l) else 0






def save_pickle_file(path, file_name, data):
    ensure_directory(path)
    with open(path + file_name + '.pkl', 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


def load_pickle_file(file_path):
    with open(file_path, 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    return data

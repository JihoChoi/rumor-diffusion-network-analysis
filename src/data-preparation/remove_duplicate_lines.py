from utils import *

# -----------------------------------
# Remove Duplicate Lines in Tree File
# -----------------------------------


def remove_duplicate_lines(input_file_path, output_file_path):

    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
        seen_lines = set()

        # Reference: https://stackoverflow.com/questions/1215208/how-might-i-remove-duplicate-lines-from-a-file
        def add_line(line):
            seen_lines.add(line)
            return line

        output_file.writelines((add_line(line) for line in input_file if line not in seen_lines))


for DATASET in ['twitter15/', 'twitter16/']:
    RAW_DATA_PATH = ROOT + 'data/rumor_detection_acl2017/' + DATASET

    ensure_directory(RAW_DATA_PATH + 'tree_u')

    for index, file in enumerate(os.listdir(RAW_DATA_PATH + 'tree')):

        if not file.endswith('.txt'):
            # TODO Error Exception
            continue

        input_path = os.path.join(RAW_DATA_PATH + 'tree', file)
        output_path = os.path.join(RAW_DATA_PATH + 'tree_u', file)

        print(index, file)
        remove_duplicate_lines(input_path, output_path)




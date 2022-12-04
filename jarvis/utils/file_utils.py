import glob
import os


def read_file(filepath):
    if os.path.exists(filepath):
        with open(file=filepath, mode="r") as infile:
            lines = []

            for line in infile.readlines():
                lines.append(line.removesuffix('\n'))

            infile.close()

            return lines
    else:
        print("File " + filepath + " doesn't exist...")


def read_all_files_in_folder(path, return_as_dict_with_filename=False):
    files = glob.glob(path, recursive=True)
    result = dict()
    result_list = []

    for file in files:
        lines = read_file(file)

        if return_as_dict_with_filename:
            filename = file.split("/")[-1].split('.')[0]
            result[filename] = lines
        else:
            result_list.extend(lines)

    if return_as_dict_with_filename:
        return result

    return result_list

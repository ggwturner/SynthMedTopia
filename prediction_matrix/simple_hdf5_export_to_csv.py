
import h5py
import csv
from utility_prediction import get_all_paths
import sys

def main(hdf5_file_name, paths=None):

    hf5p = h5py.File(hdf5_file_name, "r")
    if paths is None:
        paths = get_all_paths(hf5p["/"])

    else:
        expanded_paths = []
        for path in paths:
            expanded_paths += get_all_paths(hf5p[path])
        paths = expanded_paths

    annotations_paths = [hp for hp in paths if "column_annotations" in hp]
    core_array_paths = [hp for hp in paths if "core_array" in hp]
    annotations_list = []

    number_of_rows = hf5p[core_array_paths[0]].shape[0]

    i = 0
    for path in annotations_paths:
        annotations = hf5p[path][...]
        nrows, ncolumns = annotations.shape
        for j in range(ncolumns):
            field_name = ""
            for k in range(nrows):
                if len(annotations[k,j].strip()) > 0:
                    temp_string = annotations[k,j] + "."
                    field_name += temp_string
            field_name = field_name[:-1]
            annotations_list += [{"path": core_array_paths[i], "index": j, "field_name": field_name}]
        i += 1
    import pprint
    pprint.pprint(annotations_list)
    header = [ca["field_name"] for ca in annotations_list]
    with open(hdf5_file_name + ".csv", "wb") as fw:
        csv_writer = csv.writer(fw)
        csv_writer.writerow(header)

        for l in range(number_of_rows):
            row_to_write = []
            paths_core_vector = {}
            for path in core_array_paths:
                paths_core_vector[path] = hf5p[path][l, :]

            for annotation in annotations_list:
                row_to_write += [paths_core_vector[annotation["path"]][annotation["index"]]]
            csv_writer.writerow(row_to_write)

            if l % 1000 == 0 and l > 0:
                print("Wrote %s rows" % l)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python simple_hdf5_export_to_csv.py file_to_export.hdf5")
    main(sys.argv[1])

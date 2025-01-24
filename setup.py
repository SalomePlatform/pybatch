import os
from pathlib import Path

import setuptools
#from pytest2ctest.ctestfile_generator import compute_ctest_file


def get_data_files(data_files, basekey, path_list):
    """This function will return a list of tuples for the
    data_files parameter of the setup function.
    Args:
        - data_files: list, it is appended recursively
        - basekey: str, the subdirectory in the install directory
        - directories: the list of directories to install
    """
    for path in path_list:
        subdirs, files = [], []
        if os.path.isfile(path):
            key = os.path.join(basekey, os.path.dirname(path))
            files.append(path)
        elif os.path.isdir(path):
            key = os.path.join(basekey, path)
            for f in os.scandir(path):
                if f.is_dir():
                    subdirs.append(os.path.join(path, f.name))
                else:
                    if f.name[0] != ".":
                        files.append(os.path.join(path, f.name))
        else:
            print(path)
        data_files.append((key, files))
        get_data_files(data_files, basekey, subdirs)
    return data_files


#ctests_list = compute_ctest_file(
    #ctest_file=Path("tests/CTestTestfile.cmake"),
    #test_group_name="epylog",
    #test_files=["tests"],
    #trim_from_identifier="tests/",
#)

data_files = []
get_data_files(data_files, 'share/pybatch', ['tests', 'doc'])

setuptools.setup(
    data_files=data_files,
)

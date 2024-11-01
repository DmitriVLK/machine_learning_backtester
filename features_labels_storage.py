import os
from os.path import exists
import pickle
from common_utilities import CommonUtilities


class FeaturesLabelsStorage:

    @staticmethod
    def store_ready_features_labels(features_labels: list, file_characteristics: tuple,
                                    calculation_characteristics: tuple, directory_base: str = '.') -> str:
        """
        Stores the ready calculations from the processors to the file system.

        @param features_labels: list [features, labels]
        @param file_characteristics: tuple (processed file name, stored file name)
        @param calculation_characteristics: tuple (indicators, profit parameters, ccy parameters)
        @param directory_base: directory in which we must store the ready calculations
        @return: stored file path
        """
        stored_data = (features_labels, file_characteristics, calculation_characteristics)
        stored_full_path = os.path.join(os.getcwd(), directory_base, file_characteristics[1])
        with open(stored_full_path, 'wb') as open_pointer:
            pickle.dump(stored_data, open_pointer)
        return stored_full_path

    @staticmethod
    def restore_ready_features_labels(index: int = 0, file_name: str = None, directory_base: str = None) -> tuple:
        """
        Returns the most recent files that contain PKL calculations.
        You can call this method with just the file index. And it will check for the most recent PKL calculation
        for you automatically. Or use the file_name to provide with a specific file name that is searched.
        @param index: the pickled file index from the latest to restore.
        @param file_name: the specific file name to restore
        @param directory_base: directory in which to search for pickled files to restore. By default, uses ''.''
        @return: tuple with all files with the same prefix
        """
        if file_name is None:
            # If you don't want to check the latest file names:
            file_extension = ".pkl"
            file_name_base = CommonUtilities.get_most_recent_file_base_name_by_filename_extension(directory_base, file_extension)
            if file_name_base is None:
                print("There was no files found that match the restored file criteria. Make sure you went through all"
                      "the necessary algo steps to generate correct set of precursor files.")
                return tuple()
            searched_file_name = file_name_base + "_" + str(index) + file_extension
            if directory_base is not None and directory_base != "" and directory_base != ".":
                file_pointer = os.path.join(directory_base, searched_file_name)
            else:
                file_pointer = os.path.join(os.getcwd(), searched_file_name)
            if exists(file_pointer):
                with open(file_pointer, 'rb') as open_pointer:
                    loaded = pickle.load(open_pointer)
            else:
                # Such file doesn't exist
                return tuple()
            # If you know the specific file name that you are trying to load.
        else:
            with open(file_name, 'rb') as open_pointer:
                loaded = pickle.load(open_pointer)
        return loaded

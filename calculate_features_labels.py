from concurrent import futures
import multiprocessing
from os import getcwd, makedirs
from os.path import join
import constants
import indicators_set_up
from features_labels_storage import FeaturesLabelsStorage
from process_quotes_file import ProcessQuotesFile
from common_utilities import CommonUtilities


def run():
    """
    Runs the Features/Labels collect application
    """

    save_features_labels_folder = join(getcwd(), constants.FEATURES_LABELS_PATH)
    makedirs(save_features_labels_folder, exist_ok=True)

    csv_list = CommonUtilities.get_files_list_of_a_type_in_dir(constants.RAW_PATH)
    # Create the file name base.
    file_name_base = CommonUtilities.generate_file_name_base()

    if constants.MULTITHREADED:
        # Create adequate number of threads
        cpu_count = multiprocessing.cpu_count() - 2
        cpu_count = max(2, cpu_count)
        print("Creating multithreaded files processor with {} threads.".format(cpu_count))
        # Start working with ThreadPoolExecutor
        with futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
            # Create an empty list of Futures
            futures_obj = []

            file_index = 0
            for file_name in csv_list:
                full_file_name = join(getcwd(), constants.RAW_PATH, file_name)
                futures_obj.append(executor.submit(process_one_file, full_file_name, file_index, file_name_base))
                print("Added processor for {} file. (index {})".format(file_name, file_index))
                file_index += 1
            # Wait on all executions to end
            futures.wait(futures_obj)
            for finished_future in futures_obj:
                finished_future.result()
        print("Done processing files in multithreading.")
    else:
        file_index = 0
        for file_name in csv_list:
            print("Starting processing file: {} (index {})".format(file_name, file_index))
            full_file_name = join(getcwd(), constants.RAW_PATH, file_name)
            process_one_file(full_file_name, file_index, file_name_base)
            print("Processed file: {} (index {})".format(file_name, file_index))
            file_index += 1
        print("Done processing files.")


def process_one_file(file_name, file_index, file_name_base) -> bool:
    processor = ProcessQuotesFile(file_name, constants.PROFIT_LEVELS, constants.LOOKBACK_TIME)
    # Calculate
    processor.start_process(indicators_set_up.INDICATORS, constants.CCY_PAIR)
    # Get ready results
    processed_features_labels = processor.get_features_labels()

    total_lines_features_labels = len(processed_features_labels[0][0])

    print("\n{}: Collected {} features-labels.".format(file_index, total_lines_features_labels))
    # Store for later
    stored_file_name = file_name_base.format(file_index)
    FeaturesLabelsStorage.store_ready_features_labels(processed_features_labels,
                                                      (file_name, stored_file_name),
                                                      (indicators_set_up.INDICATORS, constants.PROFIT_LEVELS,
                                                       constants.CCY_PAIR), constants.FEATURES_LABELS_PATH)
    print("\n{}: Stored in {} features-labels.".format(file_index, stored_file_name))
    return True

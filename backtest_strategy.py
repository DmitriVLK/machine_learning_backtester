# This file contains the code to the backtester launch procedure.
from concurrent import futures
import multiprocessing
from os import getcwd
from os.path import join, exists
import keras
from tensorflow.python.data import Dataset

import keras_models
import numpy as np
from common_utilities import CommonUtilities
import constants
import indicators_set_up
from enum_classes import EnumPair
from process_quotes_file import ProcessQuotesFile
from quotes_reader import QuotesReader
from quote import Quote
from position import Position

def run() -> None:
    print("Starting BACKTEST.")
    csv_list = CommonUtilities.get_files_list_of_a_type_in_dir(constants.RAW_BACKTEST_PATH)

    currency_pair = constants.CCY_PAIR

    model_path = CommonUtilities.get_most_recent_file_base_name_by_filename_extension(constants.MODELS_PATH, ".keras")
    if model_path is None:
        print("There were no models saved/stored in the " + constants.MODELS_PATH + " folder. Ending procedure.")
        return
    model_path = join(constants.MODELS_PATH, model_path + "_0.keras")
    if exists(model_path):
        model = keras.models.load_model(model_path)
    else:
        raise ValueError("Please check while the KERAS model could not be loaded from path " + model_path)


    all_positions = []

    if constants.MULTITHREADED:
        # Create adequate number of threads
        cpu_count = multiprocessing.cpu_count() - 2
        cpu_count = max(2, cpu_count)
        print("Creating multithreaded files processor with {} threads.".format(cpu_count))
        # Start working with ThreadPoolExecutor
        with futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
            # Create an empty list of Futures. Will be filled with futures that will run multithreaded.
            futures_obj = []

            for file_name in csv_list:
                full_file_name = join(getcwd(), constants.RAW_BACKTEST_PATH, file_name)
                futures_obj.append(executor.submit(process, full_file_name, currency_pair, model))
            # Wait on all executions to end
            futures.wait(futures_obj)
            for finished_future in futures_obj:
                positions = finished_future.result()
                if positions is not None:
                    all_positions.extend(positions)
    else:
        # Single threaded version
        for file_name in csv_list:
            full_file_name = join(getcwd(), constants.RAW_BACKTEST_PATH, file_name)
            positions = process(full_file_name, currency_pair, model)
            if positions is not None:
                all_positions.extend(positions)

    # REPORTING
    total_variation = 0.0
    total_calmar = 0.0
    max_calmar = 0.0
    min_calmar = 0.0
    total_mdd = 0.0
    max_mdd = 0.0
    min_mdd = 0.0
    total_duration = 0
    total_return = 0.0
    max_loss = 0.0
    max_duration = 0
    for single_position in all_positions:
        # VARIATION METRIC. HERE IT IS THE QUANTITY OF MOVEMENTS DURING POSITION's LIFETIME
        total_variation += single_position.get_variation_metric()

        # CALMAR
        this_calmar = single_position.get_calmar_ratio()
        total_calmar += this_calmar
        if max_calmar < this_calmar:
            max_calmar = this_calmar
        if min_calmar > this_calmar:
            min_calmar = this_calmar

        # DD
        this_maxdd = single_position.get_max_draw_down()
        total_mdd += this_maxdd
        if max_mdd < this_maxdd:
            max_mdd = this_maxdd
        if min_mdd > this_maxdd:
            min_mdd = this_maxdd


        this_return = single_position.get_position_pnl()
        total_return += this_return
        if max_loss > this_return:
            max_loss = this_return

        this_duration = single_position.get_duration()
        total_duration += this_duration

        if max_duration < this_duration:
            max_duration = max_duration
    total_positions_count = len(positions)
    print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
    print('')
    print('      BACKTEST RESULT      ')
    print('')
    print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
    if total_positions_count == 0:
        print("No positions taken.")
    else:
        print(f'Total positions : {total_positions_count:,}')
        print(f'Total return : {total_return:,.2f}')
        print(f'Average return on positions : {total_return / total_positions_count:,.6f}')
        print(f'Maximal loss : {max_loss:,.6f}')
        print(f'Average of maximum losses of positions (max draw down) : {total_mdd / total_positions_count:,.6f}')
        print(f'Maximum loss of position (max draw down) : {max_mdd:,.6f}')
        print(f'Minimum loss of position (max draw down) : {min_mdd:,.6f}')
        print(f'Average Calmar ratio : {total_calmar / total_positions_count:,.6f}')
        print(f'Max Calmar ratio : {max_calmar:,.6f}')
        print(f'Min Calmar ratio : {min_calmar:,.6f}')
        print(f'Average duration of positions : {total_duration / total_positions_count:,.2f}')
        print(f'Total duration : {total_duration:,}')
        print(f'Max duration : {max_duration / constants.NANOS_IN_ONE_MINUTE:,} minutes')

def process(file_name, currency_pair: EnumPair, model: keras.Model) -> list:
    # load the trained model in the "model" folder using keras built-in tools
    quantity_processed = 0
    indicators_return_size = 0
    positions_list = []
    previous_report_time = 0

    indicators: tuple = ProcessQuotesFile.deep_copy_indicators(indicators_set_up.INDICATORS)
    order_book = CommonUtilities.init_globally_chosen_order_book(currency_pair)
    order_book.set_indicators(indicators)

    for indicator in indicators:
        indicators_return_size += indicator.get_return_size()[0]

    reader = QuotesReader(file_name, currency_pair)

    each_quote: Quote = reader.read_line()

    # No backtest/calculations for the first 100 quotes to update indicator values.
    while quantity_processed < 100 and each_quote is not None:
        order_book.incoming_quote(each_quote)
        quantity_processed += 1
        each_quote = reader.read_line()

    del quantity_processed

    # We don't want to open a number of positions in the same way as soon as a signal is present.
    current_position_is_long: bool = None

    while each_quote is not None:
        order_book.incoming_quote(each_quote)
        # Update all existing positions with the latest prices
        for position in positions_list:
            # Each position handles the OPEN/CLOSE process automatically.
            position.actualize(order_book.get_best_price(True),
                               order_book.get_best_price(False),
                               each_quote.get_local_timestamp())
        # Do the PREDICT only once X ms. Reuse the processor's function AS IS
        if ProcessQuotesFile.is_next_step_timer(previous_report_time,
                                                constants.EACH_STEP_TIMER,
                                                each_quote.get_local_timestamp()):
            previous_report_time = each_quote.get_local_timestamp()
            collected_features = ProcessQuotesFile.collect_indicators_values(indicators, indicators_return_size)
            # Wrap into a dataset object. Maybe the collected_features = (np.expand_dims(collected_features, 0))
            # would equally work
            collected_features = ([collected_features,],)
            collected_features = Dataset.from_tensor_slices(collected_features).batch(constants.BATCH_SIZE)
            #features = (np.expand_dims(collected_features, 0))
            label_prediction = model.predict(x=collected_features, verbose=0)
            # (ex. (True, False) -> buy, (False,True) -> sell, (False, False) or (True, True) -> nothing)
            label_prediction = (label_prediction[0][0] > 0.5, label_prediction[0][1] > 0.5)

            is_long = tuple(label_prediction) == (True, False)
            is_short = tuple(label_prediction) == (False, True)
            taking_position = is_long or is_short
            if taking_position:
                # Either the position is NONE and we are just starting the first position in backtest
                # Or we are switching ways in our position (we were LONG and the new signal is SELL for example)
                if current_position_is_long is None or ((is_long and not current_position_is_long) or (is_short and current_position_is_long)):
                    current_position_is_long = is_long
                    new_position = Position(is_long, order_book.get_best_price(True),
                                            order_book.get_best_price(False),
                                            each_quote.get_local_timestamp())
                    positions_list.append(new_position)

        # Update with new quote.
        each_quote = reader.read_line()
    # Close the reader.
    reader.close_reader()
    return positions_list

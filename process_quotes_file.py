import os
import copy
import constants
from common_utilities import CommonUtilities
from enum_classes import EnumPair
from feature_to_label_collection import FeatureToLabelCollection
from indicator import Indicator
from quote import Quote
from quotes_reader import QuotesReader


class ProcessQuotesFile:
    """
    This class uses the file in input and transforms it into a X -> y (features -> labels). It uses a panel
    of indicators that are implemented within.
    """

    def __init__(self, file_name: str, profit_levels: tuple, lookback_timer: int):
        """
        Constructor of the QUOTES FILE processor
        @param file_name: str. Path to file name. Absolute or relative.
        @param profit_levels: tuple containing the levels of take profit (to measure how big of a movement there was
        during some time).
        """
        self.__profit_levels = profit_levels
        self.__file_name = file_name
        self.__file_name_short = os.path.basename(self.__file_name)
        self.__lookback_timer = lookback_timer
        self.__features_labels = [None, None]
        self.__is_done = False
        self._quantity_processed = 0

    def get_features_labels(self) -> list:
        """
        Returns the features and labels array when the process is done.
        @return: tuple (features, labels)
        """
        if not self.__is_done:
            raise ValueError("Please calculate the Features -> labels" +
                             "before calling this method with start_process method.")
        return self.__features_labels

    def start_process(self, indicators_arg: tuple, currency_pair: EnumPair) -> bool:
        """
        Starts the transformation process
        @param currency_pair: currency pair on which we will perform calculations
        @param indicators_arg: list of indicators for this process
        @return: returns True if all done correctly. Returns False if there were errors or not enough data.
        """
        # Reset:
        profit_levels_length = len(self.__profit_levels)
        self.__features_labels = [[[] for i in range(profit_levels_length)], list()]
        self._quantity_processed = 0

        # Create a deep copy of the indicators: we could be processing several indicators at the same time.
        indicators: tuple = ProcessQuotesFile.deep_copy_indicators(indicators_arg)

        order_book = CommonUtilities.init_globally_chosen_order_book(currency_pair)

        order_book.set_indicators(indicators)

        indicators_return_size = 0
        for indicator in indicators:
            # TO CHANGE IF YOU WILL USE N-M-x-D quotes return size! Currently supports N-1:
            indicators_return_size += indicator.get_return_size()[0]

        reader = QuotesReader(self.__file_name, currency_pair)

        feature_label_collection = FeatureToLabelCollection(self.__lookback_timer, self.__profit_levels)
        # This is an object that can be shared between several processes inside this class/method:

        each_quote: Quote = reader.read_line()

        previous_report_time = 0
        # Process each quote in the file.
        while each_quote is not None:
            order_book.incoming_quote(each_quote)
            # How many quotes did we process so far
            self._quantity_processed += 1

            # Modify this condition at will!
            # For example, you might as well use: self._is_next_step() if you want to count steps
            # Do not report for the first 100 quotes as we are building the order book.
            if (ProcessQuotesFile.is_next_step_timer(previous_report_time,
                                                     constants.EACH_STEP_TIMER,
                                                     each_quote.get_local_timestamp())
                    and self._quantity_processed > 100):

                previous_report_time = each_quote.get_local_timestamp()
                # Each 10 quotes (OR AS YOUR CONDITION)
                # -> put one in the feature_label_collection
                collected_features: tuple = self.collect_indicators_values(indicators, indicators_return_size)
                feature_label_collection.put(each_quote.get_local_timestamp(),
                                             order_book.get_best_price(True),
                                             order_book.get_best_price(False),
                                             collected_features)

            # Each step: check the profit levels of the existing reported features.
            feature_label_collection.check_profit_levels_on_active_cells(each_quote.get_local_timestamp(),
                                                                         order_book.get_best_price(True),
                                                                         order_book.get_best_price(False))

            if self._quantity_processed % constants.FREQUENCY_OF_DATA_TRANSFERS == 0:
                reported_cell = feature_label_collection.get_ready_calculations()
                for level in range(min(profit_levels_length, len(reported_cell[0]))):
                    self.__features_labels[0][level] += reported_cell[0][level]
                self.__features_labels[1] += reported_cell[1]
                # Report each 10000 lines
                if constants.TRACE:
                    print("{}: processed {} quotes.".format(self.__file_name_short, self._quantity_processed))

            each_quote = reader.read_line()

        # Done processing: collect the data
        reader.close_reader()
        reported_cell = feature_label_collection.get_ready_calculations()
        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            self.__features_labels[0][level] += reported_cell[0][level]
        self.__features_labels[1] += reported_cell[1]
        self.__is_done = True
        return self.__is_done

    # START Step conditions section
    def _is_next_step(self) -> bool:
        """
        STEP condition. Modifiable.
        @return: True if it's the next step. False if it isn't.
        """
        if self._quantity_processed % 10 == 0:
            return True
        return False

    @staticmethod
    def is_next_step_timer(previous_time_reported: int, report_period: int, current_time: int) -> bool:
        """
        STEP condition. Modifiable. Implements a TIMED span between quotes.
        @param current_time: the time that we obse
        @param report_period: how often the timer to take action works
        @param previous_time_reported: the las time we updated the indicators collection
        @return: True if it's the next step. False if it isn't.
        """
        if previous_time_reported + report_period <= current_time:
            return True
        return False

    # END Step conditions section

    # START Utility methods
    @staticmethod
    def deep_copy_indicators(indicators: tuple) -> tuple:
        """
        Creates a clone collection of indicators with a deep copy
        @param indicators: the collection to deep copy
        @return: a tuple a copy of all indicators.
        """
        indicators_clone = []
        for indicator in indicators:
            indicator_clone = copy.deepcopy(indicator)
            indicators_clone.append(indicator_clone)
        return tuple(indicators_clone)

    @staticmethod
    def collect_indicators_values(indicators: tuple, indicators_return_size: int) -> tuple:
        """
        Collects the current values of the indicators and returns a 1-D array with it.
        If you will use N-M-x-D arrays, please reformat the method accordingly!
        @param indicators_return_size: the size of the return for all the indicators
        @param indicators: all the indicators that are being calculated
        @return: list of all current observations in the indicators.
        """
        indicator: Indicator
        collected_features = [0.0] * indicators_return_size
        index = 0
        for indicator in indicators:
            current_values = indicator.get_current_value()
            if indicator.get_return_size()[0] == 1:
                collected_features[index] = current_values
                index += 1
            else:
                for current_value in current_values:
                    collected_features[index] = current_value
                    index += 1
        return tuple(collected_features)

    # END Utility methods

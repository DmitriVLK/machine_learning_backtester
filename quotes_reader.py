import os
import re
from datetime import datetime, timedelta

import constants
from quote import Quote
from common_utilities import CommonUtilities
from enum_classes import EnumPair, EnumOrderBook


class QuotesReader:

    __START_OF_TIMES = datetime(1970, 1, 1)

    def __init__(self, file_name: str, currency_pair_arg: EnumPair, info: bool = False) -> None:
        """
        Constructor for single currency reader.
        @param file_name: file path. Absolute or relative.
        @param currency_pair_arg: ENUM pair as EnumPair object. Containing the information of CCY Pair that is being
        monitored.
        @param info: True if you want to get reading status (True by default).
        @param debug:  true if you want to get more reading status (False by default).
        """

        self.__file_name = file_name
        self.__reader = open(self.__file_name)
        self.__file_name_short = os.path.basename(self.__file_name)
        self.__is_reader_closed = False
        self.currency_pair_enum = currency_pair_arg
        self.currency_pair_str = currency_pair_arg.get_ccy_pair_with_slash()
        if constants.ORDER_BOOK_TYPE == EnumOrderBook.HIGH_FREQ_FX:
            self.__new_pattern = r"N;[0-9-]+;" + self.currency_pair_str +\
                                 r";[0-9]+;[0-9]+;[0-9]+.[0-9]{2};[0-9]+.[0-9]{2};[0-9]+.[0-9]{2};[0-9]+.[0-9]+;[BS];[0-9]"
        elif constants.ORDER_BOOK_TYPE == EnumOrderBook.DUKASKOPY:
            # Skip 1st line with title head.
            self.__reader.readline()
            self.__current_line = ""
            # The data in the DUKASKOPY files are arranged BID+OFFER on the same line. Therefore we will alternate
            # Bid first, then Offer. Then we read a new line.
            self.__gets_bid = True
            # FORMAT: Gmt time,Ask,Bid,AskVolume,BidVolume
            self.__new_pattern = r"[0-9]{2}.[0-9]{2}.[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3},[0-9]+.[0-9]+,[0-9]+.[0-9]+[0-9]+,[0-9]+"
        self._info = info

        if constants.DEBUG:
            # Force INFO when debugging.
            self._info = True
            self.__line_by_line_reader_counter = 0

        if self._info:
            self.__line_quote_by_quote_reader_counter = 0

        if self._info:
            print("{}: created reader for file. Reading {} ccy pair.".format(self.__file_name_short,
                                                                             self.currency_pair_str))

    def read_line(self) -> Quote:
        """
        Read dynamically next quote from the file, provided in the constructor.
        @return Function used to read one line of the CSV for one currency pair and returns a quote.
        Or None if the line was empty and there was nothing else to read.
        """
        if self.__is_reader_closed:
            return None  # This is intended.

        if constants.ORDER_BOOK_TYPE == EnumOrderBook.HIGH_FREQ_FX:
            line = self.__reader.readline()
        elif constants.ORDER_BOOK_TYPE == EnumOrderBook.DUKASKOPY:
            if self.__gets_bid:
                # because we skip reading line when we try to get a SELL
                self.__current_line = self.__reader.readline()
            line = self.__current_line
        quote = None
        # Read the lines while you haven't met next QUOTE with necessary CCYies
        while quote is None:
            if constants.DEBUG:
                self.__line_by_line_reader_counter += 1
                if self.__line_by_line_reader_counter % constants.FREQUENCY_OF_DATA_TRANSFERS * 5 == 0:
                    print("\r{}: read {} lines in the file".format(self.__file_name_short,
                                                                  self.__line_by_line_reader_counter), end=' ')
            if not line:
                # Problem reading/end of file -> exit
                # Close: resource leakage
                self.__reader.close()
                self.__is_reader_closed = True
                if self._info:
                    print("\n{}: done reading file: no lines remaining in the file.".format(self.__file_name_short))
                return None  # This is intended.
            if constants.ORDER_BOOK_TYPE != EnumOrderBook.HIGH_FREQ_FX or self._is_has_currency(line):
                quote = self.deserialize_quote(line)
                if constants.ORDER_BOOK_TYPE != EnumOrderBook.HIGH_FREQ_FX:
                    # Fetch the Offer next time if it was a Bid this time
                    self.__gets_bid = not self.__gets_bid
            else:
                line = self.__reader.readline()

        # Found another quote.

        if constants.TRACE:
            self.__line_quote_by_quote_reader_counter += 1
            if self.__line_quote_by_quote_reader_counter % constants.FREQUENCY_OF_DATA_TRANSFERS * 5 == 0:
                print("{}: read {} quotes from file".format(self.__file_name_short,
                                                            self.__line_quote_by_quote_reader_counter))
        return quote

    def close_reader(self) -> None:
        """
        Release reader resources
        """
        self.__reader.close()
        self.__is_reader_closed = True

    def deserialize_quote(self, quote_line: str) -> Quote:
        """
        @param deserializes the quote_line into a Quote object
        Function that determines which quotes it is by using the regex
        The regex allows to determine if it matches the correct pattern and is not in error
        """
        if bool(re.match(self.__new_pattern, quote_line)):
            if constants.ORDER_BOOK_TYPE == EnumOrderBook.HIGH_FREQ_FX:
                line_list = CommonUtilities.split_quote_line_to_list(quote_line)[1:-1]
            else:
                # We will read a BID one time. then read an OFFER a second time.
                split_line = quote_line.split(",")
                # Convert time to number
                utc_time = datetime.strptime(split_line[0], '%d.%m.%Y %H:%M:%S.%f')
                milliseconds = (utc_time - QuotesReader.__START_OF_TIMES) // timedelta(milliseconds=1)
                long_time = milliseconds * constants.NANOS_IN_ONE_MILLIS
                px: float
                amt: float
                if self.__gets_bid:
                    px = float(split_line[1])
                    amt = float(split_line[3])
                else:
                    px = float(split_line[2])
                    amt = float(split_line[4])
                # time is in format '21.10.2024 00:00:00.161' equivalent to '%d-%m-%Y %H:%M:%S.%f'
                line_list = [0, self.currency_pair_enum.get_ccy_first(), self.currency_pair_enum.get_ccy_second(),
                             long_time, long_time, amt, 0.0, 0.0, px, self.__gets_bid]
            return Quote(*line_list)
        if constants.DEBUG:
            print("{}: the quote line number {} couldn't be matched vs regex: {}"
                  .format(self.__file_name_short, self.__line_by_line_reader_counter, quote_line))
        return None

    def _is_has_currency(self, quote_line: str) -> bool:
        """
        Checks the line for the CCY pair in the known position.
        """
        count_of_point_comma: int = 0
        count_of_read_chars: int = 0
        count_chars = len(quote_line)
        while count_of_read_chars < count_chars:
            if quote_line[count_of_read_chars] == ";":
                count_of_point_comma += 1
            if count_of_point_comma == 2:
                # Check that we will not overflow the count of characters in this line.
                if count_of_read_chars + 8 < count_chars:
                    if quote_line[count_of_read_chars+1:count_of_read_chars+8] == self.currency_pair_str:
                        # Correct ccy pair
                        return True
                    else:
                        # Other ccy pair
                        return False
            if count_of_point_comma > 2:
                return False
            count_of_read_chars += 1
        # we haven't found enough ';'
        return False

    def __count_instances_of_ccy_pair(self) -> int:
        """
        Counts the number of CCY pair occurrences in the file
        """
        total_found = 0
        reader = open(self.__file_name)
        line = reader.readline()

        while line:
            if self._is_has_currency(line):
                total_found += 1
            line = reader.readline()

        reader.close()
        return total_found

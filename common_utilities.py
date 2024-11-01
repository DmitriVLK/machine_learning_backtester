import os
import glob
import re
import math
from itertools import (takewhile, repeat)
import hashlib
import constants
from datetime import datetime

from enum_classes import EnumOrderBook, EnumPair
from order_book import OrderBook
from order_book_dukaskopy import OrderBookDukascopy
from order_book_high_freq_fx import OrderBookHighFreqFx


def asc_key_fn(key):
    """
    This is a key sort function. It's used in the SortedDict collection
    @param key: provided by the SortedDict
    @return:
    """
    return key


def dsc_key_fn(key):
    """
    This is a key sort function
    @param key: provided by the SortedDict
    @return:
    """
    return -key


class CommonUtilities:
    """
    Utility class. No instance methods and constructors here
    """

    # Best way to store files: these can be sorted easily in the file system.
    __calculation_date: datetime = datetime.today()

    @staticmethod
    def num_of_rows(address: str) -> int:
        """
        Function that counts the number of rows in the data file
        Buffer read strategy. rawincount method as in
        https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python
        @param address: the path to the FILE with quotes
        @return: count of rows in that file
        """
        f = open(address, 'rb')
        bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
        # Add +1 because on the last line we could miss the CR LF char
        count = sum(buf.count(b'\n') for buf in bufgen) + 1
        f.close()
        return count

    @staticmethod
    def get_files_list_of_a_type_in_dir(directory_base: str = None, file_type: str = ".csv") -> list:
        """
        @param directory_base: the relative direcory in which we are looking for files. If not filled -- uses CWD
        @param file_type: we will look for all the files matching *.csv by default.
        @return a list with all the files found under this directory
        Function that returns a list of all the file_type that exists in the directory
        """
        # In case the user forwards a directory that is hardcoded. This should never happen
        if directory_base is not None and os.sep in directory_base:
            print("WARNING! PLEASE DO NOT USE ABSOLUTE PATHS TO FILES IN THIS SOFTWARE.")
            return glob.glob("*" + file_type, root_dir=directory_base)
        if directory_base is None:
            original_dir = os.getcwd()
        else:
            original_dir = os.path.join(os.getcwd(), directory_base)
        files_list_found = glob.glob("*" + file_type, root_dir=original_dir)
        return files_list_found

    @staticmethod
    def generate_file_name_base(file_extension:str = ".pkl") -> str:
        """
        Generates the file name bases that can later be used for the store-restore procedures.
        @return: file name base as string
        """
        file_name_local: str
        start_date_str = CommonUtilities.__calculation_date.strftime(constants.DATE_FORMAT)
        # Composed file name
        file_name_local = start_date_str + "_{}" + file_extension
        return file_name_local

    @staticmethod
    def get_most_recent_file_base_name_by_filename_extension(directory_base:str= None,
                                                             file_extension:str = ".csv") -> str:
        """
        @param directory_base: a list of string
        @param file_extension: the extension of files that we are looking for
        @return: a filename base name which usually has a name date
         yyyy-mm-dd_XXX.file_extension or yyyy-mm-dd.file_extension
        """
        all_found_files = CommonUtilities.get_files_list_of_a_type_in_dir(directory_base, file_extension)
        if len(all_found_files) > 0:
            # Found some PKL files in this directory.
            all_found_sorted = sorted(all_found_files, reverse=True)
            for next_found in all_found_sorted:
                if "_" in next_found:
                    return next_found.split('_')[0]
            # Otherwise it's just a filename. Hopefully the most recent.
            if "." in all_found_sorted[0]:
                return all_found_sorted[0].split(".")[0]
            # If no DOT in the filename -- return nothing
            print("WARNING! Your filename didn't contain a file extension for some reason.")
            return ""

    @staticmethod
    def split_quote_line_to_list(quote_line: str) -> list:
        """
        Function that split string in the line by the occurrences of pattern
        Transform the line to a list
        """
        # Strip the \r\n  (\r, \n, and space) characters. Those are not correctly converted to numbers.
        quote_line = quote_line.rstrip("\r\n")
        # Split the line into a list with the ';' as separator. Use re.split method.
        line_list: list = re.split(";", quote_line)
        # EUR/USD -> liste de EUR et USD
        currency = line_list[2]
        list_of_ccies = currency[:3], currency[4:]
        del line_list[2]
        line_list[2:2] = list_of_ccies
        return line_list

    @staticmethod
    def precision_round(number: float) -> float:
        """
        Truncates the number to a managable/comparable size. Helps preventing the situation where you might have too
        many numbers in the fraction.
        @param number: truncated number
        @return: truncated number
        """
        return round(number, constants.FLOAT_ROUND_PRECISION)

    @staticmethod
    def are_equal(number1: float, number2: float) -> bool:
        """
        Compares two numbers using the precision rounding defined in CommonUtilities.precision_round
        @param number1:
        @param number2:
        @return: true if numbers are equal
        """
        if math.isclose(number1, number2, rel_tol=constants.FLOAT_ROUND_PRECISION_DEC):
            return True
        return False

    @staticmethod
    def return_md5_string_hash(string_to_hash: str, **kwargs) -> int:
        """
        Returns a hash of string given in input (as integer)
        :param string_to_hash: text that will be hashed
        :param length: maximal length of the returned integer
        :return: int representing the provided string
        """
        if 'length' in kwargs and kwargs['length'] is not None and kwargs['length'] >= 10:
            # for some reason the length is + 2
            return int(hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()[:kwargs['length'] - 1], 16)
        else:
            return int(hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()[:15], 16)

    @staticmethod
    def init_globally_chosen_order_book(currency_pair: EnumPair = EnumPair.OTHER) -> OrderBook:
        """
        Initializes the implementation of the order book selected in the global settings.
        @param currency_pair: the ccy pair for which we init the order book. Defaults to OTHER
        @return: HIGH_FREQ_FX order book or DUKASKOPY order book. You can add additional order books if needed.
        """
        if constants.ORDER_BOOK_TYPE == EnumOrderBook.HIGH_FREQ_FX:
            return OrderBookHighFreqFx(currency_pair)
        elif constants.ORDER_BOOK_TYPE == EnumOrderBook.DUKASKOPY:
            return OrderBookDukascopy(currency_pair)
        else:
            raise ValueError("Unrecognized order book type selected.")
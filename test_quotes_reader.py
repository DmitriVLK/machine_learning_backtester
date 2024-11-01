from unittest import TestCase

from enum_classes import EnumPair
from quotes_reader import QuotesReader
from quote import Quote


class TestQuotesReader(TestCase):

    def test_read_by_line_level_file(self):
        """
        Function that test to reads the CSV lines for one currency line by line
        """
        file_name: str = "test_level_format.csv"
        currency_pair: EnumPair = EnumPair.EURUSD

        reader = QuotesReader(file_name, currency_pair)

        list_of_quotes = []
        next_quote: Quote = reader.read_line()

        while next_quote is not None:
            list_of_quotes.append(next_quote)
            next_quote = reader.read_line()

        self.assertEqual(4496, len(list_of_quotes))

    def test_read_by_line_level_file_debug(self):
        """
        Function that test to reads the CSV lines for one currency line by line. DEBUG ON.
        """
        file_name: str = "test_level_format.csv"
        currency_pair: EnumPair = EnumPair.EURUSD

        reader = QuotesReader(file_name, currency_pair, True)

        list_of_quotes = []
        next_quote: Quote = reader.read_line()

        while next_quote is not None:
            list_of_quotes.append(next_quote)
            next_quote = reader.read_line()

        self.assertEqual(4496, len(list_of_quotes))

    def test_read_file_with_problem(self):
        """
        Function that tries to read a file which has an unexpected ending.
        """
        file_name: str = "test_problem_file.csv"
        currency_pair: EnumPair = EnumPair.EURUSD

        reader = QuotesReader(file_name, currency_pair)

        list_of_quotes = []
        next_quote: Quote = reader.read_line()

        while next_quote is not None:
            list_of_quotes.append(next_quote)
            next_quote = reader.read_line()

        self.assertEqual(1096, len(list_of_quotes))

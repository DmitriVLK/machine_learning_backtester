from unittest import TestCase

import constants
import enum_classes
from order_book import OrderBook
from order_book_high_freq_fx import OrderBookHighFreqFx
from quotes_reader import QuotesReader


class TestOrderBook(TestCase):
    # This code tests the capabilities of the Level Order Book

    def test_constructor(self):
        test_order_book1 = OrderBookHighFreqFx(enum_classes.EnumPair.EURUSD)
        test_order_book2 = OrderBookHighFreqFx()
        self.assertEqual(enum_classes.EnumPair.EURUSD, test_order_book1.get_ccy_pair())
        self.assertEqual(enum_classes.EnumPair.OTHER, test_order_book2.get_ccy_pair())

    @staticmethod
    def populate_order_book(test_order_book: OrderBook = None) -> OrderBook:
        constants.ORDER_BOOK_TYPE = enum_classes.EnumOrderBook.HIGH_FREQ_FX
        book_ccy_pair = enum_classes.EnumPair.EURJPY

        reader: QuotesReader = QuotesReader("test_level_format.csv", book_ccy_pair)

        if test_order_book is None:
            test_order_book = OrderBookHighFreqFx(book_ccy_pair)
        else:
            test_order_book.set_ccy_pair(book_ccy_pair)

        quote_str_1 = "N;1564914665855-300000--1;EUR/JPY;51128851000000;1565007128828;300000.00;0.00;0.00;118.57900;B;0"
        quote_str_2 = "N;1564914665855-300000--1;EUR/JPY;51128852000000;1565007128828;300000.00;0.00;0.00;118.60000;S;0"
        quote_str_3 = "N;1564914665855-1000000--1;EUR/JPY;51128852365237;1565007128828;1000000.00;0.00;0.00;118.57900;B;0"
        quote_str_4 = "N;1564914665855-1000000--1;EUR/JPY;51128852365238;1565007128828;1000000.00;0.00;0.00;118.60000;S;0"
        quote_str_5 = "N;1564914665862-300000--1;EUR/JPY;51128887000000;1565007128884;300000.00;0.00;0.00;118.58100;B;0"
        quote_str_6 = "N;1564914665862-300000--1;EUR/JPY;51128887003581;1565007128884;300000.00;0.00;0.00;118.60000;S;0"
        quote1 = reader.deserialize_quote(quote_str_1)
        quote2 = reader.deserialize_quote(quote_str_2)
        quote3 = reader.deserialize_quote(quote_str_3)
        quote4 = reader.deserialize_quote(quote_str_4)
        quote5 = reader.deserialize_quote(quote_str_5)
        quote6 = reader.deserialize_quote(quote_str_6)
        test_order_book.incoming_quote(quote1)
        test_order_book.incoming_quote(quote2)
        test_order_book.incoming_quote(quote3)
        test_order_book.incoming_quote(quote4)
        test_order_book.incoming_quote(quote5)
        test_order_book.incoming_quote(quote6)
        reader.close_reader()
        return test_order_book

    def test_pair(self):
        test_order_book = TestOrderBook.populate_order_book()
        book_ccy_pair = enum_classes.EnumPair.EURJPY
        self.assertEqual(book_ccy_pair, test_order_book.get_ccy_pair())

    def test_quotes_count(self):
        test_order_book = TestOrderBook.populate_order_book()
        self.assertEqual(4, test_order_book.get_quotes_count())
        self.assertEqual(2, test_order_book.get_quotes_count(True))
        self.assertEqual(2, test_order_book.get_quotes_count(False))

    def test_book_volume(self):
        test_order_book = TestOrderBook.populate_order_book()
        self.assertEqual(2000000.00, test_order_book.get_book_volume())
        self.assertEqual(1000000.00, test_order_book.get_book_volume(True))
        self.assertEqual(1000000.00, test_order_book.get_book_volume(False))

    def test_book_vol_sec_ccy(self):
        test_order_book = TestOrderBook.populate_order_book()
        self.assertEqual(1000000.00 * 118.57900 + 1000000.00 * 118.60000, test_order_book.get_book_volume_in_second_ccy())
        self.assertEqual(1000000.00 * 118.57900, test_order_book.get_book_volume_in_second_ccy(True))
        self.assertEqual(1000000.00 * 118.60000, test_order_book.get_book_volume_in_second_ccy(False))

    def test_book_snapshot(self):
        test_order_book = TestOrderBook.populate_order_book()
        snapshot_all = test_order_book.get_current_snapshot()
        snapshot_bids = test_order_book.get_current_snapshot(True)
        snapshot_offers = test_order_book.get_current_snapshot(False)

        self.assertEqual(4, len(snapshot_all))
        self.assertEqual(2, len(snapshot_bids))
        self.assertEqual(2, len(snapshot_offers))
        for each_bid in snapshot_bids:
            self.assertTrue(each_bid.get_way())
        for each_offer in snapshot_offers:
            self.assertFalse(each_offer.get_way())
        self.assertTrue(snapshot_bids[0].get_id_ecn() != snapshot_bids[1].get_id_ecn())
        self.assertTrue(snapshot_offers[0].get_id_ecn() != snapshot_offers[1].get_id_ecn())

    def test_executed_quotes_for_volume(self):
        test_order_book = TestOrderBook.populate_order_book()
        executed_quotes = test_order_book.get_executed_quotes_for_volume(True, 200000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665862-300000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume(True, 400000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume(True, 1200000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume(False, 200000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665862-300000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume(False, 400000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume(False, 1200000.00)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

    def test_executed_quotes_for_volume_second_ccy(self):
        test_order_book = TestOrderBook.populate_order_book()
        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(True, 200000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665862-300000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(True, 400000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(True, 1200000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(False, 200000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665862-300000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(False, 400000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

        executed_quotes = test_order_book.get_executed_quotes_for_volume_in_second_ccy(False, 1200000.00 * 118.60)

        self.assertEqual(1, len(executed_quotes))
        self.assertEqual("1564914665855-1000000--1", executed_quotes[0].get_id_ecn())

    def test_retrieve_order(self):
        test_order_book = TestOrderBook.populate_order_book()
        found_orders = test_order_book.retrieve_order("1564914665862-300000--1")

        self.assertEqual(2, len(found_orders))
        self.assertTrue(found_orders[0] is not None)
        self.assertTrue(found_orders[1] is not None)

        found_orders = test_order_book.retrieve_order("156465862-30000--1")
        self.assertEqual(2, len(found_orders))
        self.assertTrue(found_orders[0] is None)
        self.assertTrue(found_orders[1] is None)

    def test_clear_order_book(self):
        test_order_book = TestOrderBook.populate_order_book()
        test_order_book.clear_orderbook()

        self.assertEqual(0, test_order_book.get_quotes_count(True))
        self.assertEqual(0, test_order_book.get_quotes_count(False))

        TestOrderBook.populate_order_book(test_order_book)

    def test_get_best_quote(self):
        test_order_book = TestOrderBook.populate_order_book()
        best_quote = test_order_book.get_best_quote(True)
        self.assertEqual(118.58100, best_quote.get_price())

        best_quote = test_order_book.get_best_quote(False)
        self.assertEqual(118.600, best_quote.get_price())

    def test_get_best_price(self):
        test_order_book = TestOrderBook.populate_order_book()
        best_quote = test_order_book.get_best_price(True)
        self.assertEqual(118.58100, best_quote)

        best_quote = test_order_book.get_best_price(False)
        self.assertEqual(118.600, best_quote)

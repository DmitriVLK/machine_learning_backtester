from unittest import TestCase
import constants
from enum_classes import EnumPair, EnumOrderBook
from indicator_best_bid_offer_variance import IndicatorBestBidOfferVariance
from indicator_quantity_of_quotes_in_book import IndicatorQuantityOfQuotesInBook
from process_quotes_file import ProcessQuotesFile


class TestProcessQuotesFile(TestCase):

    def test_process(self):
        constants.ORDER_BOOK_TYPE = EnumOrderBook.HIGH_FREQ_FX
        # Chosen currency pair for training
        currency_pair = EnumPair.EURUSD
        # the levels of searched take profit for the currency pair.
        profit_levels = (0.00005, 0.0001)
        lookback_time = 3 * constants.NANOS_IN_ONE_MINUTE
        # How long do we wait between each step (recalculation of indicators and report to FeatureToLabelCollection)
        each_step_time = 100 * constants.NANOS_IN_ONE_MILLIS
        indicators = (IndicatorBestBidOfferVariance(),
                      IndicatorQuantityOfQuotesInBook())
        processor = ProcessQuotesFile(r"test_level_format.csv", profit_levels, lookback_time)
        processor.start_process(indicators, currency_pair)

        self.assertIsNotNone(processor.get_features_labels())


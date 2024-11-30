from unittest import TestCase
import unittest
import numpy as np
from order_book_high_freq_fx import OrderBookHighFreqFx
from enum_classes import EnumPair
import copy

from enum_classes import EnumCcy
from indicator_best_bid_offer_variance import IndicatorBestBidOfferVariance
from quote import Quote


class TestIndicatorBestBidOfferVariance(TestCase):
    def test_constructor(self):
        # Test de l'initialisation de l'indicateur
        variance_indicator = IndicatorBestBidOfferVariance()
        self.assertEqual("Variance of best bid and best offfer over 10 periods", variance_indicator.get_doc_description())
        self.assertEqual("VAR_BBID_BOFFER_10", variance_indicator.get_description())
        return_size = variance_indicator.get_return_size()
        self.assertEqual(tuple, type(return_size))
        self.assertEqual((2,), return_size)
        self.assertEqual(1, len(return_size))

    def test_insert_quotes(self):
        ob = OrderBookHighFreqFx(EnumPair.EURUSD)

        # Quotes nécessaires pour valider les calculs
        quotes = [
            Quote(1, EnumCcy.EUR, EnumCcy.USD, 0, 0, 1000.00, 0.00, 0.00, 10.00, True),  # Bid
            Quote(2, EnumCcy.EUR, EnumCcy.USD, 0, 0, 1000.00, 0.00, 0.00, 20.00, False),  # Offer
            Quote(3, EnumCcy.EUR, EnumCcy.USD, 0, 0, 1000.00, 0.00, 0.00, 12.00, True),  # Bid
            Quote(4, EnumCcy.EUR, EnumCcy.USD, 0, 0, 1000.00, 0.00, 0.00, 18.00, False),  # Offer
            Quote(5, EnumCcy.EUR, EnumCcy.USD, 0, 0, 1000.00, 0.00, 0.00, 14.00, True),  # Bid
        ]

        # Initialisation de l'indicateur
        variance_indicator = IndicatorBestBidOfferVariance()
        ob.set_indicators([variance_indicator])

        # Insertion des quotes
        for quote in quotes:
            ob.incoming_quote(quote)

        # Observations des bids et offers
        bids = variance_indicator._IndicatorBestBidOfferVariance__last_bid_obs
        offers = variance_indicator._IndicatorBestBidOfferVariance__last_offer_obs

        print(f"Last bid observations: {bids}")
        print(f"Last offer observations: {offers}")

        # Calcul des variances attendues
        num_obs = IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS
        mean_bids = sum(bids) / num_obs
        mean_offers = sum(offers) / num_obs

        variance_bids = sum((x - mean_bids) ** 2 for x in bids) / num_obs
        variance_offers = sum((x - mean_offers) ** 2 for x in offers) / num_obs

        expected_variances = [variance_bids, variance_offers]

        # Variances calculées
        calculated_variances = variance_indicator.get_current_value()
        print(f"Calculated variances: {calculated_variances}")
        print(f"Expected variances: {expected_variances}")

        # Vérification
        self.assertAlmostEqual(expected_variances[0], calculated_variances[0], places=7)
        self.assertAlmostEqual(expected_variances[1], calculated_variances[1], places=7)

    def test_deep_copy(self):
        # Test de la copie profonde
        variance_indicator = IndicatorBestBidOfferVariance()
        copied_indicator = copy.deepcopy(variance_indicator)
        self.assertEqual("Variance of best bid and best offfer over 10 periods", copied_indicator.get_doc_description())
        self.assertEqual("VAR_BBID_BOFFER_10", copied_indicator.get_description())
        self.assertTrue(variance_indicator != copied_indicator)


if __name__ == "__main__":
    unittest.main()

from typing import List
from indicator import Indicator
from indicator_best_bid_offer_variance import IndicatorBestBidOfferVariance
from indicator_moving_average_on_price import IndicatorMovingAverageOnPrice
from indicator_moving_average_on_amount import IndicatorMovingAverageOnAmount
from indicator_quantity_of_quotes_in_book import IndicatorQuantityOfQuotesInBook


# Chosen set of indicators
INDICATORS: tuple = (IndicatorMovingAverageOnPrice(5),
                     IndicatorMovingAverageOnPrice(10),
                     IndicatorMovingAverageOnPrice(15))

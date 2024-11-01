from indicator import Indicator
from quote import Quote
from common_utilities import CommonUtilities


class IndicatorBestBidOfferVariance(Indicator):
    """
    This class calculates a simple variance over 10 periods.
    """
    TOTAL_OBSERVATIONS = 10

    def __init__(self):
        self.__last_bid_obs = [0] * IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS
        self.__last_offer_obs = [0] * IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS
        self.__last_updated_index_bids: int = 0
        self.__last_updated_index_offers: int = 0
        self.__doc_description = "Variance of best bid and best offfer over {} periods"\
            .format(IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS)
        self.__description = "VAR_BBID_BOFFER_{}".format(IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS)

    def incoming_quote(self, quote: Quote) -> None:
        # We will update only when the best price is updated.
        way = quote.get_way()
        new_price = quote.get_price()
        is_best_px = CommonUtilities.are_equal(new_price, self._order_book.get_best_price(way))
        if is_best_px:
            self.__update_px_collection(way, quote.get_price())

    def __update_px_collection(self, way: bool, new_price: float) -> None:
        if way:
            self.__last_bid_obs[self.__last_updated_index_bids] = new_price
            self.__last_updated_index_bids += 1
            if self.__last_updated_index_bids == IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS:
                self.__last_updated_index_bids = 0
        else:
            self.__last_offer_obs[self.__last_updated_index_offers] = new_price
            self.__last_updated_index_offers += 1
            if self.__last_updated_index_offers == IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS:
                self.__last_updated_index_offers = 0

    def get_current_value(self):
        mean_bids = sum(self.__last_bid_obs) / IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS
        mean_offers = sum(self.__last_offer_obs) / IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS

        deviation_bid = [(x - mean_bids) ** 2 for x in self.__last_bid_obs]
        deviation_offer = [(x - mean_offers) ** 2 for x in self.__last_offer_obs]

        variance_bids = sum(deviation_bid) / IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS
        variance_offers = sum(deviation_offer) / IndicatorBestBidOfferVariance.TOTAL_OBSERVATIONS

        return [variance_bids, variance_offers]

    def get_return_size(self) -> tuple:
        return 2,

    def get_description(self) -> str:
        return self.__description

    def get_doc_description(self) -> str:
        return self.__doc_description

    def __deepcopy__(self, memodict={}):
        return IndicatorBestBidOfferVariance()

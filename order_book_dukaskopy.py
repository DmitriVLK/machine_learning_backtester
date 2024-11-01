from enum_classes import EnumPair
from quote import Quote
from order_book import OrderBook
import indicator
indicator: 'indicator'


class OrderBookDukascopy(OrderBook):
    """
    This is the order book that should be used for dukaskopy quotes
    """

    def __init__(self, ccy_pair: EnumPair = EnumPair.OTHER) -> None:
        """
        Initializes the instance of the OrderBook for one pair of currencies
        """
        super().__init__(ccy_pair)
        self._bid: Quote = None
        self._offer: Quote = None

    def incoming_quote(self, quote: Quote) -> None:
        """
        Function used to add a quote in the orderbook
        """
        if quote.get_way(): 
            self._bid = quote
        else:
            self._offer = quote
        # Update indicators with new values.
        each_indicator: indicator.Indicator
        for each_indicator in self._indicators:
            each_indicator.incoming_quote(quote)
    
    def get_current_snapshot(self, way: bool = None) -> list:
        """
        Returns a snapshot of the current orderbook
        """
        if way is None:
            bid_is_none = self._bid is None
            offer_is_none = self._offer is None
            if bid_is_none and offer_is_none:
                return []
            if bid_is_none:
                return [self._offer]
            if offer_is_none:
                return [self._bid]
            return [self._bid, self._offer]
        if way:
            if self._bid is None:
                return []
            return [self._bid]
        if self._offer is None:
            return []
        return [self._offer]

    def get_best_price(self, way: bool = None) -> float:
        """
        Returns the highest price of the bids or offers orders
        @return: price as a number
        """
        if way:
            bid_px = self._bid.get_price() if self._bid is not None else 0.00
            return bid_px
        return self._offer.get_price() if self._offer is not None else 0.00

    def get_best_quote(self, way: bool = None) -> Quote:
        """
        Returns the highest price of the bids or offers orders
        @return: Quote as an object. None if no quotes available
        """
        if way:
            return self._bids
        else:
            return self._offers

    def get_book_volume(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way
        @param way: None (default) if you need the whole book. True for BIDs, False for OFFERs
        @return: returns the total volume available in the book for a specific side
        """
        if way is None:
            bid_amt = self._bid.get_amount() if self._bid is not None else 0.00
            offer_amt = self._offer.get_amount() if self._offer is not None else 0.00
            return bid_amt + offer_amt
        if way:
            return self._bid.get_amount() if self._bid is not None else 0.00
        return self._offer.get_amount() if self._offer is not None else 0.00

    def get_book_volume_in_second_ccy(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way in the second currency.
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS
        """
        if way is None:
            if self._bid is None:
                bid_amt_px = 0.0
            else:
                bid_amt_px = self._bid.get_amount() * self._bid.get_price()
            if self._offer is None:
                offer_amt_px = 0.0
            else:
                offer_amt_px = self._offer.get_amount() * self._offer.get_price()
            return bid_amt_px + offer_amt_px
        if way:
            return self._bid.get_amount() * self._bid.get_price() if self._bid is not None else 0.00
        return self._offer.get_amount() * self._offer.get_price() if self._offer is not None else 0.00

    def get_quotes_count(self, way: bool = None):
        """
        Returns the count of orders in the book for a specified way
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS.
        @return: int count
        """
        if way is None:
            return 2
        return 1

    def get_executed_quotes_for_volume(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        if way:
            return [self._bid]
        return [self._offer]

    def get_executed_quotes_for_volume_in_second_ccy(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        if way:
            return [self._bid]
        return [self._offer]

    def clear_orderbook(self) -> None:
        """
        Function used to clear the collections
        """
        self._bid = None
        self._offer = None
        self._ccy_pair: EnumPair = EnumPair.OTHER

    def retrieve_order(self, quote_id) -> tuple:
        """
        Returns 2 quote if available in the order book. Different return from Ticker order book!!!
        @param quote_id: the identificator of the quote that must be looked up
        @return: tuple object corresponding to the given quote ID. None, None if nothing was found.
        """
        return ()
    
    def __repr__(self):
        return self._ccy_pair.__str__() + " DUKASKOPY order book"


    def __str__(self):
        formatted_view = ""
        formatted_view += "{:25.5f}\t{:10.2f}\n".format(self._offer.get_price(), self._offer.get_amount())
        formatted_view += "{:10.2f}{:15.5f}\t\n".format(self._bid.get_amount(), self._bid.get_price())
        return self._ccy_pair.__str__() + " order book. Orders present:\n" + formatted_view
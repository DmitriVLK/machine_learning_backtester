from abc import ABC, abstractmethod
from enum_classes import EnumPair
from quote import Quote
import indicator
indicator: 'indicator'


class OrderBook(ABC):
    """
    This is the order book that should be used for LEVEL incoming orders in one currency
    """

    def __init__(self, ccy_pair: EnumPair = EnumPair.OTHER) -> None:
        """
        Initializes the instance of the OrderBook for one pair of currencies
        """
        self._indicators: tuple = ()
        self._ccy_pair: EnumPair = ccy_pair

    def get_indicators(self) -> tuple:
        """
        Returns the list of indicators that will must be processed by the order book.
        @return: list of Indicator class's objects
        """
        return self._indicators

    def set_indicators(self, indicators: tuple) -> None:
        """
        Sets indicators list that will be processed by the order book
        @param indicators: list of Indicator class's objects
        """
        self._indicators = indicators
        each_indicator: indicator.Indicator
        for each_indicator in self._indicators:
            each_indicator.set_order_book(self)
            
    def get_ccy_pair(self) -> EnumPair:
        """
        Returns the set CCY pair of the book
        @return: OTHER if the CCY pair was not set
        """
        return self._ccy_pair

    def set_ccy_pair(self, pair: EnumPair) -> None:
        """
        Sets the set CCY pair of the book
        """
        self._ccy_pair = pair

    @abstractmethod
    def incoming_quote(self, quote: Quote) -> None:
        """
        Function used to add a quote in the orderbook
        """
        pass

    @abstractmethod
    def get_current_snapshot(self, way: bool = None) -> list:
        """
        Returns a snapshot of the current orderbook
        """
        pass

    @abstractmethod
    def get_best_price(self, way: bool = None) -> float:
        """
        Returns the highest price of the bids or offers orders
        @return: price as a number
        """
        pass

    @abstractmethod
    def get_best_quote(self, way: bool = None) -> Quote:
        """
        Returns the highest price of the bids or offers orders
        @return: Quote as an object. None if no quotes available
        """
        pass

    @abstractmethod
    def get_book_volume(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way
        @param way: None (default) if you need the whole book. True for BIDs, False for OFFERs
        @return: returns the total volume available in the book for a specific side
        """
        # The last key in the bids is the amount that is available in the order book
        pass

    @abstractmethod
    def get_book_volume_in_second_ccy(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way in the second currency.
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS
        """
        pass

    @abstractmethod
    def get_quotes_count(self, way: bool = None):
        """
        Returns the count of orders in the book for a specified way
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS.
        @return: int count
        """
        pass

    @abstractmethod
    def get_executed_quotes_for_volume(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        pass


    @abstractmethod
    def get_executed_quotes_for_volume_in_second_ccy(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        pass

    @abstractmethod
    def clear_orderbook(self) -> None:
        """
        Function used to clear the collections
        """
        pass

    @abstractmethod
    def retrieve_order(self, quote_id) -> tuple:
        """
        Retrieves a specific order from the order book by order ID
        @param quote_id: order ID of the searched order
        @return: tuple with 1 or 2 orders generally
        """
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
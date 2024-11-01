from sortedcontainers import SortedDict
from enum_classes import EnumPair
from order_book import OrderBook
from quote import Quote
import indicator
indicator: 'indicator'


class OrderBookHighFreqFx(OrderBook):
    """
    This is the order book that should be used for LEVEL incoming orders in one currency. For High frequency FX orders.
    """

    def __init__(self, ccy_pair: EnumPair = EnumPair.OTHER) -> None:
        """
        Initializes the instance of the OrderBook for one pair of currencies
        """
        super().__init__(ccy_pair)
        # These objects hold the amount <-> Quote combo
        self._bids = SortedDict()
        self._offers = SortedDict()

        self._bids_id = {}
        self._offers_id = {}

    def incoming_quote(self, quote: Quote) -> None:
        """
        Function used to add a quote in the orderbook
        """
        old_quote: Quote
        if quote.get_way(): 
            if quote.get_amount() in self._bids.keys():
                old_quote = self._bids[quote.get_amount()]
                self._bids_id.pop(old_quote.get_id_ecn())
            self._bids[quote.get_amount()] = quote
            self._bids_id[quote.get_id_ecn()] = quote
        else:
            if quote.get_amount() in self._offers.keys():
                old_quote = self._offers[quote.get_amount()]
                self._offers_id.pop(old_quote.get_id_ecn())
            self._offers[quote.get_amount()] = quote
            self._offers_id[quote.get_id_ecn()] = quote
        # Update indicators with new values.
        each_indicator: indicator.Indicator
        for each_indicator in self._indicators:
            each_indicator.incoming_quote(quote)
    
    def get_current_snapshot(self, way: bool = None) -> list:
        """
        Returns a snapshot of the current orderbook
        """
        returned_list: list = []
        if way is None:
            orders_bids = self._bids.values()
            orders_offers = self._offers.values()
            for order in orders_bids:
                returned_list.append(order)
            for order in orders_offers:
                returned_list.append(order)
            return returned_list

        if way:
            orders_bids = self._bids.values()
            for order in orders_bids:
                returned_list.append(order)
            return returned_list

        orders_offers = self._offers.values()
        for order in orders_offers:
            returned_list.append(order)
        return returned_list

    def get_best_price(self, way: bool = None) -> float:
        """
        Returns the highest price of the bids or offers orders
        @return: price as a number
        """
        if way and len(self._bids.values()) > 0:
            return self._bids.values()[0].get_price()
        elif not way and len(self._offers.values()) > 0:
            return self._offers.values()[0].get_price()
        return 0.0

    def get_best_quote(self, way: bool = None) -> Quote:
        """
        Returns the highest price of the bids or offers orders
        @return: Quote as an object. None if no quotes available
        """
        if way:
            return self._bids.peekitem(0)[1]
        else:
            return self._offers.peekitem(0)[1]

    def get_book_volume(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way
        @param way: None (default) if you need the whole book. True for BIDs, False for OFFERs
        @return: returns the total volume available in the book for a specific side
        """
        # The last key in the bids is the amount that is available in the order book
        count_of_orders: int
        if way is None:
            count_of_offers = len(self._offers.values())
            count_of_bids = len(self._bids.values())
            bids_vol = self._bids.peekitem(count_of_bids - 1)[0]
            offers_vol = self._offers.peekitem(count_of_offers - 1)[0]
            return bids_vol + offers_vol
        
        if way:
            count_of_orders = len(self._bids.values())
            return self._bids.peekitem(count_of_orders - 1)[0]
        
        count_of_orders = len(self._offers.values())
        return self._offers.peekitem(count_of_orders - 1)[0]

    def get_book_volume_in_second_ccy(self, way: bool = None) -> float:
        """
        Returns the volume of orders for a specified way in the second currency.
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS
        """
        count_of_orders: int
        worst_quote: Quote
        if way is None:
            count_of_offers = len(self._offers.values())
            count_of_bids = len(self._bids.values())
            worst_bid: Quote = self._bids.peekitem(count_of_bids - 1)[1]
            worst_offer: Quote = self._offers.peekitem(count_of_offers - 1)[1]
            counter_amt_bid = worst_bid.get_amount() * worst_bid.get_price()
            counter_amt_offer = worst_offer.get_amount() * worst_offer.get_price()
            return counter_amt_bid + counter_amt_offer

        if way:
            count_of_orders = len(self._bids.values())
            worst_quote = self._bids.peekitem(count_of_orders - 1)[1]
            return worst_quote.get_amount() * worst_quote.get_price()
        else:
            count_of_orders = len(self._offers.values())
            worst_quote = self._offers.peekitem(count_of_orders - 1)[1]
            return worst_quote.get_amount() * worst_quote.get_price()

    def get_quotes_count(self, way: bool = None):
        """
        Returns the count of orders in the book for a specified way
        @param way: None (default) if you need the whole book. True for BIDS, False for OFFERS.
        @return: int count
        """
        if way is None:
            count_bids = len(self._bids_id)
            count_offers = len(self._offers_id)
            return count_bids + count_offers
        elif way:
            return len(self._bids_id)
        
        return len(self._offers_id)

    def get_executed_quotes_for_volume(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        returned_list: list = []
        if way:
            for amount in self._bids.keys():
                if amount >= volume:
                    returned_list.append(self._bids[amount])
                    return returned_list
            count_orders = len(self._bids.keys())
            returned_list.append(self._bids.peekitem(count_orders - 1)[1])
            return returned_list
        for amount in self._offers.keys():
            if amount >= volume:
                returned_list.append(self._offers[amount])
                return returned_list
            count_orders = len(self._offers.keys())
            returned_list.append(self._offers.peekitem(count_orders - 1)[1])
            return returned_list

    def get_executed_quotes_for_volume_in_second_ccy(self, way: bool, volume: float) -> list:
        """
        Returns the executed quotes for a specific volume for a selected way. Takes into account the best price
        execution policy
        @param way: True for BIDS, False for OFFERS
        @param volume: volume to match
        """
        returned_list: list = []
        quote: Quote
        if way:
            for quote in self._bids.values():
                amount = quote.get_amount()
                sec_ccy_vol = amount * quote.get_price()
                if sec_ccy_vol >= volume:
                    returned_list.append(self._bids[amount])
                    return returned_list
            count_orders = len(self._bids.keys())
            returned_list.append(self._bids.peekitem(count_orders - 1)[1])
            return returned_list

        for quote in self._offers.values():
            amount = quote.get_amount()
            sec_ccy_vol = amount * quote.get_price()
            if sec_ccy_vol >= volume:
                returned_list.append(self._offers[amount])
                return returned_list
            count_orders = len(self._offers.keys())
            returned_list.append(self._offers.peekitem(count_orders - 1)[1])
            return returned_list

    def clear_orderbook(self) -> None:
        """
        Function used to clear the collections
        """
        self._bids = SortedDict()
        self._offers = SortedDict()
        self._bids_id = {}
        self._offers_id = {}
        self._ccy_pair: EnumPair = EnumPair.OTHER

    def retrieve_order(self, quote_id) -> tuple:
        """
        Returns 2 quote if available in the order book. Different return from Ticker order book!!!
        @param quote_id: the identificator of the quote that must be looked up
        @return: tuple object corresponding to the given quote ID. None, None if nothing was found.
        """
        bid: Quote
        offer: Quote
        if quote_id in self._bids_id.keys():
            bid = self._bids_id[quote_id]
        else:
            bid = None
        if quote_id in self._offers_id.keys():
            offer = self._offers_id[quote_id]
        else:
            offer = None
        
        return bid, offer
    
    def __repr__(self):
        return self._ccy_pair.__str__() + " order book high frequency data"


    def __str__(self):
        offer: Quote
        bid: Quote
        formatted_view = ""
        for offer in self._offers.values():
            formatted_view += "{:25.5f}\t{:10.2f}\n".format(offer.get_price(), offer.get_amount())
        for bid in self._bids.values():
            formatted_view += "{:10.2f}{:15.5f}\t\n".format(bid.get_amount(), bid.get_price())

        return self._ccy_pair.__str__() + " order book. Orders present:\n" + formatted_view
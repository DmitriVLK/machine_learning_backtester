# REPAIR CIRCULAR DEPENDENCY error
# Hide the OrderBook from compiler but allow this type to be displayed during DEV and RUN phases.
# It's not the most elegant way of handling it. Check if this will be supported in further versions of PYTHON
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Evaluates to TRUE only during runtime.
    from order_book import OrderBook
# Regular imports
from abc import ABC, abstractmethod
from quote import Quote

# Abstract Indicator class
class Indicator(ABC):

    def __init__(self, order_book: OrderBook=None):
        """
        @param order_book: the link (reference) to Order Book. This argument is not mandatory and is probably set within the order book
        with the set_order_book method.
        """
        self._order_book: OrderBook = order_book

    def set_order_book(self, order_book: OrderBook=None):
        self._order_book: OrderBook = order_book
    
    @abstractmethod
    def incoming_quote(self, quote: Quote) -> None:
        """
        Process the incoming quote
        @param quote: this is a NEW quote.
        """
        pass

    @abstractmethod
    def get_current_value(self):
        """
        Returns the current calculation value
        @return: a value of an unknown type. You might see the type using the get_return_size method.
        """
        pass

    @abstractmethod
    def get_return_size(self) -> tuple:
        """
        Returns the size of the array in get_current_value method. Could be a vector (1-D), Table (2-D) or other (N-D)
        array.
        @return: (N) for a vector, (N,M) for a Table, (N,M,L) for a 3-D etc.
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Returns a short description of the indicator for text table output
        @return: str with a text of the indicator description. For example: for a Moving average of 5
        you would output: MA_5
        """
        pass

    @abstractmethod
    def get_doc_description(self) -> str:
        """
        Returns a human-readable description of the indicator
        @return: str with a text of the indicator description. For example: for a Moving average of 5
        you would output: Moving Average 5 periods
        """
        pass

    @abstractmethod
    def __deepcopy__(self, memodict={}):
        """
        Implement a deep copy for these classes.
        @param memodict:
        @return:
        """
        pass

    def __str__(self):
        return self.get_doc_description()

    def __repr__(self):
        return self.get_description()



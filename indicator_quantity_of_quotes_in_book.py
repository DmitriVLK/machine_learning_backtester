from indicator import Indicator
from quote import Quote


class IndicatorQuantityOfQuotesInBook(Indicator):
    # Creates a Moving average indicator. Filled step by step with new values.

    def __init__(self):
        self.__doc_description = "Quantity of quotes in the book"
        self.__description = "QTY_QUOTES_ORD_BOOK_{}"

    def incoming_quote(self, quote: Quote) -> None:
        pass

    def get_current_value(self):
        return self._order_book.get_quotes_count(True) + self._order_book.get_quotes_count(False)

    def get_return_size(self) -> tuple:
        # A 1-D sized tuple requires a comma after the number
        return 1,

    def get_description(self) -> str:
        return self.__description

    def get_doc_description(self) -> str:
        return self.__doc_description

    def __deepcopy__(self, memodict={}):
        return IndicatorQuantityOfQuotesInBook()



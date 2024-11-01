from indicator import Indicator
from quote import Quote


class IndicatorMovingAverageOnPrice(Indicator):
    # Creates a Moving average indicator. Filled step by step with new values.

    def __init__(self, ma_period: int):
        super().__init__()
        self.__ma_period = ma_period
        self.__doc_description = "Price moving average {} periods".format(self.__ma_period)
        self.__description = "MA_PX_{}".format(self.__ma_period)
        self.__observations = [0.0] * ma_period
        self.__current_updated_cell = 0
        
    def incoming_quote(self, quote: Quote) -> None:
        # Mid calculation:
        best_bid = self._order_book.get_best_price(True)
        best_offer = self._order_book.get_best_price(False)
        mid = best_bid + best_offer
        mid /= 2.0
        self.__observations[self.__current_updated_cell] = mid
        self.__current_updated_cell += 1
        if self.__current_updated_cell == self.__ma_period:
            self.__current_updated_cell = 0

    def get_current_value(self):
        sum = 0.0
        for obs in self.__observations:
            sum += obs
        return sum / self.__ma_period

    def get_return_size(self) -> tuple:
        # A 1-D sized tuple requires a comma after the number
        return 1,

    def get_description(self) -> str:
        return self.__description

    def get_doc_description(self) -> str:
        return self.__doc_description

    def __deepcopy__(self, memodict={}):
        return IndicatorMovingAverageOnPrice(self.__ma_period)


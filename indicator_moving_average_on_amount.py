from indicator import Indicator
from quote import Quote


class IndicatorMovingAverageOnAmount(Indicator):
    # Creates a Moving average indicator. Filled step by step with new values.

    def __init__(self, ma_period: int):
        self.__ma_period: int = ma_period
        # Initialize the array to 0s
        self.__observations: list = [0] * self.__ma_period
        self.__next_updated_value: int = 0
        self.__doc_description = "Amount moving average {} periods".format(self.__ma_period)
        self.__description = "MA_AMT_{}".format(self.__ma_period)

    def incoming_quote(self, quote: Quote) -> None:
        self.__observations[self.__next_updated_value] = quote.get_amount()
        self.__next_updated_value += 1
        # Reset when we hit the MAX
        if self.__next_updated_value == self.__ma_period:
            self.__next_updated_value = 0

    def get_current_value(self):
        return sum(self.__observations) / self.__ma_period

    def get_return_size(self) -> tuple:
        # A 1-D sized tuple requires a comma after the number
        return 1,

    def get_description(self) -> str:
        return self.__description

    def get_doc_description(self) -> str:
        return self.__doc_description

    def __deepcopy__(self, memodict={}):
        return IndicatorMovingAverageOnAmount(self.__ma_period)



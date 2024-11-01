import constants


class Position:
    def __init__(self, is_long_position: bool, price_bid: float, price_offer: float, current_time: int):
        """Creates the Position object and initializes the starting parameters for it.

        Args:
            is_long_position (bool): True if it's a LONG position. False if it's a SHORT position.
            price_bid (float): currently observed best bid on the market.
            price_offer (float): currently observer best offer on the market.
            current_time (int): currently observed time on the clock.
        """

        self.__is_long_position = is_long_position
        if is_long_position:
            self.__opening_price: float = price_offer
            self.__last_update_on_closing_price = price_bid
        else:
            self.__opening_price: float = price_bid
            self.__last_update_on_closing_price = price_offer
        # We lose the spread immediately
        self.__max_draw_down: float = price_bid - price_offer
        self.__position_is_closed: bool = False
        self.__opening_time: int = current_time
        self.__last_price_update_time: int = self.__opening_time
        self.__max_draw_down: float = 0.0
        self.__updates_during_lifetime = 0

    def actualize(self, price_update_bid: float, price_update_offer: float, new_time: int) -> None:
        if not self.__position_is_closed:
            self.__updates_during_lifetime += 1
            self.__last_price_update_time = new_time
            # Stores the current PnL in bps
            delta_price: float
            # if the model say us to buy or sell
            # delta price is different with respect to a short position et long position
            if self.__is_long_position:
                delta_price = price_update_bid - self.__opening_price
            else:
                delta_price = self.__opening_price - price_update_offer
            # self.__price_collection.append(self.__current_price)

            duration = self.__last_price_update_time - self.__opening_time
            # Close position with condition price and time
            if (delta_price > constants.TAKE_PROFIT or delta_price < constants.STOP_LOSS
                    or duration >= constants.MAX_TIME_POSITION):
                self.close_position(price_update_bid, price_update_offer)

            # Get maximum draw down of position
            if delta_price < self.__max_draw_down:
                self.__max_draw_down = delta_price

    def close_position(self, price_bid: float, price_offer) -> None:
        self.__position_is_closed = True
        if self.__is_long_position:
            self.__last_update_on_closing_price = price_bid
        else:
            self.__last_update_on_closing_price = price_offer

    def is_long_position(self) -> bool:
        """ Returns True if it's a long position. False if it's a  short position.

        Returns:
            bool: True if it's a BUY. False if it's a  SELL.
        """
        return self.__is_long_position

    def get_variation_metric(self) -> float:
        """
        This variation metric represents the quantity of movements in the position during the quantity of seconds it's
        been alive
        @return: float average quantity of movements in the position during the time it was alive.
        """
        if self.get_duration() == 0:
            return 0.0
        total_duration_seconds = self.get_duration() / constants.NANOS_IN_ONE_SECOND
        return self.__updates_during_lifetime / total_duration_seconds

    def get_opening_time(self) -> int:
        return self.__opening_time

    def get_opening_price(self) -> float:
        return self.__opening_price

    def get_closing_price(self) -> float:
        return self.__last_update_on_closing_price

    def get_duration(self) -> int:
        """
        This is a duration in nanos
        @return:
        """
        return self.__last_price_update_time - self.__opening_time

    def is_position_closed(self) -> bool:
        """
        If returns True, means the position has been closed/handled.
        @return:
        """
        return self.__position_is_closed

    def get_max_draw_down(self) -> float:
        """
        The MAX dd is a negative metric in this code. A Max DD equal to ""-5"" means that the maximum loss was of 5 units
        @return: an absolute float with the amount lost. The Max DD should always be populated with a minimum of
        the initial spread.
        """
        return self.__max_draw_down

    def get_position_pnl(self) -> float:
        if self.__is_long_position:
            return self.__last_update_on_closing_price - self.__opening_price
        return self.__opening_price - self.__last_update_on_closing_price

    def get_calmar_ratio(self) -> float:
        if self.__max_draw_down < 0.0:
            return self.get_position_pnl() / (-self.__max_draw_down)
        else:
            return self.get_position_pnl()



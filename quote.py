from enum_classes import EnumCcy, EnumPair


class Quote:
    # Static field with incrementing ID for the current quote.
    # This variable will be incremented after each call of TradeSituation.generate_next_id().
    # It is used to populate __quote_id.
    __common_quote_id: int = 0

    def __init__(self, quote_id_arg, currency1_arg, currency2_arg, local_timestamp_arg: int, ecn_timestamp_arg: int,
                 amount_arg: float = None, minqty_arg: float = None, lotsize_arg: float = None,
                 price_arg: float = None, way_arg: str = 'B'):
        """
        Initializes the instance of the Quote.
        """
        self.__quote_internal_id = Quote.generate_next_id()
        # try converting to int it can be stored as INT
        if quote_id_arg is str and quote_id_arg.isdigit():
            self.__quote_ecn_id = int(quote_id_arg)
        else:
            self.__quote_ecn_id = quote_id_arg

        # If it's already and EnumCcy, copy the variable. Otherwise, recognize the str into the correct EnumCcy
        if isinstance(currency1_arg, EnumCcy):
            self.__ccy1 = currency1_arg
        else:
            self.__ccy1 = EnumCcy[currency1_arg]

        if isinstance(currency1_arg, EnumCcy):
            self.__ccy2 = currency2_arg
        else:
            self.__ccy2 = EnumCcy[currency2_arg]
        if self.__ccy1 == EnumCcy.OTH and self.__ccy2 == EnumCcy.OTH:
            self.__ccy_pair = EnumPair.OTHER
        else:
            self.__ccy_pair = EnumPair[self.__ccy1.name + self.__ccy2.name]
        self.__local_timestamp = int(local_timestamp_arg)
        self.__ecn_timestamp = int(ecn_timestamp_arg)
        self.__amount = float(amount_arg)
        self.__minimum_quantity = float(minqty_arg)
        self.__lot_size = float(lotsize_arg)
        self.__price = float(price_arg)
        if way_arg =='B':
            self.__order_way: bool = True
        elif way_arg =='S':
            self.__order_way: bool = False
        elif type(way_arg) == bool:
            self.__order_way: bool = way_arg
        else:
            raise AttributeError("Please input wither a str of a bool for the WAY attr")

    def get_id_internal(self) -> int:
        """
        Returns the ID of this specific quote
        """
        return self.__quote_internal_id

    def get_id_ecn(self):
        """
        Not strongly typed return. Could be an INT or a STR
        @return: ID as provided by ECN
        """
        return self.__quote_ecn_id

    def get_ccy1(self) -> EnumCcy:
        return self.__ccy1

    def get_ccy2(self) -> EnumCcy:
        return self.__ccy2

    def get_pair(self) -> EnumPair:
        """
        Returns the currency pair
        """
        return self.__ccy_pair

    def get_local_timestamp(self) -> int:
        # Usually counted in nanoseconds
        if self.__local_timestamp:
            return self.__local_timestamp
        print("A local timestamp 0 was returned. Please check if this is normal.")
        return 0

    def get_ecn_timestamp(self) -> int:
        if self.__ecn_timestamp:
            return self.__ecn_timestamp
        return 0

    def get_amount(self) -> float:
        if self.__amount:
            return self.__amount
        print("An amount equal to 0.00 was returned. Please check if this is normal.")
        return 0.00

    def get_min_quantity(self) -> float:
        if self.__minimum_quantity:
            return self.__minimum_quantity
        return 0.00

    def get_lot_size(self) -> float:
        if self.__lot_size:
            return self.__lot_size
        return 0.00

    def get_price(self) -> float:
        if self.__price:
            return self.__price
        print("A price equal to 0.00 was returned. Please check if this is normal.")
        return 0.00

    def get_way(self) -> bool:
        return self.__order_way

    @staticmethod
    def generate_next_id():
        Quote.__common_quote_id += 1
        return Quote.__common_quote_id

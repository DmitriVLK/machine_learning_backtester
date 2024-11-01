from enum import Enum

class EnumOrderBook(Enum):
    HIGH_FREQ_FX = 1
    DUKASKOPY = 2


class EnumHyperParamsOptimization(Enum):
    BAYESIAN = 1
    GRID = 2
    RANDOM = 3
    NONE = 4


class EnumCcy(Enum):
    """
    Enum with currencies
    """

    GBP = 1
    AUD = 2
    USD = 3
    EUR = 4
    JPY = 5
    CHF = 6
    NZD = 7
    NOK = 8
    SEK = 9
    CAD = 10
    # OTHER
    OTH = 99


class EnumPair(Enum):
    """
    Enum with currency pairs
    """

    GBPUSD = 1
    EURUSD = 2
    EURJPY = 3
    GBPAUD = 4
    USDCHF = 5
    USDJPY = 6
    NZDUSD = 7
    AUDUSD = 8
    NOKSEK = 9
    USDCAD = 10
    OTHER = 99

    def get_ccy_first(self):
        if self.value == 99:
            return EnumCcy.OTH
        return EnumCcy[self.name[0:3]]

    def get_ccy_second(self):
        if self.value == 99:
            return EnumCcy.OTH
        return EnumCcy[self.name[3:6]]

    def get_ccy_pair_with_slash(self):
        if self.value == 99:
            return 'OTH/OTH'
        return self.name[0:3] + '/' + self.name[3:6]
    
    def __str__(self):
        return self.get_ccy_pair_with_slash()
    
    def __repr__(self):
        return self.__str__()

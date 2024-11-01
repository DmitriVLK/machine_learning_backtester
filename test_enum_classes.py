from unittest import TestCase
from enum_classes import EnumCcy, EnumPair


class TestEnumClasses(TestCase):

    def test_ccy_pair(self):
        ccy_pair = EnumPair.EURUSD
        self.assertEqual(EnumCcy.EUR, ccy_pair.get_ccy_first())
        self.assertEqual(EnumCcy.USD, ccy_pair.get_ccy_second())
        self.assertEqual('EUR/USD', ccy_pair.get_ccy_pair_with_slash())

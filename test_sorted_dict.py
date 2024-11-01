from unittest import TestCase
from sortedcontainers import SortedDict
from common_utilities import asc_key_fn, dsc_key_fn


class TestCommonUtilities(TestCase):
    # This code tests the capabilities of the SortedDict class provided by a 3d party developer

    def test_sort_asc(self):
        """
        Function that test to reads the CSV lines for one currency
        """
        collection = SortedDict(asc_key_fn)
        collection[1] = 'a'
        collection[2] = 'b'
        collection[3] = 'c'

        self.assertEqual((1, 'a'), collection.popitem(0))
        self.assertEqual((2, 'b'), collection.popitem(0))
        self.assertEqual((3, 'c'), collection.popitem(0))

    def test_sort_dsc(self):
        """
        Function that test to reads the CSV lines for one currency
        """
        collection = SortedDict(dsc_key_fn)
        collection[1] = 'a'
        collection[2] = 'b'
        collection[3] = 'c'

        self.assertEqual((3, 'c'), collection.popitem(0))
        self.assertEqual((2, 'b'), collection.popitem(0))
        self.assertEqual((1, 'a'), collection.popitem(0))

    def test_peek_item_asc(self):
        """
        Function that test to reads the CSV lines for one currency
        """
        collection = SortedDict(asc_key_fn)
        collection[1] = 'a'
        collection[2] = 'b'
        collection[3] = 'c'

        self.assertEqual((1, 'a'), collection.peekitem(0))
        self.assertEqual(1, collection.peekitem(0)[0])
        self.assertEqual('a', collection.peekitem(0)[1])

    def test_peek_item_dsc(self):
        """
        Function that test to reads the CSV lines for one currency
        """
        collection = SortedDict(dsc_key_fn)
        collection[1] = 'a'
        collection[2] = 'b'
        collection[3] = 'c'

        self.assertEqual((3, 'c'), collection.peekitem(0))
        self.assertEqual(3, collection.peekitem(0)[0])
        self.assertEqual('c', collection.peekitem(0)[1])



from unittest import TestCase

from feature_to_label_collection import FeatureToLabelCollection


class TestFeatureToLabelCollection(TestCase):

    def test_constructor(self):
        collection = FeatureToLabelCollection(100, (0.005, 0.006))

    def test_put(self):
        collection = FeatureToLabelCollection(100, (0.005, 0.006))
        collection.put(1000, 1.005, 1.006, (1, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1000, 1.005, 1.006)

    def test_check_profit_levels_on_active_cells(self):
        # Check EXCEL calculator FeatureToLabelCollectionResults.xlsx for calculation explanation.

        profit_levels = (0.005, 0.006)
        profit_levels_length = len(profit_levels)
        collection = FeatureToLabelCollection(5, profit_levels)
        append_features_labels = [[[] for i in range(profit_levels_length)], list()]

        collection.put(1000, 1.005, 1.006, (1, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1000, 1.005, 1.006)
        collection.put(1001, 1.004, 1.008, (2, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1001, 1.004, 1.008)
        collection.put(1002, 1.002, 1.003, (3, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1002, 1.002, 1.003)
        collection.put(1003, 1.006, 1.007, (4, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1003, 1.006, 1.007)

        # no ready cells here
        reported_cell = collection.get_ready_calculations()
        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]

        append_features_labels[1] += reported_cell[1]

        reported_labels = reported_cell[0]
        reported_features = reported_cell[1]
        self.assertEqual(0, len(reported_labels))
        self.assertEqual(0, len(reported_features))

        collection.put(1004, 1.011, 1.015, (5, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1004, 1.011, 1.015)

        # take profit hit on BUY, but timer didn't elapse
        reported_cell = collection.get_ready_calculations()

        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]
        append_features_labels[1] += reported_cell[1]

        self.assertEqual(0, len(reported_cell[0]))

        # This price level triggers SELL on line timer 1004 0.006 profit level (BID SIDE 1.011 - 0.006 = 1.005)
        collection.put(1005, 1.0012, 1.002, (6, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1005, 1.0012, 1.002)

        # Timer elapsed for 1000: check the cell
        reported_cell = collection.get_ready_calculations()

        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]
        append_features_labels[1] += reported_cell[1]

        reported_labels = reported_cell[0]
        reported_features = reported_cell[1]
        self.assertEqual(2, len(reported_cell))
        self.assertEqual(2, len(reported_labels))
        self.assertEqual(1, len(reported_features))

        # 1000
        self.assertEqual([False, True], reported_labels[0][0])
        self.assertEqual([False, False], reported_labels[1][0])
        self.assertEqual((1, 2, 3, 4, 5), reported_features[0])

        # This price level triggers SELL on line timer 1004 0.005 profit level
        collection.put(1006, 1.0061, 1.007, (7, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1006, 1.0061, 1.007)
        # This price level triggers BUY on line timer 1004 0.005 profit level
        collection.put(1007, 1.02, 1.021, (8, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1007, 1.02, 1.021)

        # Timer elapsed for 1000, 1001, 1002: check the cell
        reported_cell = collection.get_ready_calculations()

        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]
        append_features_labels[1] += reported_cell[1]

        reported_labels = reported_cell[0]
        reported_features = reported_cell[1]
        self.assertEqual(2, len(reported_cell))
        self.assertEqual(2, len(reported_labels))
        self.assertEqual(2, len(reported_labels[0]))
        self.assertEqual(2, len(reported_features))

        # 1001
        self.assertEqual([False, False], reported_labels[0][0])
        self.assertEqual([False, False], reported_labels[1][0])
        self.assertEqual((2, 2, 3, 4, 5), reported_features[0])
        # 1002
        self.assertEqual([False, True], reported_labels[0][1])
        self.assertEqual([False, True], reported_labels[1][1])
        self.assertEqual((3, 2, 3, 4, 5), reported_features[1])

        collection.put(1008, 1.01, 1.012, (9, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1008, 1.01, 1.012)
        collection.put(1009, 1.005, 1.007, (10, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1009, 1.005, 1.007)

        # Timer elapsed for [1000-1004]: check the cell 1004
        reported_cell = collection.get_ready_calculations()

        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]
        append_features_labels[1] += reported_cell[1]

        reported_labels = reported_cell[0]
        reported_features = reported_cell[1]
        self.assertEqual(2, len(reported_cell))
        self.assertEqual(2, len(reported_labels))
        self.assertEqual(2, len(reported_labels[0]))
        self.assertEqual(2, len(reported_features))

        # 1003
        self.assertEqual([False, True], reported_labels[0][0])
        self.assertEqual([False, True], reported_labels[1][0])
        self.assertEqual((4, 2, 3, 4, 5), reported_features[0])
        # 1004
        self.assertEqual([True, True], reported_labels[0][1])
        self.assertEqual([True, False], reported_labels[1][1])
        self.assertEqual((5, 2, 3, 4, 5), reported_features[1])

        # Note that this addition isn't used to calculate the TRIGGERS. It's purely to report the values.
        # Because the timer is way ahead.
        collection.put(1100, 1.0012, 1.002, (101, 2, 3, 4, 5))
        collection.check_profit_levels_on_active_cells(1100, 1.0012, 1.002)

        # Check all the reported cells
        reported_cell = collection.get_ready_calculations()

        for level in range(min(profit_levels_length, len(reported_cell[0]))):
            append_features_labels[0][level] += reported_cell[0][level]
        append_features_labels[1] += reported_cell[1]

        reported_labels = reported_cell[0]
        reported_features = reported_cell[1]

        self.assertEqual(2, len(reported_cell))
        self.assertEqual(2, len(reported_labels))
        self.assertEqual(5, len(reported_labels[0]))
        self.assertEqual(5, len(reported_features))

        # 1005
        self.assertEqual([False, True], reported_labels[0][0])
        self.assertEqual([False, True], reported_labels[1][0])
        self.assertEqual((6, 2, 3, 4, 5), reported_features[0])
        # 1006
        self.assertEqual([False, True], reported_labels[0][1])
        self.assertEqual([False, True], reported_labels[1][1])
        self.assertEqual((7, 2, 3, 4, 5), reported_features[1])
        # 1007
        self.assertEqual([True, False], reported_labels[0][2])
        self.assertEqual([True, False], reported_labels[1][2])
        self.assertEqual((8, 2, 3, 4, 5), reported_features[2])
        # 1008
        self.assertEqual([False, False], reported_labels[0][3])
        self.assertEqual([False, False], reported_labels[1][3])
        self.assertEqual((9, 2, 3, 4, 5), reported_features[3])
        # 1009
        self.assertEqual([False, False], reported_labels[0][4])
        self.assertEqual([False, False], reported_labels[1][4])
        self.assertEqual((10, 2, 3, 4, 5), reported_features[4])

        self.assertEqual(10, len(append_features_labels[0][0]))
        self.assertEqual(10, len(append_features_labels[0][1]))
        self.assertEqual(10, len(append_features_labels[1]))


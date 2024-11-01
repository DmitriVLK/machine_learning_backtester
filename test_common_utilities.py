import os
from unittest import TestCase
from common_utilities import CommonUtilities
from datetime import datetime

class TestCommonUtilities(TestCase):

    def test_num_of_rows(self):
        """
        Function that test to reads the CSV lines for one currency
        """
        file_name: str = "test_level_format.csv"
        count = CommonUtilities.num_of_rows(file_name)
        self.assertEqual(50000, count)

    def test_num_of_csvs(self):
        """
        Function that checks how many CSVs there is in this dir
        """
        all_csvs = CommonUtilities.get_files_list_of_a_type_in_dir(".")
        self.assertEqual(3, len(all_csvs))
        all_csvs = CommonUtilities.get_files_list_of_a_type_in_dir()
        self.assertEqual(3, len(all_csvs))
        all_csvs = CommonUtilities.get_files_list_of_a_type_in_dir(".", ".csv")
        self.assertEqual(3, len(all_csvs))
        all_csvs_sorted = sorted(all_csvs)
        self.assertEqual("test_level_format.csv", all_csvs_sorted[0])
        all_csvs = CommonUtilities.get_files_list_of_a_type_in_dir(os.getcwd())
        self.assertEqual(3, len(all_csvs))

    def test_split_quote(self):
        """
        Function that tries to deserialize a string.
        """
        line = "M;8444869899270648938;USD/CHF;30909333430072;1486128909144222;2000000.00;0.00;0.00;0.99393"
        expected_list = ['M', '8444869899270648938', 'USD', 'CHF', '30909333430072', '1486128909144222', '2000000.00',
                         '0.00', '0.00', '0.99393']
        effective_list = CommonUtilities.split_quote_line_to_list(line)
        self.assertEqual(expected_list, effective_list)

    def test_equal_numbers(self):
        number1 = 1.0000001
        number2 = 1.0000001
        self.assertTrue(CommonUtilities.are_equal(number1, number2))
        number1 = 1.0000001
        number2 = 1.0000002
        self.assertFalse(CommonUtilities.are_equal(number1, number2))


    def test_generate_date_method(self):
        generated = CommonUtilities.generate_file_name_base()

        test_date: datetime = datetime.today()
        # Best way to store files: these can be sorted easily in the file system.
        date_format: str = "%Y-%m-%d-%H-%M"
        date_str = test_date.strftime(date_format)
        file_name_local = date_str + "_{}.pkl"

        self.assertEqual(file_name_local, generated)

    def test_generate_date_method_2(self):
        generated = CommonUtilities.generate_file_name_base(".csv")

        test_date: datetime = datetime.today()
        # Best way to store files: these can be sorted easily in the file system.
        date_format: str = "%Y-%m-%d-%H-%M"
        date_str = test_date.strftime(date_format)
        file_name_local = date_str + "_{}.csv"

        self.assertEqual(file_name_local, generated)
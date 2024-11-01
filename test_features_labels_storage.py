import os
from os import remove
from os.path import exists
from datetime import datetime
from unittest import TestCase

from features_labels_storage import FeaturesLabelsStorage


class TestFeaturesLabelsStorage(TestCase):


    def test_store(self):
        test_date: datetime = datetime.today()
        # Best way to store files: these can be sorted easily in the file system.
        date_format: str = "%Y-%m-%d-%H-%M"
        date_str = test_date.strftime(date_format)
        file_name_local = date_str + "_0.pkl"

        file_chars = None, file_name_local

        stored = FeaturesLabelsStorage.store_ready_features_labels(None, file_chars, None)
        self.assertTrue(exists(stored))
        # Remove test file
        remove(stored)

        stored2 = FeaturesLabelsStorage.store_ready_features_labels(None, file_chars, None, os.getcwd())
        self.assertTrue(exists(stored2))
        # Remove test file
        remove(stored2)

    def test_restore(self):
        test_date: datetime = datetime.today()
        # Best way to store files: these can be sorted easily in the file system.
        date_format: str = "%Y-%m-%d-%H-%M"
        date_str = test_date.strftime(date_format)
        file_name_local = date_str + "_0.pkl"

        file_chars = None, file_name_local

        stored = FeaturesLabelsStorage.store_ready_features_labels(None, file_chars, None)
        self.assertTrue(exists(stored))

        restored = FeaturesLabelsStorage.restore_ready_features_labels(0)
        self.assertIsNotNone(restored)
        # Remove test file
        remove(stored)

    def test_restore_with_file_dir(self):
        test_date: datetime = datetime.today()
        # Best way to store files: these can be sorted easily in the file system.
        date_format: str = "%Y-%m-%d-%H-%M"
        date_str = test_date.strftime(date_format)
        file_name_local = date_str + "_0.pkl"

        file_chars = None, file_name_local

        stored = FeaturesLabelsStorage.store_ready_features_labels(None, file_chars, None, directory_base=os.getcwd())
        self.assertTrue(exists(stored))

        restored = FeaturesLabelsStorage.restore_ready_features_labels(0, directory_base=os.getcwd())
        self.assertIsNotNone(restored)
        # Remove test file
        remove(stored)



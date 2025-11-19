import sys
import os
import unittest
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('.'))

from feed_generation.feed_generator import generate_rss
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

class TestRSS(unittest.TestCase):
    def test_generate_rss(self):
        items = [
            {
                'bvid': 'BV1xx411c7mD',
                'title': 'Test Video',
                'url': 'https://www.bilibili.com/video/BV1xx411c7mD',
                'desc': 'Test Description',
                'score': 8,
                'tags': ['AI', 'Tech'],
                'analysis': 'Good video',
                'pubdate': 1678888888
            }
        ]
        metadata = {
            'title': 'Test Feed',
            'description': 'Test Description',
            'link': 'https://example.com'
        }
        success, msg = generate_rss(items, 'test_output.xml', metadata)
        self.assertTrue(success)
        self.assertTrue(os.path.exists('test_output.xml'))
        
        # Clean up
        if os.path.exists('test_output.xml'):
            os.remove('test_output.xml')

    def test_ui_import(self):
        # Just check if we can instantiate MainWindow without error
        app = QApplication(sys.argv)
        try:
            window = MainWindow()
            self.assertIsNotNone(window)
        except Exception as e:
            self.fail(f"Failed to instantiate MainWindow: {e}")

if __name__ == '__main__':
    unittest.main()

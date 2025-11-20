import sys
import os
import unittest
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.models import ScrapedItem
from app.rss.feed_gen import RSSGenerator
from app.ai.client import AIProcessor
from unittest.mock import MagicMock, patch

class TestAdvancedFeatures(unittest.TestCase):
    def test_rss_filtering(self):
        # Create items with different scores and risks
        item_high_quality = ScrapedItem(
            url="http://example.com/1",
            title="High Quality",
            content="Good content",
            publish_date=datetime.now(),
            ai_score=90,
            risk_level="Low"
        )
        item_low_quality = ScrapedItem(
            url="http://example.com/2",
            title="Low Quality",
            content="Bad content",
            publish_date=datetime.now(),
            ai_score=40,
            risk_level="Low"
        )
        item_high_risk = ScrapedItem(
            url="http://example.com/3",
            title="High Risk",
            content="Risky content",
            publish_date=datetime.now(),
            ai_score=80,
            risk_level="High"
        )
        
        generator = RSSGenerator()
        # Filter out score < 60 and risk == High
        generator.add_items([item_high_quality, item_low_quality, item_high_risk], min_score=60, filter_high_risk=True)
        
        rss_xml = generator.generate_rss()
        
        # Verify filtering (Low quality item should be absent)
        self.assertNotIn("Low Quality", rss_xml)
        
        # Verify content (High quality item should be present)
        self.assertIn("High Quality", rss_xml)
        self.assertIn("90", rss_xml) # Check score
        self.assertIn("Low", rss_xml) # Check risk level

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test_key"})
    @patch('app.ai.client.OpenAI')
    def test_ai_scoring_parsing(self, mock_openai):
        # Mock AI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "summary": "Test Summary",
            "sentiment": "Positive",
            "score": 85,
            "risk_level": "Low"
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        processor = AIProcessor()
        result = processor.analyze("test content")
        
        self.assertEqual(result['score'], 85)
        self.assertEqual(result['risk_level'], "Low")

if __name__ == '__main__':
    unittest.main()

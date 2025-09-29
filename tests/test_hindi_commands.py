import unittest
import asyncio
from core.nlp_engine import NLPEngine
from core.voice_engine import VoiceEngine

class TestHindiCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nlp_engine = NLPEngine()
        cls.voice_engine = VoiceEngine()
        
    def run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)
    
    def test_basic_commands(self):
        """Test basic Hindi command processing"""
        test_cases = [
            {
                "command": "क्रोम खोलो",
                "expected_intent": "open_application",
                "expected_entities": [{"type": "application", "normalized": "chrome"}]
            },
            {
                "command": "वर्ड बंद करो",
                "expected_intent": "close_application",
                "expected_entities": [{"type": "application", "normalized": "word"}]
            },
            {
                "command": "सिस्टम स्टेटस बताओ",
                "expected_intent": "get_info",
                "expected_entities": []
            }
        ]
        
        for case in test_cases:
            result = self.run_async(self.nlp_engine.process_command(case["command"]))
            
            # Check intent
            self.assertEqual(
                result["intent"]["name"],
                case["expected_intent"],
                f"Failed intent detection for: {case['command']}"
            )
            
            # Check entities
            for expected_entity in case["expected_entities"]:
                entity_found = False
                for entity in result["entities"]:
                    if (entity["type"] == expected_entity["type"] and
                        entity["normalized"] == expected_entity["normalized"]):
                        entity_found = True
                        break
                self.assertTrue(
                    entity_found,
                    f"Entity not found in command: {case['command']}"
                )
    
    def test_complex_commands(self):
        """Test complex Hindi commands with multiple entities"""
        test_cases = [
            {
                "command": "शाम 6 बजे यूट्यूब खोलो और म्यूजिक प्ले करो",
                "expected_intents": ["open_application", "play_media"],
                "expected_entities": [
                    {"type": "time", "normalized": "evening 6:00"},
                    {"type": "application", "normalized": "youtube"},
                    {"type": "application", "normalized": "spotify"}
                ]
            },
            {
                "command": "कल सुबह 9 बजे मीटिंग का रिमाइंडर सेट करो",
                "expected_intent": "set_reminder",
                "expected_entities": [
                    {"type": "date", "normalized": "tomorrow"},
                    {"type": "time", "normalized": "morning 9:00"}
                ]
            }
        ]
        
        for case in test_cases:
            result = self.run_async(self.nlp_engine.process_command(case["command"]))
            
            # For single intent commands
            if "expected_intent" in case:
                self.assertEqual(
                    result["intent"]["name"],
                    case["expected_intent"],
                    f"Failed intent detection for: {case['command']}"
                )
            
            # Check all expected entities are found
            for expected_entity in case["expected_entities"]:
                entity_found = False
                for entity in result["entities"]:
                    if (entity["type"] == expected_entity["type"] and
                        entity["normalized"] == expected_entity["normalized"]):
                        entity_found = True
                        break
                self.assertTrue(
                    entity_found,
                    f"Entity not found in command: {case['command']}"
                )
    
    def test_voice_output(self):
        """Test Hindi voice output"""
        test_texts = [
            "नमस्ते, मैं जार्विस हूं।",
            "सिस्टम स्टेटस सामान्य है।",
            "आपका कमांड प्रोसेस किया जा रहा है।"
        ]
        
        for text in test_texts:
            try:
                self.voice_engine.speak(text)
                # If we reach here, no exception was raised
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Voice output failed for: {text} with error: {str(e)}")

if __name__ == '__main__':
    unittest.main()
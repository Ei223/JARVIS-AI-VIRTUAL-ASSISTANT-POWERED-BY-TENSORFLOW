import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification
from typing import Dict, Any, List, Optional
import json
import os
import re
import logging

class NLPEngine:
    def __init__(self):
        """Initialize the NLP engine with multilingual models"""
        print("Initializing NLP Engine...")
        
        # Initialize variables
        self.mbart_model = None
        self.mbart_tokenizer = None
        self.mbart_model_name = "facebook/mbart-large-50-many-to-many-mmt"
        
        # Don't load models in __init__, they'll be loaded when needed
        print("NLP Engine initialized (models will be loaded when needed).")
            
    def _setup_nlp(self):
        """Setup NLP models in the background"""
        try:
            if not self.mbart_model:
                self.mbart_model_name = "facebook/mbart-large-50-many-to-many-mmt"
                print("Loading tokenizer...")
                self.mbart_tokenizer = AutoTokenizer.from_pretrained(self.mbart_model_name)
                print("Loading model...")
                self.mbart_model = AutoModelForSeq2SeqLM.from_pretrained(self.mbart_model_name, torch_dtype=torch.float32)
                
                # Move model to GPU if available
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                print(f"Using device: {device}")
                self.mbart_model = self.mbart_model.to(device)
                print("Successfully loaded mBART-50 for Hindi conversation.")
        except Exception as e:
            logging.error(f"Error loading NLP models: {str(e)}")
            print(f"Warning: Error loading NLP models: {str(e)}")
            # Don't raise, let the system continue with limited functionality
    def generate_conversational_response(self, user_text: str, source_lang: str = "hi_IN", target_lang: str = "hi_IN") -> str:
        """Generate a conversational response in Hindi using mBART-50."""
        try:
            tokenizer = self.mbart_tokenizer
            model = self.mbart_model
            # Set language codes for Hindi
            tokenizer.src_lang = source_lang
            inputs = tokenizer(user_text, return_tensors="pt")
            generated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.lang_code_to_id[target_lang],
                max_length=128,
                num_beams=4,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            response = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            return response
        except Exception as e:
            logging.error(f"Conversational response error: {str(e)}")
            return "माफ़ कीजिए, मैं अभी उत्तर नहीं दे सकता।"
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text with enhanced Hindi support"""
        entities = []
        
        # Enhanced application patterns with Hindi alternatives
        app_patterns = [
            # Web browsers
            r'(chrome|क्रोम|गूगल क्रोम|ब्राउज़र|इंटरनेट)',
            # Media and entertainment
            r'(youtube|यूट्यूब|वीडियो)',
            r'(spotify|स्पॉटिफाई|संगीत|म्यूजिक)',
            r'(vlc|वीएलसी|मीडिया प्लेयर)',
            # Office applications
            r'(word|वर्ड|शब्द|डॉक्यूमेंट)',
            r'(excel|एक्सेल|स्प्रेडशीट)',
            r'(powerpoint|पावरपॉइंट|प्रेजेंटेशन)',
            # System applications
            r'(calculator|कैलकुलेटर|गणक)',
            r'(notepad|नोटपैड|एडिटर)',
            r'(explorer|एक्सप्लोरर|फ़ाइल)',
            # Communication apps
            r'(whatsapp|वाट्सएप|मैसेंजर)',
            r'(skype|स्काइप|वीडियो कॉल)',
            r'(telegram|टेलीग्राम)'
        ]
        
        # Enhanced time patterns with Hindi time formats
        time_patterns = [
            # Digital time formats
            r'(\d{1,2}(?::\d{2})?(?:\s*(?:बजे|बज गए|am|pm))?)',
            # Time periods
            r'(सुबह|प्रातः|दोपहर|शाम|संध्या|रात|मध्यरात्री)',
            # Relative time
            r'(आधा घंटा|एक घंटा|दो घंटे|\d+\s*घंटे)',
            r'(कुछ मिनट|थोड़ी देर|\d+\s*मिनट)',
            # Specific times
            r'(सूर्योदय|सूर्यास्त|भोर|मध्याह्न)'
        ]
        
        # Date and duration patterns
        date_patterns = [
            r'(आज|कल|परसों|बीता हुआ|अगला|पिछला)',
            r'(सोमवार|मंगलवार|बुधवार|गुरुवार|शुक्रवार|शनिवार|रविवार)',
            r'(\d{1,2}\s*(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर))'
        ]
        
        # Location patterns
        location_patterns = [
            r'(घर|ऑफिस|कार्यालय|दफ्तर|स्कूल|बाहर|अंदर)',
            r'(कमरा|रूम|हॉल|किचन|बाथरूम)'
        ]
        
        # Extract applications
        for pattern in app_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": "application",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "normalized": self._normalize_app_name(match.group())
                })
        
        # Extract time references
        for pattern in time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": "time",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "normalized": self._normalize_time(match.group())
                })
        
        # Extract dates
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": "date",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "normalized": self._normalize_date(match.group())
                })
        
        # Extract locations
        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": "location",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
        
    def _normalize_app_name(self, app_name: str) -> str:
        """Normalize application names to standard English forms"""
        hindi_to_english = {
            'क्रोम': 'chrome',
            'गूगल क्रोम': 'chrome',
            'ब्राउज़र': 'browser',
            'यूट्यूब': 'youtube',
            'वीडियो': 'youtube',
            'स्पॉटिफाई': 'spotify',
            'संगीत': 'spotify',
            'म्यूजिक': 'spotify',
            'वीएलसी': 'vlc',
            'वर्ड': 'word',
            'शब्द': 'word',
            'एक्सेल': 'excel',
            'पावरपॉइंट': 'powerpoint',
            'कैलकुलेटर': 'calculator',
            'नोटपैड': 'notepad',
            'एक्सप्लोरर': 'explorer',
            'वाट्सएप': 'whatsapp',
            'स्काइप': 'skype',
            'टेलीग्राम': 'telegram'
        }
        return hindi_to_english.get(app_name.lower(), app_name.lower())
        
    def _normalize_time(self, time_str: str) -> str:
        """Convert Hindi time references to standard format"""
        hindi_time_map = {
            'सुबह': 'morning',
            'प्रातः': 'morning',
            'दोपहर': 'afternoon',
            'शाम': 'evening',
            'संध्या': 'evening',
            'रात': 'night',
            'मध्यरात्री': 'midnight',
            'बजे': ':00',
            'बज गए': ':00'
        }
        
        # Replace Hindi time indicators
        for hindi, english in hindi_time_map.items():
            time_str = time_str.replace(hindi, english)
            
        return time_str
        
    def _normalize_date(self, date_str: str) -> str:
        """Convert Hindi date references to standard format"""
        hindi_date_map = {
            'आज': 'today',
            'कल': 'tomorrow',
            'परसों': 'day_after_tomorrow',
            'बीता हुआ': 'past',
            'अगला': 'next',
            'पिछला': 'last',
            'सोमवार': 'Monday',
            'मंगलवार': 'Tuesday',
            'बुधवार': 'Wednesday',
            'गुरुवार': 'Thursday',
            'शुक्रवार': 'Friday',
            'शनिवार': 'Saturday',
            'रविवार': 'Sunday',
            'जनवरी': 'January',
            'फरवरी': 'February',
            'मार्च': 'March',
            'अप्रैल': 'April',
            'मई': 'May',
            'जून': 'June',
            'जुलाई': 'July',
            'अगस्त': 'August',
            'सितंबर': 'September',
            'अक्टूबर': 'October',
            'नवंबर': 'November',
            'दिसंबर': 'December'
        }
        
        for hindi, english in hindi_date_map.items():
            date_str = date_str.replace(hindi, english)
            
        return date_str
    
    def _extract_context(self, hindi_text: str, english_text: str) -> Dict[str, Any]:
        """Extract contextual information from the command"""
        context = {
            "time_sensitive": any(word in hindi_text.lower() for word in ["अभी", "जल्दी", "तुरंत"]),
            "urgency": "high" if any(word in hindi_text.lower() for word in ["जल्दी", "तुरंत"]) else "normal",
            "politeness": "polite" if any(word in hindi_text.lower() for word in ["कृपया", "प्लीज"]) else "neutral"
        }
        return context
        
    async def generate_response(self, processed_command: Dict[str, Any]) -> str:
        """Generate natural Hindi response based on processed command"""
        intent = processed_command["intent"]["name"]
        confidence = processed_command["intent"]["confidence"]
        
        # If confidence is too low, ask for clarification
        if confidence < 0.5:
            return "मुझे आपकी बात समझ में नहीं आई। कृपया दोबारा बताएं।"
        
        # Generate contextual response based on intent and entities
        if intent == "open_application" and processed_command["entities"]:
            app_name = processed_command["entities"][0]["value"]
            return f"ठीक है, मैं {app_name} खोल रहा हूं।"
            
        elif intent == "get_info":
            return "मैं आपको यह जानकारी देता हूं।"
            
        elif intent == "system_control":
            return "सिस्टम कंट्रोल के लिए आपका क्या आदेश है?"
            
        return "मैं आपकी मदद कैसे कर सकता हूं?"
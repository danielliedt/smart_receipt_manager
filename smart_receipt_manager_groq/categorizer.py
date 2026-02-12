# File: categorizer.py (v1.5 - Cloud Version)
import json
import os
import re
from groq import Groq
import rules_config  # CATEGORIES, FALSE_FRIENDS, HARDCODED_RULES
from path_config import CSV_FOLDER, SETTINGS_FILE

class ProductCategorizer:
    def __init__(self):
        self.model_name = "llama-3.3-70b-versatile"
        self.mapping_file = CSV_FOLDER / "manual_mappings.json"
        self.manual_mappings = self.load_mappings()
        self.client = None # Initialized on demand

    def _get_api_key(self):
        """Retrieve API key from settings or environment."""
        # 1. Check settings.json (GUI user input)
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    key = json.load(f).get("groq_key", "")
                    if key: return key
            except: pass
        
        # 2. Fallback: Hardcoded key for distribution
        # Replace this with your key when building the executable
        return "YOUR_FALLBACK_KEY_HERE"

    def load_mappings(self):
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def normalize(self, text):
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9äöüß ]', ' ', text)
        return " ".join(text.split())

    def get_category(self, item_name):
        if not item_name:
            return "UNCATEGORIZED", 0.0

        clean_name = self.normalize(item_name)

        # 1. Local rules (False Friends)
        for word, category in rules_config.FALSE_FRIENDS.items():
            if word.lower() in clean_name:
                return category, 1.0

        # 2. Local rules (Hardcoded)
        for category, keywords in rules_config.HARDCODED_RULES.items():
            if any(kw.lower() in clean_name for kw in keywords):
                return category, 1.0

        # 3. Memory (Manual mappings)
        if item_name in self.manual_mappings:
            return self.manual_mappings[item_name], 1.0

        # 4. Cloud AI
        return self.ask_cloud_llm(item_name)

    def ask_cloud_llm(self, original_name):
        key = self._get_api_key()
        if not key or "YOUR_FALLBACK" in key:
            return "UNCATEGORIZED", 0.0

        if not self.client:
            self.client = Groq(api_key=key)

        category_list = ", ".join(rules_config.CATEGORIES)
        prompt = f"""
        Categorize this German supermarket item: "{original_name}"
        Choose EXACTLY ONE from this list: {category_list}
        Return ONLY the category name.
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=20
            )
            ai_response = completion.choices[0].message.content.strip()
            
            for cat in rules_config.CATEGORIES:
                if cat.lower() in ai_response.lower():
                    return cat, 0.98
            
            return "Miscellaneous", 0.70
        except Exception as e:
            print(f"   [!] Groq API Error: {e}")
            return "UNCATEGORIZED", 0.0

    def save_manual_mapping(self, item_name, correct_category):
        self.manual_mappings[item_name] = correct_category
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.manual_mappings, f, indent=4, ensure_ascii=False)
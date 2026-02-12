import json
import os
import requests
import re
import rules_config 
from path_config import INPUT_FOLDER, PROCESSED_FOLDER, CSV_FOLDER

class ProductCategorizer:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.1:latest"
        self.mapping_file = CSV_FOLDER / "manual_mappings.json"
        self.manual_mappings = self.load_mappings()

    def load_mappings(self):
        """Loads manual corrections from JSON file."""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def normalize(self, text):
        """Cleans text for consistent comparisons."""
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9äöüß ]', ' ', text)
        return " ".join(text.split())

    def get_category(self, item_name):
        """Priority logic: Rules -> Memory -> AI."""
        clean_name = self.normalize(item_name)

        # 1. Check False Friends (Top Priority)
        for word, category in rules_config.FALSE_FRIENDS.items():
            if word in clean_name:
                return category, 1.0

        # 2. Check Hardcoded Rules
        for category, keywords in rules_config.HARDCODED_RULES.items():
            if any(kw in clean_name for kw in keywords):
                return category, 1.0

        # 3. Check Manual Memory
        if item_name in self.manual_mappings:
            return self.manual_mappings[item_name], 1.0

        # 4. Final step: AI categorization
        return self.ask_llm(item_name, clean_name)

    def ask_llm(self, original_name, clean_name):
        """Communicates with local Llama model via Ollama."""
        category_list = ", ".join(rules_config.CATEGORIES)
        
        prompt = f"""
        You are an expert for German supermarket products.
        Categorize the following item: "{original_name}"
        
        Choose EXACTLY ONE category from this list: {category_list}
        
        Specific rules:
        - "Passierte Tomaten" always belongs to "Pantry & Cooking".
        - "Baguette" always belongs to "Breakfast & Bakery".
        - Pay attention to brand names and typical German abbreviations.
        
        Return ONLY the exact category name from the list. 
        No explanations, no introduction, no punctuation.
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": { 
                "temperature": 0.0 
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=15)
            if response.status_code == 200:
                ai_response = response.json().get("response", "").strip()
                
                # Validation: Does response match our category list?
                for cat in rules_config.CATEGORIES:
                    if cat.lower() in ai_response.lower():
                        return cat, 0.95
                
                return "Miscellaneous", 0.70
            return "UNCATEGORIZED", 0.0
        except Exception as e:
            print(f"   [!] AI Error: {e}")
            return "UNCATEGORIZED", 0.0

    def save_manual_mapping(self, item_name, correct_category):
        """Saves a manual correction to the mapping file."""
        self.manual_mappings[item_name] = correct_category
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.manual_mappings, f, indent=4, ensure_ascii=False)
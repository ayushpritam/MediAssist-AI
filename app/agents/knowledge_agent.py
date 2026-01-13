import pandas as pd
import os
import difflib

class KnowledgeAgent:
    def __init__(self):
        self.knowledge_base = pd.DataFrame()
        self.all_diseases = []
        
        # --- SYNONYM DICTIONARY ---
        self.synonyms = {
            "blood pressure": "Hypertension",
            "high blood pressure": "Hypertension",
            "bp": "Hypertension",
            "hypertension": "Hypertension",
            "sugar": "Diabetes",
            "diabetes": "Diabetes",
            "diabetic": "Diabetes",
            "high sugar": "Diabetes",
            "corona": "COVID-19",
            "covid": "COVID-19",
            "virus": "COVID-19",
            "breathing problem": "Asthma",
            "cant breathe": "Asthma",
            "wheezing": "Asthma",
            "inhaler": "Asthma",
            "stomach bug": "Food Poisoning",
            "food poisoning": "Food Poisoning",
            "low blood": "Anemia",
            "anemia": "Anemia",
            "cold": "Common Cold",
            "flu": "Common Cold",
            "headache": "Migraine",
            "piles": "Dimorphic hemmorhoids(piles)",
            "dimorphic hemmorhoids(piles)": "Dimorphic hemmorhoids(piles)", 
            "pox": "Chicken pox",
            "chicken pox": "Chicken pox",
            "jaundice": "Jaundice",
            "typhoid": "Typhoid",
            "malaria": "Malaria",
            "dengue": "Dengue"
        }

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            desc_path = os.path.join(base_path, '..', 'data', 'symptom_Description.csv')
            prec_path = os.path.join(base_path, '..', 'data', 'symptom_precaution.csv')

            if os.path.exists(desc_path) and os.path.exists(prec_path):
                df_desc = pd.read_csv(desc_path)
                df_prec = pd.read_csv(prec_path)
                
                # --- CRITICAL FIX: CLEANING BEFORE MERGE ---
                # Remove accidental spaces from the 'Disease' column
                df_desc['Disease'] = df_desc['Disease'].astype(str).str.strip()
                df_prec['Disease'] = df_prec['Disease'].astype(str).str.strip()

                # --- CRITICAL FIX: LEFT MERGE ---
                # how='left' ensures we keep the Description even if Precautions are missing
                self.knowledge_base = pd.merge(df_desc, df_prec, on="Disease", how='left')
                
                # Create a lowercase column for easier searching
                self.knowledge_base['Disease_Lower'] = self.knowledge_base['Disease'].str.lower().str.strip()
                self.all_diseases = self.knowledge_base['Disease_Lower'].tolist()
                
                print(f"KnowledgeAgent: Loaded {len(self.knowledge_base)} diseases successfully.")
            else:
                print("Error: Knowledge CSV files not found.")
        except Exception as e:
            print(f"Error loading Knowledge base: {e}")

    def _find_closest_match(self, user_text):
        """Smart Spell Checker"""
        matches = difflib.get_close_matches(user_text, self.all_diseases, n=1, cutoff=0.5)
        return matches[0] if matches else None

    def get_info(self, topic):
        if self.knowledge_base.empty:
            return None
        
        clean_topic = str(topic).lower().strip()

        # 1. Check Synonyms
        if clean_topic in self.synonyms:
            clean_topic = self.synonyms[clean_topic].lower()

        # 2. Try Exact Match
        match = self.knowledge_base[self.knowledge_base['Disease_Lower'] == clean_topic]
        
        # 3. Fuzzy Match
        if match.empty:
            closest_disease = self._find_closest_match(clean_topic)
            if closest_disease:
                match = self.knowledge_base[self.knowledge_base['Disease_Lower'] == closest_disease]

        # 4. Partial Match
        if match.empty:
            match = self.knowledge_base[self.knowledge_base['Disease_Lower'].str.contains(clean_topic, regex=False, na=False)]

        if not match.empty:
            row = match.iloc[0]
            
            # Extract precautions safely
            precautions = []
            for i in range(1, 5):
                col = f"Precaution_{i}"
                if col in row and pd.notna(row[col]) and str(row[col]).strip():
                    precautions.append(str(row[col]).capitalize())

            return {
                "name": row['Disease'],
                "description": row['Description'],
                "precautions": precautions
            }
            
        return None

knowledge_agent = KnowledgeAgent()
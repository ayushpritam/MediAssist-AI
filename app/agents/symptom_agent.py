import joblib
import re
import os

class SymptomAgent:
    def __init__(self):
        self.model = None
        try:
            # Locate the model in the 'ml_models' folder at the project root
            base_path = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_path, '..', '..', 'ml_models', 'symptom_model.pkl')
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("SymptomAgent: ML Model loaded successfully.")
            else:
                print(f"Error: Model not found at {model_path}. Please run train_model.py.")
        except Exception as e:
            print(f"Error loading Symptom model: {e}")

    def _clean_text(self, text):
        """Cleans text to match the training format."""
        text = str(text).strip().lower()
        text = re.sub(r'_', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def predict_disease(self, user_input):
        if not self.model:
            return {"error": "Model not loaded"}

        cleaned_input = self._clean_text(user_input)
        if not cleaned_input:
            return {}

        try:
            # The pipeline expects a list of strings
            probs = self.model.predict_proba([cleaned_input])[0]
            classes = self.model.classes_

            # Filter results with > 10% confidence
            results = {
                disease: prob 
                for disease, prob in zip(classes, probs) 
                if prob > 0.1
            }
            
            # Sort by confidence
            sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True)[:3])
            return sorted_results
        except Exception as e:
            return {"error": str(e)}

symptom_agent = SymptomAgent()
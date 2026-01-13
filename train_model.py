import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import re

def clean_text(text):
    """
    Standardizes text: lowercase, removes underscores, removes extra spaces.
    Example: "High_Fever" -> "high fever"
    """
    text = str(text).lower().strip()
    text = re.sub(r'_', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def train():
    print("🚀 Starting Model Training...")

    # 1. Setup File Paths (RELATIVE TO THE MAIN FOLDER)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to dataset: app/data/dataset.csv
    dataset_path = os.path.join(base_dir, 'app', 'data', 'dataset.csv')
    
    # Path to save model: app/ml_models/symptom_model.pkl
    # (We check if 'app/ml_models' exists, if not we try just 'ml_models')
    model_dir = os.path.join(base_dir, 'app', 'ml_models')
    if not os.path.exists(model_dir):
        # Fallback: maybe the folder is in the root?
        model_dir = os.path.join(base_dir, 'ml_models')
        os.makedirs(model_dir, exist_ok=True) # Create it if it doesn't exist
        
    model_save_path = os.path.join(model_dir, 'symptom_model.pkl')

    # 2. Load Data
    if not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset not found at {dataset_path}")
        print("Please check that 'dataset.csv' is inside the 'app/data' folder.")
        return

    print(f"📂 Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # Fill NaN values
    df = df.fillna('')

    # 3. Preprocess Data
    print("⚙️  Preprocessing symptom data...")
    symptom_cols = [col for col in df.columns if 'Symptom' in col]
    
    def combine_symptoms(row):
        symptoms = [str(row[c]) for c in symptom_cols if row[c] != '']
        cleaned_symptoms = [clean_text(s) for s in symptoms]
        return " ".join(cleaned_symptoms)

    df['features'] = df.apply(combine_symptoms, axis=1)
    
    X = df['features']
    y = df['Disease']

    # 4. Create Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', MultinomialNB())
    ])

    # 5. Train Model
    print(f"🧠 Training on {len(df)} records...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline.fit(X_train, y_train)

    # 6. Evaluate
    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

    # 7. Save Model
    joblib.dump(pipeline, model_save_path)
    print(f"💾 Model saved to: {model_save_path}")
    print("🎉 Training Complete!")

if __name__ == "__main__":
    train()
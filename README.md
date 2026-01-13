# 🩺 MediAssist AI

**MediAssist AI** is an intelligent healthcare chatbot designed to provide preliminary medical assessments, symptom analysis, and emergency triage. It utilizes a Multi-Agent System driven by Machine Learning and Rule-Based Logic to assist users with health concerns.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange)

##  Features

* ** Emergency Triage:** Detects life-threatening symptoms (e.g., heart attack, stroke) and warns users immediately.
* ** Symptom Analysis:** Uses a trained Machine Learning model to predict potential conditions based on user inputs.
* ** Medical Knowledge Base:** Retrieves detailed information about diseases, symptoms, and precautions.
* ** Treatment Recommendations:** Provides home remedies and general recovery guidance.
* ** PDF Reports:** Generates a downloadable consultation report for doctors.
* ** Voice Support:** Allows users to speak their symptoms instead of typing.

##  Installation (Run Locally)

If you want to run this project on your own machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ayushpritam/MediAssist-AI.git](https://github.com/ayushpritam/MediAssist-AI.git)
    cd MediAssist-AI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    * **Backend (API):**
        ```bash
        python -m app.main
        ```
    * **Frontend (UI):**
        ```bash
        streamlit run frontend/app.py
        ```

##  Disclaimer
**MediAssist AI is a prototype and NOT a licensed medical professional.** It is intended for educational and informational purposes only. In case of a real medical emergency, call 911/112 or visit the nearest hospital immediately.

---
**Created by:** Ayush Pritam

import re

class TriageAgent:
    def __init__(self):
        # 🔴 EMERGENCY KEYWORDS BY CATEGORY
        self.emergency_keywords = {
            "cardiac": [
                "chest pain", "heart attack", "crushing pain",
                "pressure on chest", "tightness in chest",
                "radiating pain", "chest discomfort"
            ],
            "stroke": [
                "face drooping", "arm weakness", "slurred speech",
                "numbness", "cant speak", "blurred vision",
                "one side numb", "drooping face"
            ],
            "respiratory": [
                "difficulty breathing", "shortness of breath",
                "choking", "cant breathe", "gasping",
                "blue lips", "wheezing", "breathlessness"
            ],
            "trauma": [
                "severe bleeding", "coughing blood",
                "coughing up blood", "blood in vomit",
                "head injury", "unconscious",
                "deep cut", "severe burn"
            ],
            "allergic": [
                "throat closing", "throat is closing",
                "swollen tongue", "anaphylaxis",
                "swelling face", "hives",
                "trouble swallowing"
            ],
            "general": [
                "seizure", "collapse", "unresponsive",
                "poison", "overdose", "fainted"
            ]
        }

        # 🔴 COMMON ALLERGY TRIGGERS
        self.allergy_triggers = [
            "peanut", "nuts", "shellfish", "egg",
            "milk", "soy", "seafood"
        ]

    def _normalize(self, text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def check_triage(self, message):
        """
        Returns:
        (STATUS, RESPONSE_MESSAGE)
        STATUS → EMERGENCY | SAFE
        """
        text = self._normalize(message)

        # 🚨 1️⃣ ANAPHYLAXIS (HIGHEST PRIORITY)
        if any(food in text for food in self.allergy_triggers) and (
            "throat" in text or "breath" in text or "swelling" in text
        ):
            return (
                "EMERGENCY",
                "🚨 **EMERGENCY: Possible ANAPHYLAXIS (severe allergic reaction)**\n\n"
                "This is life-threatening.\n\n"
                "👉 **Call emergency services (112/911) IMMEDIATELY**\n"
                "👉 If you have an epinephrine injector, use it NOW\n\n"
                "*Do not rely on this chatbot for emergencies.*"
            )

        # 🚨 2️⃣ CATEGORY-BASED EMERGENCY CHECK
        for category, keywords in self.emergency_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return (
                        "EMERGENCY",
                        f"🚨 **EMERGENCY DETECTED**\n\n"
                        f"Your symptoms suggest a serious **{category.upper()} emergency**.\n\n"
                        "👉 **Call emergency services (112/911) immediately** or go to the nearest ER.\n\n"
                        "*Do not rely on this chatbot for life-threatening situations.*"
                    )

        # ✅ 3️⃣ SAFE TO CONTINUE
        return "SAFE", ""

triage_agent = TriageAgent()

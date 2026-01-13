import re
from app.agents.triage_agent import triage_agent
from app.agents.symptom_agent import symptom_agent
from app.agents.knowledge_agent import knowledge_agent

def generate_response(user_message):
    
    # --- 1. SAFETY FIRST: Triage Check ---
    triage_status, triage_msg = triage_agent.check_triage(user_message)
    if triage_status == "EMERGENCY":
        return triage_msg

    # --- 2. INTENT CLASSIFICATION ---
    knowledge_pattern = r"^(what is|what's|what are|how does|tell me about|define|explain)\b"
    symptom_pattern = r"\b(i have|i feel|my \w+ hurts|pain|ache|fever|cough|rash|vomiting|stool)\b"

    user_text_lower = user_message.lower().strip()

    # --- CASE A: USER ASKS A QUESTION ---
    if re.search(knowledge_pattern, user_text_lower):
        topic = re.sub(knowledge_pattern, "", user_text_lower).strip("? .")
        
        # Get Info (Name, Desc, Precautions)
        data = knowledge_agent.get_info(topic)
        
        if data:
            # SUCCESS: Use the OFFICIAL NAME from 'data['name']'
            response = f"**About {data['name']}:**\n{data['description']}\n"
            if data['precautions']:
                response += "\n**Precautions/Steps:**\n" + "\n".join([f"- {p}" for p in data['precautions']])
            return response
        else:
            # FAIL: Pass through to symptom check just in case
            pass 

    # --- CASE B: SYMPTOM ANALYSIS ---
    predictions = symptom_agent.predict_disease(user_message)

    if not predictions or "error" in predictions:
        return "I'm sorry, I couldn't analyze your input. Are you describing symptoms or asking for medical information? Please try being more specific."

    # Get top prediction
    top_disease = list(predictions.keys())[0]
    confidence = predictions[top_disease]

    # Get Info for the predicted disease
    data = knowledge_agent.get_info(top_disease)

    # Build Response
    response = ""
    if triage_status == "URGENT":
        response += f"⚠️ **{triage_msg}**\n\n"

    # Use the corrected name if we found data, otherwise use the prediction raw string
    display_name = data['name'] if data else top_disease

    response += f"Based on your symptoms, a likely condition is **{display_name}** ({int(confidence*100)}% match).\n\n"
    
    if data:
        response += f"**Overview:** {data['description']}\n\n"
        response += "**Recommended Steps:**\n"
        if data['precautions']:
            for p in data['precautions']:
                response += f"- {p}\n"
    else:
        response += f"**Overview:** I couldn't find specific details for '{display_name}' in the knowledge base, but please consult a doctor.\n"
        response += "**Recommended Steps:**\n- Consult a doctor for specific advice.\n"

    response += "\n*Disclaimer: I am an AI, not a doctor. This is for informational purposes only.*"

    return response 

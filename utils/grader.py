import json
import streamlit as st

# --- TRY IMPORTING GROQ (PREFERRED) OR FALLBACK TO OPENAI ---
try:
    from groq import Groq
    USE_GROQ = True
except ImportError:
    from openai import OpenAI
    USE_GROQ = False

def call_grader(rubric, submission, translate=False):
    """
    Calls the AI API (Groq or OpenAI) and returns a CLEAN dictionary.
    """
    
    # --- 1. API CLIENT SETUP ---
    if USE_GROQ:
        client = Groq(api_key=st.secrets["GROQ_KEY"])
        model = "llama-3.1-8b-instant"
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_KEY"])
        model = "gpt-4o-mini"

    # --- 2. BUILD THE PROMPT ---
    prompt = f"""
    Rubric: {rubric}
    Submission: {submission}
    
    IMPORTANT: Output strictly valid JSON with the following EXACT structure:
    {{
        "score": "85/100",
        "strengths": ["Strength point 1", "Strength point 2"],
        "weaknesses": ["Weakness point 1", "Weakness point 2"],
        "feedback": ["Actionable step 1", "Actionable step 2", "Actionable step 3"]
    }}
    """
    
    if translate:
        prompt += "\n\nAlso, translate the final feedback into Spanish."

    # --- 3. API CALL ---
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a strict academic grader. Always output valid JSON. The 'feedback' key must ALWAYS be a list of sentences."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    # --- 4. PARSE THE RESPONSE ---
    result_data = json.loads(response.choices[0].message.content)

    # --- 5. 🛡️ THE CRITICAL FIX: CLEAN & STANDARDIZE THE DATA ---
    
    # Fix 'feedback': If it's a single string, split it into a list of bullet points.
    if isinstance(result_data.get('feedback'), str):
        feedback_text = result_data['feedback']
        # If it has periods, split into sentences. Otherwise, just wrap it.
        if '. ' in feedback_text:
            result_data['feedback'] = [s.strip() + '.' for s in feedback_text.split('. ') if s.strip()]
        elif '\n' in feedback_text:
            result_data['feedback'] = [line.strip() for line in feedback_text.split('\n') if line.strip()]
        else:
            result_data['feedback'] = [feedback_text]  # Wrap single sentence into a list
    
    # Fix 'strengths': If it's a string, wrap it in a list.
    if isinstance(result_data.get('strengths'), str):
        result_data['strengths'] = [result_data['strengths']]
    
    # Fix 'weaknesses': If it's a string, wrap it in a list.
    if isinstance(result_data.get('weaknesses'), str):
        result_data['weaknesses'] = [result_data['weaknesses']]
    
    # Ensure all fields exist to prevent KeyErrors in the UI
    result_data.setdefault('strengths', [])
    result_data.setdefault('weaknesses', [])
    result_data.setdefault('feedback', [])
    result_data.setdefault('score', 'N/A')

    return result_data
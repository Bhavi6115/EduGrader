import json
import streamlit as st
from groq import Groq

def call_grader(rubric, submission, translate=False):
    """
    Calls the Groq AI API and returns a CLEAN dictionary.
    """
    
    # --- 1. API CLIENT SETUP ---
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    model = "llama-3.1-8b-instant"

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

    # --- 5. CLEAN & STANDARDIZE THE DATA ---
    
    # Fix 'feedback': If it's a single string, split it into a list of bullet points.
    if isinstance(result_data.get('feedback'), str):
        feedback_text = result_data['feedback']
        if '. ' in feedback_text:
            result_data['feedback'] = [s.strip() + '.' for s in feedback_text.split('. ') if s.strip()]
        elif '\n' in feedback_text:
            result_data['feedback'] = [line.strip() for line in feedback_text.split('\n') if line.strip()]
        else:
            result_data['feedback'] = [feedback_text]
    
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


def suggest_rubric(submission):
    """
    Uses Groq to generate a grading rubric based on the submission.
    """
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    model = "llama-3.1-8b-instant"
    
    prompt = f"""
    Based on this student submission, create a detailed grading rubric with 3 to 4 categories and their percentage weights. 
    The total must equal 100%.
    
    Submission: {submission}
    
    Output format (just plain text, no markdown, no bullet points, no asterisks):
    Category 1 (X%): Description
    Category 2 (Y%): Description
    Category 3 (Z%): Description
    Category 4 (W%): Description
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content
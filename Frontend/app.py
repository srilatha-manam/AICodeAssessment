import streamlit as st
import requests
import json

# FastAPI backend URL
API_URL = "http://localhost:8000/code-assessment"

# Page Config
st.set_page_config(page_title="AI Code Assessment App", layout="wide")

st.title("🧠 AI Code Assessment App")

# 1. Load a random question
if "question" not in st.session_state:
    response = requests.get(f"{API_URL}/question")
    if response.status_code == 200:
        st.session_state.question = response.json()
    else:
        st.error("Failed to load a question.")

question = st.session_state.question
st.subheader("Problem Statement")
st.code(question["question"], language="python")

# 2. User input code
st.subheader("Write Your Code Below")
code_input = st.text_area("Code Editor", height=300, key="code_editor")

# Language selector (Judge0 uses language_id: 71 for Python 3)
languages = {
    "Python 3": 71,
    "C": 50,
    "C++": 54,
    "Java": 62,
    "C#": 51,
    "JavaScript": 63    
}
selected_lang = st.selectbox("Choose Language", list(languages.keys()))
language_id = languages[selected_lang]

# Submit code
if st.button("Submit Code"):
    with st.spinner("Evaluating your solution..."):
        payload = {
            "code": code_input,
            "language_id": language_id,
            "question_id": question["id"]
        }

        try:
            res = requests.post(f"{API_URL}/evaluate", json=payload)
            if res.status_code == 200:
                result = res.json()
                st.success(" Evaluation Completed")
                st.markdown(f"**Correct:** `{result['correct']}`")
                st.markdown(f"**Expected Output:** `{result['expected']}`")
                st.markdown(f"**Your Output:** `{result['actual']}`")
                st.markdown(f"**Status:** `{result['status']}`")
            else:
                st.error(f"Error: {res.status_code} - {res.text}")
        except Exception as e:
            st.exception("Submission failed.")

import streamlit as st
import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8000/code-assessment"

st.set_page_config(
    page_title="AI Code Assessment App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .feedback-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    .status-pass { color: #28a745; }
    .status-fail { color: #dc3545; }
    .status-partial { color: #ffc107; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Code Assessment App")
st.markdown("*Powered by Gemini 1.5 Flash for intelligent code evaluation*")

# Ask for question ID if not already provided
if "question" not in st.session_state:
    st.markdown("## 🔢 Enter Question ID to Begin")
    question_id_input = st.text_input("Enter a valid Question ID", placeholder="e.g., 101")

    if st.button("📥 Load Question"):
        if question_id_input.strip().isdigit():
            try:
                with st.spinner("Fetching question..."):
                    response = requests.get(f"{API_URL}/question/{question_id_input.strip()}")
                    response.raise_for_status()
                    st.session_state.question = response.json()
                    st.rerun()
            except requests.exceptions.HTTPError:
                st.error(f"❌ Question with ID {question_id_input.strip()} not found.")
            except Exception as e:
                st.error(f"❌ Failed to load question: {e}")
        else:
            st.warning("⚠️ Please enter a valid numeric Question ID.")
    st.stop()

question = st.session_state.question

# Sidebar - info
with st.sidebar:
    st.header("📊 Assessment Focus")
    st.info("""
    **Gemini AI evaluates your code on:**
    - ✅ Correctness
    - 🧩 Complexity
    - 🎯 Simplicity & clarity
    - 🔍 Edge cases
    - 🛡️ Error handling
    - ⚡ Performance
    - 🏗️ Structure
    - 📖 Readability
    """)

# Display Question
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("## 📝 Problem Statement")
    st.markdown(f"### {question['title']}")
    st.markdown("**Description:**")
    st.markdown(question['description'])

    st.markdown("**Examples:**")
    for i, ex in enumerate(question['examples'], 1):
        with st.expander(f"💡 Example {i}", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Input:**")
                st.code(ex['input'], language="text")
            with c2:
                st.markdown("**Output:**")
                st.code(ex['output'], language="text")
            if 'explanation' in ex and ex['explanation']:
                st.markdown("**🧠 Explanation:**")
                st.info(ex['explanation'])

with col2:
    st.markdown("## ⚙️ Submission Settings")
    languages = {
        "🐍 Python 3": 71,
        "🔧 C": 50,
        "⚡ C++": 54,
        "☕ Java": 62,
        "💎 C#": 51,
        "🌐 JavaScript": 63
    }
    selected_lang = st.selectbox("Choose Language", list(languages.keys()))
    language_id = languages[selected_lang]
    language_name = selected_lang.split(" ", 1)[1]

# Code Input Area
st.markdown("## 💻 Code Editor")
code_input = st.text_area(
    "Your Code",
    height=400,
    placeholder=f"Write your {language_name} code here..."
)

col_submit, col_clear = st.columns([3, 1])
with col_submit:
    submit_button = st.button("🚀 Submit & Evaluate Code", type="primary", use_container_width=True)
with col_clear:
    if st.button("🗑️ Clear Code", use_container_width=True):
        st.rerun()

# Submission Logic
if submit_button:
    if not code_input.strip():
        st.warning("⚠️ Please enter your code before submitting!")
    else:
        with st.spinner("🤖 Gemini AI is evaluating your solution..."):
            payload = {
                "code": code_input,
                "language_id": language_id,
                "question_id": question["id"]
            }
            try:
                response = requests.post(f"{API_URL}/evaluate", json=payload)
                response.raise_for_status()
                result = response.json()

                # Results Display
                st.markdown("## 🎯 Execution Results")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    correct_color = "green" if result.get('correct') else "red"
                    st.markdown(f"**Correctness:** :{correct_color}[{result.get('correct', 'Unknown')}]")
                with c2:
                    st.markdown(f"**Status:** `{result.get('status', 'Unknown')}`")
                with c3:
                    st.markdown(f"**Expected:** `{result.get('expected', 'N/A')}`")
                with c4:
                    st.markdown(f"**Your Output:** `{result.get('actual', 'N/A')}`")

                feedback = result.get("feedback")
                if feedback and isinstance(feedback, dict) and "error" not in feedback:
                    st.markdown("## 🤖 Gemini AI Feedback")
                    summary = feedback.get("summary", {})
                    overall_score = summary.get("overall_score", 0)
                    recommendation = summary.get("recommendation", "unknown")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Overall Score", f"{overall_score}/10")
                    with col2:
                        rec_color = {"accept": "green", "review": "orange", "reject": "red"}.get(recommendation, "gray")
                        st.markdown(f"**Recommendation:** :{rec_color}[{recommendation.upper()}]")
                    with col3:
                        st.markdown(f"**Complexity:** {summary.get('complexity_rating', 'unknown')}")

                    # Feedback Tabs
                    sections = feedback.get("feedback", {})
                    t1, t2, t3, t4 = st.tabs(["📊 Scores", "💡 Suggestions", "✨ Positives", "🎯 Improvements"])
                    with t1:
                        for section_name, section_data in sections.items():
                            if isinstance(section_data, dict):
                                st.markdown(f"### {section_name.replace('_', ' ').title()}")
                                st.markdown(f"**Score:** {section_data.get('score', 0)}/10")
                                st.markdown(f"**Status:** `{section_data.get('status', '')}`")
                                st.markdown(section_data.get("comments", ""))
                                st.divider()
                    with t2:
                        for s in feedback.get("intelligent_suggestions", []):
                            st.markdown(f"- {s}")
                    with t3:
                        for p in feedback.get("positive_aspects", []):
                            st.success(f"✅ {p}")
                    with t4:
                        for i in feedback.get("areas_for_improvement", []):
                            st.warning(f"🎯 {i}")

                    if summary.get("remarks"):
                        st.markdown("### 📝 Final Remarks")
                        st.info(summary["remarks"])

                elif feedback and "error" in feedback:
                    st.warning(f"⚠️ AI Feedback Error: {feedback.get('error', 'Unknown error')}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Network error: {e}")
            except Exception as e:
                st.error(f"❌ Submission failed: {e}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown("*Powered by Gemini 1.5 Flash AI • Built with Streamlit*")

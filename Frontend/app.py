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

# Custom CSS for better styling
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

# Sidebar for additional controls
with st.sidebar:
    st.header("🔧 Controls")
    if st.button("🔄 Load New Question"):
        if "question" in st.session_state:
            del st.session_state.question
        st.rerun()
    
    st.header("📊 Assessment Focus")
    st.info("""
    **Gemini AI evaluates your code on:**
    - ✅ Correctness
    - 🧩 Complexity appropriateness
    - 🎯 Simplicity & clarity
    - 🔍 Edge case handling
    - 🛡️ Error handling
    - ⚡ Performance
    - 🏗️ Code structure
    - 📖 Readability
    """)

# Load question only once per session unless manually refreshed
if "question" not in st.session_state:
    try:
        with st.spinner("Loading coding challenge..."):
            response = requests.get(f"{API_URL}/question")
            response.raise_for_status()
            st.session_state.question = response.json()
    except Exception as e:
        st.error(f"❌ Failed to load a question: {e}")
        st.stop()

question = st.session_state.question

# Display question in a more attractive format
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📝 Problem Statement")
    
    # Question title
    st.markdown(f"### {question['title']}")
    
    # Question description
    st.markdown("**Description:**")
    st.markdown(question['description'])
    
    # Examples
    st.markdown("**Examples:**")
    for i, ex in enumerate(question['examples'], 1):
        with st.expander(f"💡 Example {i}", expanded=True):
            col_input, col_output = st.columns(2)
            with col_input:
                st.markdown("**Input:**")
                st.code(ex['input'], language="text")
            with col_output:
                st.markdown("**Output:**")
                st.code(ex['output'], language="text")
            if 'explanation' in ex and ex['explanation']:
                st.markdown("**🧠 Explanation:**")
                st.info(ex['explanation'])

with col2:
    st.markdown("## ⚙️ Submission Details")
    
    # Language selection with icons
    languages = {
        "🐍 Python 3": 71,
        "🔧 C": 50,
        "⚡ C++": 54,
        "☕ Java": 62,
        "💎 C#": 51,
        "🌐 JavaScript": 63
    }
    
    selected_lang = st.selectbox("Choose Programming Language", list(languages.keys()))
    language_id = languages[selected_lang]
    language_name = selected_lang.split(" ", 1)[1]  # Remove emoji for API

# Code editor section
st.markdown("## 💻 Code Editor")
st.markdown("*Write your solution below:*")

code_input = st.text_area(
    "Your Code", 
    height=400,
    placeholder=f"Write your {language_name} solution here..."
)

# Submission section
col_submit, col_clear = st.columns([3, 1])

with col_submit:
    submit_button = st.button("🚀 Submit & Evaluate Code", type="primary", use_container_width=True)

with col_clear:
    if st.button("🗑️ Clear Code", use_container_width=True):
        st.rerun()

# Handle code submission
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
                
                # Display execution results
                st.markdown("## 🎯 Execution Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    correct_color = "green" if result.get('correct') else "red"
                    st.markdown(f"**Correctness:** :{correct_color}[{result.get('correct', 'Unknown')}]")
                
                with col2:
                    st.markdown(f"**Status:** `{result.get('status', 'Unknown')}`")
                
                with col3:
                    st.markdown(f"**Expected:** `{result.get('expected', 'N/A')}`")
                
                with col4:
                    st.markdown(f"**Your Output:** `{result.get('actual', 'N/A')}`")
                
                # Display AI feedback if available
                feedback = result.get("feedback")
                if feedback and isinstance(feedback, dict) and "error" not in feedback:
                    st.markdown("## 🤖 Gemini AI Feedback")
                    
                    # Overall score display
                    summary = feedback.get("summary", {})
                    overall_score = summary.get("overall_score", 0)
                    recommendation = summary.get("recommendation", "unknown")
                    
                    # Score visualization
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Overall Score", f"{overall_score}/10")
                    with col2:
                        rec_color = {"accept": "green", "review": "orange", "reject": "red"}.get(recommendation, "gray")
                        st.markdown(f"**Recommendation:** :{rec_color}[{recommendation.upper()}]")
                    with col3:
                        complexity = summary.get("complexity_rating", "unknown")
                        st.markdown(f"**Complexity:** {complexity}")
                    
                    # Detailed feedback sections
                    feedback_sections = feedback.get("feedback", {})
                    
                    # Create tabs for different feedback categories
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Scores", "💡 Suggestions", "✨ Positives", "🎯 Improvements"])
                    
                    with tab1:
                        # Display detailed scores
                        for section_name, section_data in feedback_sections.items():
                            if isinstance(section_data, dict):
                                col1, col2, col3 = st.columns([2, 1, 3])
                                
                                with col1:
                                    st.markdown(f"**{section_name.replace('_', ' ').title()}**")
                                
                                with col2:
                                    score = section_data.get("score", 0)
                                    status = section_data.get("status", "unknown")
                                    
                                    score_color = "green" if score >= 7 else "orange" if score >= 4 else "red"
                                    st.markdown(f":{score_color}[{score}/10]")
                                    st.markdown(f"*{status}*")
                                
                                with col3:
                                    comments = section_data.get("comments", "")
                                    st.markdown(comments)
                                
                                st.divider()
                    
                    with tab2:
                        suggestions = feedback.get("intelligent_suggestions", [])
                        if suggestions:
                            for i, suggestion in enumerate(suggestions, 1):
                                st.markdown(f"**{i}.** {suggestion}")
                        else:
                            st.info("No specific suggestions available.")
                    
                    with tab3:
                        positives = feedback.get("positive_aspects", [])
                        if positives:
                            for positive in positives:
                                st.success(f"✅ {positive}")
                        else:
                            st.info("Keep coding to discover what you do well!")
                    
                    with tab4:
                        improvements = feedback.get("areas_for_improvement", [])
                        if improvements:
                            for improvement in improvements:
                                st.warning(f"🎯 {improvement}")
                        else:
                            st.info("Great job! No major areas for improvement identified.")
                    
                    # Final remarks
                    remarks = summary.get("remarks", "")
                    if remarks:
                        st.markdown("### 📝 Final Remarks")
                        st.info(remarks)
                
                elif feedback and "error" in feedback:
                    st.warning(f"⚠️ AI Feedback Error: {feedback.get('error', 'Unknown error')}")
                    st.info("AI feedback is temporarily unavailable, but your code execution results are shown above.")
                else:
                    st.info("💡 **Tip:** AI feedback is only available when your code executes successfully. Try fixing any runtime errors first!")
                
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Network error: {e}")
            except Exception as e:
                st.error(f"❌ Submission failed: {e}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown("*Powered by Gemini 1.5 Flash AI • Built with Streamlit*")

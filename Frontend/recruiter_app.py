# Frontend/app.py - Updated to show recruiter feedback from Gemini and enhanced Judge0 execution details

import streamlit as st
import requests
import json
from typing import Dict, Any
import time

#API_URL = st.secrets["API_URL"]
API_URL = "http://localhost:8000/code-assessment"
st.set_page_config(
    page_title="AI Code Assessment - Dynamic Questions", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎯"
)

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "user_code" not in st.session_state:
    st.session_state.user_code = ""
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "questions_generated" not in st.session_state:
    st.session_state.questions_generated = 0

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Dynamic Question Generator")       
    if st.button("🎲 New Question", type="primary", use_container_width=True):
        try:
            with st.spinner("🤖 AI is creating a unique question..."):               
                start_time = time.time()
                response = requests.get(f"{API_URL}/question", timeout=90)
                generation_time = time.time() - start_time                
                response.raise_for_status()
                question_data = response.json()                
                st.session_state.current_question = question_data
                st.session_state.user_code = ""
                st.session_state.evaluation_result = None
                st.session_state.questions_generated += 1
                st.success(f"✅ Fresh question generated in {generation_time:.1f}s!")
                st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to generate question: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

    st.markdown("### 💻 Programming Language")
    language_options = {
        "Python": 71,
        "Java": 62,
        "JavaScript": 63,
        "C": 50,
        "C++": 54,
        "C#": 51
    }
    selected_language = st.selectbox("Choose Language", list(language_options.keys()), index=0)

if st.session_state.current_question:
    question = st.session_state.current_question
    st.header(f"📝 {question.get('title', 'Unknown Title')}")    
    st.markdown("### 📋 Problem Description")
    st.markdown(question.get('description', 'No description available'))

    if question.get('examples'):     
        st.markdown("### 🧪 Examples")
        for example in question['examples']:
            st.markdown("**Input:**")
            st.code(example.get('input', ''), language='text')
            st.markdown("**Output:**")
            st.code(example.get('output', ''), language='text')
            if example.get('explanation'):
                st.markdown("**Explanation:**")
                st.info(example['explanation'])

    st.markdown("### 💻 Your Solution")
    st.session_state.user_code = st.text_area(
        f"Write your {selected_language} solution:",
        value=st.session_state.user_code,
        height=300
    )

    submit_button = st.button("🚀 Submit & Evaluate", disabled=not st.session_state.user_code.strip())

    if submit_button:
        try:
            with st.spinner("🔄 Evaluating code and generating feedback..."):
                submission_data = {
                    "code": st.session_state.user_code,
                    "language_id": language_options[selected_language],
                    "question_id": question['id']
                }
                response = requests.post(f"{API_URL}/evaluate", json=submission_data, timeout=60)
                response.raise_for_status()
                st.session_state.evaluation_result = response.json()
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error during submission: {e}")

    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        st.markdown("---")
        st.markdown("## 📊 Evaluation Results")

        if result.get('correct'):
            st.success("🎉 Perfect! Your solution is correct!")
        else:
            st.warning("🔍 Review your solution. Let's improve it together!")

        tab1, tab2, tab3 = st.tabs(["📥 Output Comparison", "🔧 Execution", "🤖 Recruiter Feedback"])

        with tab1:
            st.markdown("### ✅ Expected Output")
            st.code(result.get('expected', ''), language='text')
            st.markdown("### 📤 Your Output")
            st.code(result.get('actual', ''), language='text')

        with tab2:
            st.markdown("### 🖥️ Execution Status")
            st.write(f"**Status:** {result.get('status')}")
            st.write(f"**CPU Time Limit:** {result.get('feedback', {}).get('full_judge_response', {}).get('cpu_time_limit', 'N/A')}")
            st.write(f"**Memory Limit:** {result.get('feedback', {}).get('full_judge_response', {}).get('memory_limit', 'N/A')} KB")
            st.write(f"**Memory Used:** {result.get('feedback', {}).get('full_judge_response', {}).get('memory', 'N/A')} KB")
            st.write(f"**Time Taken:** {result.get('feedback', {}).get('full_judge_response', {}).get('time', 'N/A')}s")

        with tab3:
            st.markdown("## 🤖 Recruiter Feedback Summary")
            fb = result.get('feedback', {})
            if not fb:
                st.info("Feedback not available.")
            else:
                st.markdown(f"### 🏆 Verdict: **{fb.get('verdict', 'N/A')}**")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🧠 Problem Solving", fb.get("problem_solving_score_out_of_100", "N/A"))
                col2.metric("✅ Correctness", fb.get("code_correctness_score_out_of_100", "N/A"))
                col3.metric("🧹 Code Quality", fb.get("code_quality_score_out_of_100", "N/A"))
                col4.metric("⚡ Efficiency", fb.get("efficiency_score_out_of_100", "N/A"))

                st.markdown("### 🧪 Test Case Coverage")
                coverage = fb.get("test_case_coverage", {})
                st.write(f"**Passed:** {coverage.get('passed')} / {coverage.get('total')}")
                st.write(f"**Coverage %:** {coverage.get('coverage_percent')}%")
                st.write(f"**Edge Cases Handled:** {'✅ Yes' if coverage.get('edge_cases_handled') else '❌ No'}")

                st.markdown("### 🧾 Language & Execution")
                st.write(f"**Language Used:** {fb.get('language_used')}")
                st.write(f"**Compilation:** {fb.get('code_compilation_status')}")
                st.write(f"**Runtime Errors:** {'❌ Yes' if fb.get('runtime_error_occurred') else '✅ None'}")
                st.write(f"**Time Taken:** {fb.get('time_taken')}")

                st.markdown("### 🧠 AI Insights")
                st.write(f"**Readability:** {fb.get('code_readability_feedback')}")
                st.write(f"**Algorithm Design:** {fb.get('algorithm_design_feedback')}")
                st.write(f"**Debugging Skills:** {fb.get('debugging_and_testing_skills_feedback')}")
                st.write(f"**Language Proficiency:** {fb.get('language_proficiency_comments')}")
                st.write(f"**Completion Status:** {fb.get('code_completion_status')}")

                st.markdown("### 📌 Observations")
                observation = fb.get("observations", "")
                if isinstance(observation, str):
                    st.markdown(f"{observation}")
                else:
                    st.markdown("\n".join([f"- {obs}" for obs in observation]))

                st.markdown("### 💪 Strengths")
                for strength in fb.get("strengths", []):
                    st.success(f"✅ {strength}")

                st.markdown("### ❗ Areas of Concern")
                for issue in fb.get("areas_of_concern", []):
                    st.warning(f"⚠️ {issue}")

                st.markdown("### 💡 Suggestions for Improvement")
                for tip in fb.get("improvement_suggestions", []):
                    st.info(f"💡 {tip}")

                st.markdown("### 📈 Attempt History")
                st.write(f"**Attempts Made:** {fb['attempt_summary']['attempts_made']}")
                st.write(f"**Approach Summary:** {fb['attempt_summary']['approach_used']}")
                st.markdown("**Changes Over Attempts:**")
                for attempt in fb['attempt_summary']['changes_over_attempts']:
                    st.markdown(f"- {attempt}")

                st.markdown(f"🕒 Timestamp: `{fb.get('timestamp')}`")

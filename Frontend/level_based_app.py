import streamlit as st
import requests
from datetime import datetime, timedelta
import time

API_URL = "http://localhost:8000/api/v1/code-assessment"

LEVELS = [
    {"level": "easy", "count": 2, "time_limit": 300},  # 5 min
    {"level": "medium", "count": 1, "time_limit": 600}  # 10 min
]

language_options = {
    "Python": 71,
    "Java": 62,
    "JavaScript": 63,
    "C": 50,
    "C++": 54,
    "C#": 51
}

# 🧠 Session state
if "questions" not in st.session_state:
    st.session_state.questions = []
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "user_code" not in st.session_state:
    st.session_state.user_code = ""
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "level_pointer" not in st.session_state:
    st.session_state.level_pointer = 0
if "level_question_counter" not in st.session_state:
    st.session_state.level_question_counter = 0

st.set_page_config(
    page_title="AI Code Assessment",
    layout="wide",
    initial_sidebar_state="auto",
    page_icon="🎯"
)

st.title("🎯 AI Code Assessment")

# 🔁 Load next question

def load_next_question():
    level_config = LEVELS[st.session_state.level_pointer]
    response = requests.get(f"{API_URL}/load-question?difficulty={level_config['level']}")
    response.raise_for_status()
    st.session_state.questions.append(response.json())
    st.session_state.start_time = datetime.now()
    st.session_state.submitted = False
    st.session_state.user_code = ""
    st.session_state.evaluation_result = None

# ▶️ Load first question
if len(st.session_state.questions) == 0:
    load_next_question()

current_question = st.session_state.questions[st.session_state.question_index]
level_config = LEVELS[st.session_state.level_pointer]

# 🧭 Header
st.caption(f"Level: {level_config['level'].capitalize()} — Question {st.session_state.level_question_counter + 1} of {level_config['count']}")

# 🕐 Timer logic
countdown_placeholder = st.empty()
remaining_time = max(
    0,
    int((st.session_state.start_time + timedelta(seconds=level_config["time_limit"]) - datetime.now()).total_seconds())
)
mins, secs = divmod(remaining_time, 60)
countdown_placeholder.markdown(f"### ⏳ Time Remaining: `{mins:02d}:{secs:02d}`")

if remaining_time == 0 and not st.session_state.submitted:
    st.warning("⏰ Time's up! You didn't submit in time.")
    st.session_state.submitted = True

# 🧪 Show Question
st.header(f"📝 {current_question['title']} ({level_config['level'].capitalize()})")
st.markdown(current_question.get("description", ""))

if current_question.get('examples'):
    st.subheader("📌 Examples")
    for example in current_question['examples']:
        st.code(f"Input:\n{example['input']}")
        st.code(f"Output:\n{example['output']}")
        if example.get("explanation"):
            st.markdown(f"💡 {example['explanation']}")

selected_language = st.selectbox("🧑‍💻 Language", list(language_options.keys()), index=0)
st.session_state.user_code = st.text_area(
    "✍️ Your Code",
    value=st.session_state.user_code,
    height=300
)

# 🚀 Submit
if st.button("🚀 Submit", disabled=st.session_state.submitted or remaining_time <= 0):
    with st.spinner("Evaluating..."):
        try:
            res = requests.post(f"{API_URL}/evaluate-code", json={
                "code": st.session_state.user_code,
                "language_id": language_options[selected_language],
                "question_id": current_question["id"]
            }, timeout=60)
            res.raise_for_status()
            st.session_state.evaluation_result = res.json()
            st.session_state.submitted = True
        except Exception as e:
            st.error(f"Submission failed: {e}")

# ✅ Feedback
if st.session_state.submitted:
    result = st.session_state.evaluation_result
    if result:
        if result.get("correct"):
            st.success("✅ Correct! Well done.")
        else:
            st.warning("❌ Incorrect. Please review your logic.")

        st.markdown("### 🎯 Output Comparison")
        st.code(f"Expected Output:\n{result.get('expected', '')}")
        st.code(f"Your Output:\n{result.get('actual', '')}")

        if result.get("feedback"):
            fb = result["feedback"]
            st.markdown("### 🧠 Recruiter Feedback")
            st.markdown(f"- Verdict: `{fb.get('verdict')}`")
            st.markdown(f"- Problem Solving Score: {fb.get('problem_solving_score_out_of_100')}")
            st.markdown(f"- Code Quality: {fb.get('code_quality_score_out_of_100')}")
    else:
        st.error("⏰ No evaluation. You missed the deadline.")

# ➡️ Next
if st.session_state.submitted:
    if st.button("➡️ Next Question"):
        st.session_state.level_question_counter += 1

        if st.session_state.level_question_counter >= level_config["count"]:
            st.session_state.level_pointer += 1
            st.session_state.level_question_counter = 0

            if st.session_state.level_pointer >= len(LEVELS):
                st.balloons()
                st.success("🎉 All levels completed! Thank you.")
                st.stop()

        st.session_state.question_index += 1
        load_next_question()
        st.rerun()

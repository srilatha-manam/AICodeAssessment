import streamlit as st
import requests

API_URL = "http://localhost:8000/code-assessment"

st.set_page_config(page_title="AI Code Assessment App", layout="wide")
st.title("AI Code Assessment App")

# Load question only once per session unless manually refreshed
if "question" not in st.session_state:
    try:
        response = requests.get(f"{API_URL}/question")
        response.raise_for_status()
        st.session_state.question = response.json()
    except Exception as e:
        st.error(f"Failed to load a question: {e}")
        st.stop()

question = st.session_state.question

# Display question
st.subheader("Problem Statement")
st.markdown(f"### {question['title']}")
st.markdown(f"**Description:** {question['description']}")
st.markdown("**Examples:**")
for i, ex in enumerate(question['examples'], 1):
    st.markdown(f"- **Example {i}:**")
    st.code(f"Input: {ex['input']}\nOutput: {ex['output']}", language="text")

# Code editor
st.subheader("Write Your Code Below")
code_input = st.text_area("Code Editor", height=300)

# Language options
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

# Submit and evaluate
if st.button("Submit Code"):
    with st.spinner("Evaluating your solution..."):
        payload = {
            "code": code_input,
            "language_id": language_id,
            "question_id": question["id"]
        }
        try:
            res = requests.post(f"{API_URL}/evaluate", json=payload)
            res.raise_for_status()
            result = res.json()

            st.success("Evaluation Completed")
            st.markdown(f"**Correct:** `{result['correct']}`")
            st.markdown(f"**Expected Output:** `{result['expected']}`")
            st.markdown(f"**Your Output:** `{result['actual']}`")
            st.markdown(f"**Status:** `{result['status']}`")

            # Show detailed feedback if present
            feedback = result.get("feedback")
            if feedback and isinstance(feedback, dict):
                st.subheader("AI Feedback")

                for category in ["correctness", "edge_cases", "readability", "structure", "error_handling", "performance"]:
                    section = feedback.get(category)
                    if section:
                        st.markdown(f"**{category.capitalize()}**")
                        st.markdown(f"- **Status:** {section.get('status', '')}")
                        st.markdown(f"- **Comments:** {section.get('comments', '')}")

                suggestions = feedback.get("suggestions", [])
                if suggestions:
                    st.markdown("**Suggestions:**")
                    for s in suggestions:
                        st.markdown(f"- {s}")

                summary = feedback.get("summary", {})
                if summary:
                    st.markdown("**Summary:**")
                    st.markdown(f"- **Overall Score:** {summary.get('overall_score', 0.0)}")
                    st.markdown(f"- **Remarks:** {summary.get('remarks', '')}")
            else:
                st.info("AI feedback is only available when your code passes all test cases and executes successfully.")
        except Exception as e:
            st.exception(f"Submission failed: {e}")

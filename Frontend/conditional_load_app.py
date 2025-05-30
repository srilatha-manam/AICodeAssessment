import streamlit as st
import requests

API_BASE = "http://localhost:8000/conditional-code-assessment"
st.set_page_config(page_title="AI Assessment", layout="centered")

# Initialize session state
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.current_question = None
    st.session_state.test_completed = False
    st.session_state.code_input = ""

# Load a question from the API
def load_question(difficulty):
    response = requests.get(f"{API_BASE}/conditional-question", params={"difficulty": difficulty})
    if response.ok:
        st.session_state.current_question = response.json()
        st.session_state.code_input = ""  # reset editor on new question
    else:
        st.error("No questions found.")

# Load the initial question if not loaded yet
if st.session_state.current_question is None:
    load_question("easy")

question = st.session_state.current_question

# Show final completion message and Restart button
if st.session_state.test_completed:
    st.info("Thank you for completing the assessment!")
    if st.button("Restart Test"):
        st.session_state.round = 1
        st.session_state.test_completed = False
        load_question("easy")
        st.experimental_rerun()

# Show the question if test is not completed
elif question:
    st.subheader(f"Round {st.session_state.round}: {question['difficultylevel']} Question")
    st.markdown(f"### {question['title']}")
    st.write(question["description"])

    st.markdown("#### Examples")
    for i, ex in enumerate(question["examples"], 1):
        st.code(f"Input: {ex['input']}\nExpected Output: {ex['output']}")

    # Code editor bound to session state
    code = st.text_area("Write your code here:", height=300, key="code_input")

    # Language selector
    languages = {
        "Python 3": 71,
        "C++": 54,
        "Java": 62,
        "C#": 51,
    }
    language = st.selectbox("Choose Language", list(languages.keys()))
    language_id = languages[language]

    if st.button("Submit Code"):
        payload = {
            "code": code,
            "language_id": language_id,
            "question_id": question["id"]
        }

        with st.spinner("Evaluating your solution..."):
            response = requests.post(f"{API_BASE}/conditional-evaluate", json=payload)

            if response.ok:
                result = response.json()
                percent = result["percentage"]
                st.success(f"You passed {result['passed_testcases']} out of {result['total_testcases']} test cases.")
                st.info(f"Score: {percent:.2f}%")

                if st.session_state.round == 1:
                    if result["qualified_for_next_round"]:
                        st.session_state.round = 2
                        st.success("You qualified for the next round! Loading medium-level question...")
                        load_question("Medium")
                        st.experimental_rerun()  # refresh UI to show new question
                    else:
                        st.error("You are not qualified for the next round.")
                        st.session_state.test_completed = True
                else:
                    st.balloons()
                    st.success("You have completed both rounds!")
                    st.session_state.test_completed = True

                st.markdown("#### Outputs")
                for i, (exp, act) in enumerate(zip(result["expected_outputs"], result["actual_outputs"]), 1):
                    st.code(f"Test {i}\nExpected: {exp}\nYour Output: {act}")
            else:
                st.error(f"Error: {response.text}")

else:
    st.warning("Question could not be loaded. Please try again later.")

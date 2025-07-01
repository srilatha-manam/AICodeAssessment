# Frontend/app.py - Complete version with enhanced feedback formatting

import streamlit as st
import requests
import json
from typing import Dict, Any
import time

API_URL = st.secrets.get("API_URL", "http://localhost:8000/code-assessment")

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

# Custom CSS for better UI and feedback display
st.markdown("""
<style>
.stAlert > div {
    padding: 1rem;
    border-radius: 0.5rem;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.error-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.info-box {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.dynamic-badge {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 1rem;
    font-size: 0.8rem;
    font-weight: bold;
}
.feedback-section {
    background-color: #f8f9fa;
    border-left: 4px solid #007bff;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 0.25rem;
}
.feedback-section h2, .feedback-section h3 {
    margin-top: 0;
    color: #495057;
}
.feedback-section p {
    margin-bottom: 0.5rem;
    line-height: 1.6;
}
.feedback-section ul {
    padding-left: 1.5rem;
}
.feedback-section li {
    margin-bottom: 0.3rem;
}
/* Better spacing for markdown content */
.stMarkdown > div > p {
    margin-bottom: 0.8rem !important;
}
.stMarkdown > div > ul {
    margin-bottom: 1rem !important;
}
.stMarkdown > div > h2 {
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
}
.stMarkdown > div > h3 {
    margin-top: 1.2rem !important;
    margin-bottom: 0.6rem !important;
}
/* Custom feedback styling */
.feedback-container {
    background: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.feedback-header {
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
.feedback-item {
    margin-bottom: 1.5rem;
    padding: 0.8rem;
    background: #f8f9fa;
    border-radius: 0.3rem;
    border-left: 3px solid #28a745;
}
.feedback-item.error {
    border-left-color: #dc3545;
}
.feedback-item.warning {
    border-left-color: #ffc107;
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 AI Code Assessment Platform")
st.markdown("*Powered by Google Gemini 1.5 Flash - Every question is unique and freshly generated*")

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Dynamic Question Generator")       
    # Main generation button   
    if st.button("🎲 New Question", type="primary", use_container_width=True):
        try:
            with st.spinner("🤖 AI is creating a unique question..."):               
                
                start_time = time.time()
                response = requests.get(f"{API_URL}/question", timeout=45)
                generation_time = time.time() - start_time                
                response.raise_for_status()
                question_data = response.json()                
                st.session_state.current_question = question_data
                st.session_state.user_code = ""  # Reset code
                st.session_state.evaluation_result = None  # Reset results
                st.session_state.questions_generated += 1
                
                st.success(f"✅ Fresh question generated in {generation_time:.1f}s!")
                st.rerun()
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to generate question: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
    
    # Language selector
    st.markdown("### 💻 Programming Language")
    language_options = {
        "Python": 71,
        "Java": 62,
        "JavaScript": 63,
        "C": 50,
        "C++": 54,
        "C#": 51
    }
    
    selected_language = st.selectbox(
        "Choose Language",
        list(language_options.keys()),
        index=0
    )  
# Main content area
if st.session_state.current_question:
    question = st.session_state.current_question
    
    # Question header with difficulty and generation info
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.header(f"📝 {question.get('title', 'Unknown Title')}")    
    with col3:
        st.markdown('<span class="dynamic-badge">🤖 AI Generated</span>', unsafe_allow_html=True)
    with col4:
        st.markdown(f"**ID:** {question.get('id', 'N/A')}")
    
    # Question description
    st.markdown("### 📋 Problem Description")
    
    description = question.get('description', 'No description available')
    st.markdown(f"""
    <div class="info-box">
    {description}
    </div>
    """, unsafe_allow_html=True)
    
    # Examples section with correct counts per difficulty
    if question.get('examples'):     
        examples = question['examples']            
        for i, example in enumerate(examples, 1):                
                col1, col2 = st.columns(2)                
                with col1:
                    st.markdown("**Input:**")
                    input_value = example.get('input', '').strip()
                    if input_value:
                        st.code(input_value, language='text')
                    else:
                        st.error("No input provided")
                
                with col2:
                    st.markdown("**Output:**")
                    output_value = example.get('output', '').strip()
                    if output_value:
                        st.code(output_value, language='text')
                    else:
                        st.error("No output provided")
                
                if example.get('explanation'):
                    st.markdown("**Explanation:**")
                    st.info(example['explanation'])
                else:
                    st.warning("No explanation provided for this example")
    
    # Code editor section
    st.markdown("### 💻 Your Solution")
    
    st.session_state.user_code = st.text_area(
        f"Write your {selected_language} solution:",
        value=st.session_state.user_code,
        height=350    
    )
    
    # Submit button section
    col1, col2, col3 = st.columns([2, 1, 1])    
    with col1:
        submit_button = st.button(
            "🚀 Submit & Evaluate", 
            type="primary", 
            disabled=not st.session_state.user_code.strip(),
            use_container_width=True
        )   
    # Code submission with enhanced feedback
    if submit_button and st.session_state.user_code.strip():
        try:
            with st.spinner("🔄 Evaluating code and generating AI feedback..."):
                submission_data = {
                    "code": st.session_state.user_code,
                    "language_id": language_options[selected_language],
                    "question_id": question['id']
                }
                
                response = requests.post(f"{API_URL}/evaluate", json=submission_data, timeout=45)
                response.raise_for_status()                
                result = response.json()
                st.session_state.evaluation_result = result
                st.rerun()
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Your code might be taking too long to execute or our AI is working hard!")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Submission failed: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
    
    # Display results with enhanced formatting
    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        
        st.markdown("---")
        st.markdown("## 📊 Evaluation Results")
        
        # Result header with better styling
        if result.get('correct'):
            st.markdown("""
            <div class="success-box">
            <h3>🎉 Perfect! Your solution is correct!</h3>
            <p>Excellent work! Your code passed all test cases. 🏆</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-box">
            <h3>🔍 Almost there! Let's debug together</h3>
            <p>Learning happens through iterations. Let's see what can be improved! 💪</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Execution details with tabs
        tab1, tab2, tab3 = st.tabs(["📊 Test Results", "🔍 Execution Details", "🤖 AI Feedback"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📥 Expected Output")
                st.code(result.get('expected', ''), language='text')
            
            with col2:
                st.markdown("### 📤 Your Output")
                actual_output = result.get('actual', '')
                if actual_output.strip():
                    st.code(actual_output, language='text')
                else:
                    st.code("No output produced", language='text')
        
        with tab2:
            # Status information
            status = result.get('status', 'Unknown')
            if 'error' in status.lower() or 'fail' in status.lower():
                st.error(f"**Execution Status:** {status}")
            elif 'accept' in status.lower():
                st.success(f"**Execution Status:** {status}")
            else:
                st.info(f"**Execution Status:** {status}")
            
            # Additional debug info
            if result.get('feedback'):
                with st.expander("🔧 Raw Feedback Data (for debugging)"):
                    st.json(result['feedback'])
        
        with tab3:
            # AI Feedback section with improved formatting
            if result.get('has_ai_feedback') and result.get('formatted_feedback'):
                # Display the formatted feedback with proper spacing and styling
                feedback_content = result['formatted_feedback']
                
                # Display the AI feedback header
                st.markdown("### 🤖 AI Code Analysis")
                
                # Display the formatted feedback content with HTML support
                st.markdown(feedback_content, unsafe_allow_html=True)                
                # Action buttons after feedback
              
                
            elif result.get('feedback'):
                st.markdown("### 🤖 AI Analysis")
                st.json(result['feedback'])
            else:
                st.info("💡 AI feedback will be available once your code executes successfully. Keep trying! 🚀")


    # Quick start buttons with enhanced styling
    st.markdown("### 🚀 Quick Start Options")  
       
    # Feature highlights
    st.markdown("---")
    st.markdown("### 🎯 Feedback Analysis Features:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🟢 Success Feedback:**
        - Overall Assessment (score & recommendation)
        - Detailed section analysis (8 categories)
        - Line-by-line breakdown
        - Actionable suggestions
        """)
    
    with col2:
        st.markdown("""
        **🔴 Failure Feedback:**
        - Error Analysis (root cause identification)
        - Output Comparison (why it differs)
        - Step-by-step fixes
        - Debugging strategies
        """)    
   
    
    # Additional feature showcase
    st.markdown("---")
    st.markdown("### 🔍 What Makes Our AI Feedback Special:")
    
    # Create an example feedback display
    st.markdown("#### Example Success Feedback Format:")
    st.markdown("""
    ```
    Overall Assessment
    Score: 8.5/10
    Recommendation: REVIEW
    Complexity: low
    Simplicity: excellent

    ✅ Correctness
    Status: pass
    Score: 10/10

    The code correctly identifies and counts the unique elements...

    🧩 Complexity
    Status: appropriate
    Score: 10/10

    The solution uses a concise and efficient approach...

    💡 Intelligent Suggestions
    • Add input validation for edge cases
    • Consider adding docstrings for better documentation
    • Implement error handling for robustness
    ```
    """)
    
    st.markdown("#### Example Failure Feedback Format:")
    st.markdown("""
    ```
    Error Analysis
    Primary Error: Logic Error - Wrong Output
    Location: In the main algorithm loop
    Root Cause: Incorrect handling of edge cases
    Severity: MAJOR

    📊 Output Comparison

    Why Output Differs:
    Your code handles the basic case correctly but fails on edge cases...

    🛠️ How to Fix Your Code
    • Check your loop termination condition
    • Add validation for empty inputs
    • Review the algorithm logic for boundary cases

    🐛 Debugging Tips
    • Use print statements to trace variable values
    • Test with the provided examples step by step
    • Consider edge cases like empty arrays or single elements
    ```
    """)

# Footer with enhanced stats
st.markdown("---")
st.markdown("""
---
*🤖 Powered by Google Gemini 1.5 Flash for unlimited, original question generation*  

""")
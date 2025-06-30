# Backend/services/feedback_generation_service.py - Fixed formatting

import google.generativeai as genai
import json
import asyncio
from typing import Dict, Any, Optional

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyA2yG9LDl-UnfWv7B1UnsjXPXoa8Qk-3_s"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_feedback_for_success(code: str, question_desc: str, language: str = "Python") -> dict:
    """
    Generate comprehensive feedback for successfully executed code
    """
    prompt = f"""
You are an expert code reviewer and mentor. Analyze the following {language} code submission for a coding assessment.

**Problem Statement:**
{question_desc}

**Submitted Code:**
```{language.lower()}
{code}
```

**Evaluation Criteria:**
Please provide detailed feedback in the following JSON format. Be constructive, specific, and educational in your comments.

Evaluate based on:
1. **Correctness** - Does the code solve the problem correctly?
2. **Code Complexity** - Is the solution appropriately complex or over-engineered?
3. **Simplicity** - Is the code clean, readable, and easy to understand?
4. **Edge Cases** - Does it handle boundary conditions and edge cases?
5. **Error Handling** - Are potential errors and exceptions handled?
6. **Performance** - Is the solution efficient in terms of time/space complexity?
7. **Code Structure** - Is the code well-organized and follows best practices?
8. **Readability** - Are variable names meaningful and is the code self-documenting?

**Required JSON Response Format:**
{{
    "feedback": {{
        "correctness": {{
            "status": "pass/fail/partial",
            "score": 0-10,
            "comments": "Detailed analysis of correctness"
        }},
        "complexity": {{
            "status": "appropriate/over-engineered/too-simple",
            "score": 0-10,
            "comments": "Analysis of solution complexity and appropriateness"
        }},
        "simplicity": {{
            "status": "excellent/good/poor",
            "score": 0-10,
            "comments": "Evaluation of code simplicity and clarity"
        }},
        "edge_cases": {{
            "status": "pass/fail/partial",
            "score": 0-10,
            "comments": "Assessment of edge case handling"
        }},
        "error_handling": {{
            "status": "pass/fail/partial",
            "score": 0-10,
            "comments": "Evaluation of error handling mechanisms"
        }},
        "performance": {{
            "status": "excellent/good/poor",
            "score": 0-10,
            "comments": "Time and space complexity analysis"
        }},
        "structure": {{
            "status": "excellent/good/poor",
            "score": 0-10,
            "comments": "Code organization and structure assessment"
        }},
        "readability": {{
            "status": "excellent/good/poor",
            "score": 0-10,
            "comments": "Code readability and documentation evaluation"
        }}
    }},
    "intelligent_suggestions": [
        "Specific, actionable improvement suggestions",
        "Best practice recommendations",
        "Performance optimization tips",
        "Code simplification ideas"
    ],
    "positive_aspects": [
        "Things the code does well",
        "Good practices demonstrated"
    ],
    "areas_for_improvement": [
        "Specific areas that need work",
        "Common pitfalls to avoid"
    ],
    "summary": {{
        "overall_score": 0.0-10.0,
        "complexity_rating": "low/medium/high",
        "simplicity_rating": "excellent/good/needs-improvement",
        "remarks": "Overall assessment and key takeaways",
        "recommendation": "accept/review/reject"
    }}
}}

Please provide only valid JSON without any additional text or formatting.
"""
    return await _generate_feedback_response(prompt)

async def generate_feedback_for_failure(
    code: str, 
    question_desc: str, 
    correctness: bool,
    status: str,
    expected: str,
    actual_output: str,
    error_message: Optional[str] = None,
    language: str = "Python"
) -> dict:
    """
    Generate comprehensive feedback for failed code execution
    """
    
    # Determine the type of failure
    failure_type = _determine_failure_type(status, error_message, actual_output)
    
    prompt = f"""
You are an expert programming mentor specializing in debugging and error analysis. A student has submitted code that failed to execute properly or produced incorrect output.

**Problem Statement:**
{question_desc}

**Submitted Code:**
```{language.lower()}
{code}
```

**Execution Results:**
- **Correctness:** {"Correct" if correctness else "Incorrect"}
- **Status:** {status}
- **Expected Output:** {expected}
- **Actual Output:** {actual_output}
- **Error Message:** {error_message if error_message else "No error message"}
- **Failure Type:** {failure_type['type']}
- **Failure Description:** {failure_type['description']}

**Your Task:**
Analyze the code failure and provide educational feedback that helps the student understand:
1. **What went wrong** - Identify the specific errors
2. **Why it happened** - Explain the root cause
3. **How to fix it** - Provide concrete solutions
4. **How to prevent similar errors** - Share best practices

**Required JSON Response Format:**
{{
    "feedback": {{
        "error_analysis": {{
            "primary_error": "Main error identified",
            "error_location": "Where in the code the error occurs",
            "root_cause": "Why this error happened",
            "severity": "critical/major/minor"
        }},
        "correctness": {{
            "status": "fail",
            "score": 0-4,
            "comments": "Detailed analysis of what makes the output incorrect"
        }},
        "syntax_errors": {{
            "status": "pass/fail",
            "score": 0-10,
            "comments": "Analysis of syntax issues if any"
        }},
        "logic_errors": {{
            "status": "pass/fail", 
            "score": 0-10,
            "comments": "Analysis of logical mistakes in the algorithm"
        }},
        "runtime_errors": {{
            "status": "pass/fail",
            "score": 0-10,
            "comments": "Analysis of runtime exceptions and their causes"
        }},
        "edge_cases": {{
            "status": "fail/partial",
            "score": 0-10,
            "comments": "Assessment of edge case handling failures"
        }},
        "code_structure": {{
            "status": "good/poor",
            "score": 0-10,
            "comments": "Structure issues that might contribute to errors"
        }}
    }},
    "error_solutions": [
        "Step-by-step solution to fix the primary error",
        "Code corrections needed",
        "Alternative approaches to consider"
    ],
    "debugging_tips": [
        "How to debug this type of error",
        "Tools and techniques for troubleshooting",
        "Common debugging strategies"
    ],
    "code_improvements": [
        "Specific code changes needed",
        "Better variable names or structure",
        "Input validation improvements"
    ],
    "learning_points": [
        "Key concepts the student should review",
        "Common mistakes to avoid",
        "Best practices related to this error"
    ],
    "expected_vs_actual": {{
        "difference_explanation": "Clear explanation of why output differs from expected",
        "output_analysis": "Analysis of what the actual output represents",
        "correction_strategy": "How to align output with expectations"
    }},
    "summary": {{
        "error_type": "{failure_type['type']}",
        "fix_difficulty": "easy/medium/hard",
        "estimated_fix_time": "time estimate to fix the error",
        "priority_fixes": ["Most important fixes to make first"],
        "encouragement": "Positive message to motivate the student",
        "next_steps": "What the student should do next"
    }}
}}

Focus on being educational, encouraging, and providing actionable advice. Help the student learn from their mistakes.
Please provide only valid JSON without any additional text or formatting.
"""

    return await _generate_feedback_response(prompt)

def _determine_failure_type(status: str, error_message: Optional[str], actual_output: str) -> dict:
    """Determine the type of failure based on execution results"""
    status_lower = status.lower()
    
    failure_info = {
        "type": "",
        "description": ""
    }
    
    if "compilation error" in status_lower or "compile" in status_lower:
        failure_info["type"] = "Compilation Error"
        failure_info["description"] = "The code failed to compile due to syntax or structural issues."
    elif "runtime error" in status_lower or "exception" in status_lower:
        failure_info["type"] = "Runtime Error"
        failure_info["description"] = "The code encountered an error during execution."
    elif "time limit exceeded" in status_lower:
        failure_info["type"] = "Time Limit Exceeded"
        failure_info["description"] = "The code took too long to execute."
    elif "memory limit exceeded" in status_lower:
        failure_info["type"] = "Memory Limit Exceeded"
        failure_info["description"] = "The code used too much memory."
    elif error_message and any(err in error_message.lower() for err in ["syntax", "indentation", "invalid syntax"]):
        failure_info["type"] = "Syntax Error"
        failure_info["description"] = "The code contains invalid syntax."
    elif actual_output and actual_output.strip() != "":
        failure_info["type"] = "Logic Error - Wrong Output"
        failure_info["description"] = "The code produced incorrect output."
    else:
        failure_info["type"] = "Unknown Error"
        failure_info["description"] = "An unidentified error occurred."
    
    return failure_info

async def _generate_feedback_response(prompt: str) -> dict:
    """Common function to generate feedback using Gemini API"""
    try:
        # Generate response using Gemini
        response = await asyncio.to_thread(_generate_gemini_response, prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No valid JSON found in response")
        
        json_text = response_text[start_idx:end_idx]
        feedback_data = json.loads(json_text)
        
        return feedback_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return _generate_fallback_feedback(f"JSON parsing failed: {str(e)}")
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _generate_fallback_feedback(f"AI feedback generation failed: {str(e)}")

def _generate_gemini_response(prompt: str):
    """Synchronous wrapper for Gemini API call"""
    return model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2000,
            top_p=0.8,
            top_k=40
        )
    )

def _generate_fallback_feedback(error_message: str) -> dict:
    """Generate a basic feedback structure when AI generation fails"""
    return {
        "feedback": {
            "error_analysis": {
                "primary_error": "Unable to analyze due to AI service error",
                "error_location": "Unknown",
                "root_cause": "AI feedback service unavailable",
                "severity": "unknown"
            }
        },
        "error_solutions": [
            "AI feedback service is currently unavailable",
            "Please try submitting your code again later"
        ],
        "summary": {
            "error_type": "Service Error",
            "encouragement": "Don't give up! Try again when the service is available.",
            "next_steps": "Retry your submission"
        },
        "error": error_message
    }

# FIXED - Enhanced feedback display function for SUCCESS cases
def format_feedback_for_display(feedback_data: dict) -> str:
    """Format SUCCESS feedback data with proper line-by-line display"""
    if "error" in feedback_data:
        return f"⚠️ **Feedback Generation Error:** {feedback_data['error']}"
    
    try:
        feedback = feedback_data.get('feedback', {})
        summary = feedback_data.get('summary', {})
        
        # Use HTML formatting with proper line breaks
        formatted_output = []
        
        # Overall Assessment - Each item on separate line
        overall_score = summary.get('overall_score', 0)
        recommendation = summary.get('recommendation', 'unknown')
        complexity = summary.get('complexity_rating', 'unknown')
        simplicity = summary.get('simplicity_rating', 'unknown')
        
        formatted_output.append("<h2>Overall Assessment</h2>")
        formatted_output.append(f"<p><strong>Score:</strong> {overall_score}/10<br>")
        formatted_output.append(f"<strong>Recommendation:</strong> {recommendation.upper()}<br>")
        formatted_output.append(f"<strong>Complexity:</strong> {complexity}<br>")
        formatted_output.append(f"<strong>Simplicity:</strong> {simplicity}</p>")
        formatted_output.append("<br>")
        
        # Detailed feedback sections - Each with clear separation
        section_emojis = {
            'correctness': '✅',
            'complexity': '🧩',
            'simplicity': '🎯',
            'edge_cases': '🔍',
            'error_handling': '🛡️',
            'performance': '⚡',
            'structure': '🏗️',
            'readability': '📖'
        }
        
        for section, emoji in section_emojis.items():
            if section in feedback:
                section_data = feedback[section]
                status = section_data.get('status', 'unknown')
                score = section_data.get('score', 0)
                comments = section_data.get('comments', '')
                
                formatted_output.append(f"<h2>{emoji} {section.replace('_', ' ').title()}</h2>")
                formatted_output.append(f"<p><strong>Status:</strong> {status}<br>")
                formatted_output.append(f"<strong>Score:</strong> {score}/10</p>")
                formatted_output.append(f"<p>{comments}</p>")
                formatted_output.append("<br>")
        
        # Suggestions and improvements - Each on separate lines
        suggestions = feedback_data.get('intelligent_suggestions', [])
        if suggestions:
            formatted_output.append("<h2>💡 Intelligent Suggestions</h2>")
            formatted_output.append("<ul>")
            for suggestion in suggestions:
                formatted_output.append(f"<li>{suggestion}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        positive_aspects = feedback_data.get('positive_aspects', [])
        if positive_aspects:
            formatted_output.append("<h2>✨ What You Did Well</h2>")
            formatted_output.append("<ul>")
            for aspect in positive_aspects:
                formatted_output.append(f"<li>{aspect}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        improvements = feedback_data.get('areas_for_improvement', [])
        if improvements:
            formatted_output.append("<h2>🎯 Areas for Improvement</h2>")
            formatted_output.append("<ul>")
            for improvement in improvements:
                formatted_output.append(f"<li>{improvement}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        # Final remarks
        remarks = summary.get('remarks', '')
        if remarks:
            formatted_output.append("<h2>📝 Final Remarks</h2>")
            formatted_output.append(f"<p>{remarks}</p>")
        
        return "".join(formatted_output)
        
    except Exception as e:
        return f"⚠️ **Error formatting feedback:** {str(e)}"

def format_failure_feedback_for_display(feedback_data: dict) -> str:
    """Format FAILURE feedback data with proper line-by-line display"""
    if "error" in feedback_data:
        return f"⚠️ **Feedback Generation Error:** {feedback_data['error']}"
    
    try:
        # Use HTML formatting with proper line breaks
        formatted_output = []
        
        # Error Analysis Section - Each item on separate line
        if "error_analysis" in feedback_data.get("feedback", {}):
            error_analysis = feedback_data["feedback"]["error_analysis"]
            formatted_output.append("<h2>Error Analysis</h2>")
            formatted_output.append(f"<p><strong>Primary Error:</strong> {error_analysis.get('primary_error', 'Unknown')}<br>")
            formatted_output.append(f"<strong>Location:</strong> {error_analysis.get('error_location', 'Unknown')}<br>")
            formatted_output.append(f"<strong>Root Cause:</strong> {error_analysis.get('root_cause', 'Unknown')}<br>")
            formatted_output.append(f"<strong>Severity:</strong> {error_analysis.get('severity', 'Unknown').upper()}</p>")
            formatted_output.append("<br>")
        
        # Expected vs Actual Output - Each item on separate line
        if "expected_vs_actual" in feedback_data:
            expected_vs_actual = feedback_data["expected_vs_actual"]
            formatted_output.append("<h2>📊 Output Comparison</h2>")
            formatted_output.append(f"<p><strong>Why Output Differs:</strong><br>")
            formatted_output.append(f"{expected_vs_actual.get('difference_explanation', '')}</p>")
            formatted_output.append(f"<p><strong>Your Output Analysis:</strong><br>")
            formatted_output.append(f"{expected_vs_actual.get('output_analysis', '')}</p>")
            formatted_output.append(f"<p><strong>How to Fix:</strong><br>")
            formatted_output.append(f"{expected_vs_actual.get('correction_strategy', '')}</p>")
            formatted_output.append("<br>")
        
        # Solutions - Each on separate lines
        solutions = feedback_data.get('error_solutions', [])
        if solutions:
            formatted_output.append("<h2>🛠️ How to Fix Your Code</h2>")
            formatted_output.append("<ul>")
            for solution in solutions:
                formatted_output.append(f"<li>{solution}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        # Code Improvements - Each on separate lines
        improvements = feedback_data.get('code_improvements', [])
        if improvements:
            formatted_output.append("<h2>💡 Code Improvements Needed</h2>")
            formatted_output.append("<ul>")
            for improvement in improvements:
                formatted_output.append(f"<li>{improvement}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        # Debugging Tips - Each on separate lines
        debugging_tips = feedback_data.get('debugging_tips', [])
        if debugging_tips:
            formatted_output.append("<h2>🐛 Debugging Tips</h2>")
            formatted_output.append("<ul>")
            for tip in debugging_tips:
                formatted_output.append(f"<li>{tip}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        # Learning Points - Each on separate lines
        learning_points = feedback_data.get('learning_points', [])
        if learning_points:
            formatted_output.append("<h2>📚 What to Study Next</h2>")
            formatted_output.append("<ul>")
            for point in learning_points:
                formatted_output.append(f"<li>{point}</li>")
            formatted_output.append("</ul>")
            formatted_output.append("<br>")
        
        # Summary and Encouragement - Each item on separate line
        summary = feedback_data.get('summary', {})
        if summary:
            formatted_output.append("<h2>📝 Summary</h2>")
            formatted_output.append(f"<p><strong>Error Type:</strong> {summary.get('error_type', 'Unknown')}<br>")
            formatted_output.append(f"<strong>Fix Difficulty:</strong> {summary.get('fix_difficulty', 'Unknown')}<br>")
            formatted_output.append(f"<strong>Estimated Fix Time:</strong> {summary.get('estimated_fix_time', 'Unknown')}</p>")
            
            priority_fixes = summary.get('priority_fixes', [])
            if priority_fixes:
                formatted_output.append("<p><strong>Priority Fixes:</strong></p>")
                formatted_output.append("<ul>")
                for fix in priority_fixes:
                    formatted_output.append(f"<li>{fix}</li>")
                formatted_output.append("</ul>")
            
            if summary.get('encouragement'):
                formatted_output.append(f"<p><strong>💪 {summary['encouragement']}</strong></p>")
            
            if summary.get('next_steps'):
                formatted_output.append(f"<p><strong>Next Steps:</strong><br>")
                formatted_output.append(f"{summary['next_steps']}</p>")
        
        return "".join(formatted_output)
        
    except Exception as e:
        return f"⚠️ **Error formatting feedback:** {str(e)}"

# Helper function to map language IDs to language names
def get_language_name(language_id: int) -> str:
    """Map Judge0 language IDs to language names"""
    language_map = {
        71: "Python",
        62: "Java", 
        63: "JavaScript",
        50: "C",
        54: "C++",
        51: "C#",
        72: "Ruby",
        73: "Rust",
        74: "TypeScript",
        # Add more mappings as needed
    }
    return language_map.get(language_id, "Python")  # Default to Python

# Legacy function for backward compatibility
async def generate_feedback(code: str, question_desc: str, language: str = "Python") -> dict:
    """Legacy function - redirects to success feedback generation"""
    return await generate_feedback_for_success(code, question_desc, language)
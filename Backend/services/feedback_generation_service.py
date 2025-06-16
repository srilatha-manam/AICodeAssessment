import google.generativeai as genai
import json
import asyncio
from typing import Dict, Any

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDS0SXbtLKaawt2IdjTezO8HzsaSoM6RJM"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_feedback(code: str, question_desc: str, language: str = "Python") -> dict:
    """
    Generate comprehensive feedback for submitted code using Gemini 1.5 Flash
    
    Args:
        code: The submitted code to evaluate
        question_desc: Description of the coding problem
        language: Programming language used (default: Python)
    
    Returns:
        Dictionary containing structured feedback
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
        
        # Validate the structure
        if not _validate_feedback_structure(feedback_data):
            raise ValueError("Invalid feedback structure")
        
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
            temperature=0.3,  # Lower temperature for more consistent JSON
            max_output_tokens=2000,
            top_p=0.8,
            top_k=40
        )
    )

def _validate_feedback_structure(feedback_data: Dict[Any, Any]) -> bool:
    """Validate that the feedback has the expected structure"""
    try:
        required_sections = [
            'correctness', 'complexity', 'simplicity', 'edge_cases',
            'error_handling', 'performance', 'structure', 'readability'
        ]
        
        if 'feedback' not in feedback_data:
            return False
        
        feedback = feedback_data['feedback']
        for section in required_sections:
            if section not in feedback:
                return False
            if not all(key in feedback[section] for key in ['status', 'score', 'comments']):
                return False
        
        # Check for required top-level keys
        required_keys = ['intelligent_suggestions', 'summary']
        for key in required_keys:
            if key not in feedback_data:
                return False
        
        return True
    except:
        return False

def _generate_fallback_feedback(error_message: str) -> dict:
    """Generate a basic feedback structure when AI generation fails"""
    return {
        "feedback": {
            "correctness": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate correctness due to AI service error"
            },
            "complexity": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate complexity"
            },
            "simplicity": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate simplicity"
            },
            "edge_cases": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate edge case handling"
            },
            "error_handling": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate error handling"
            },
            "performance": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate performance"
            },
            "structure": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate code structure"
            },
            "readability": {
                "status": "unknown",
                "score": 0,
                "comments": "Unable to evaluate readability"
            }
        },
        "intelligent_suggestions": [
            "AI feedback service is currently unavailable",
            "Please try submitting your code again later"
        ],
        "positive_aspects": [],
        "areas_for_improvement": [],
        "summary": {
            "overall_score": 0.0,
            "complexity_rating": "unknown",
            "simplicity_rating": "unknown",
            "remarks": f"Feedback generation failed: {error_message}",
            "recommendation": "retry"
        },
        "error": error_message
    }

# Enhanced feedback display function for better user experience
def format_feedback_for_display(feedback_data: dict) -> str:
    """Format feedback data for better display in Streamlit"""
    if "error" in feedback_data:
        return f"⚠️ **Feedback Generation Error:** {feedback_data['error']}"
    
    try:
        feedback = feedback_data.get('feedback', {})
        summary = feedback_data.get('summary', {})
        
        formatted_output = []
        
        # Overall score and recommendation
        overall_score = summary.get('overall_score', 0)
        recommendation = summary.get('recommendation', 'unknown')
        
        formatted_output.append(f"## 📊 Overall Assessment")
        formatted_output.append(f"**Score:** {overall_score}/10")
        formatted_output.append(f"**Recommendation:** {recommendation.upper()}")
        formatted_output.append(f"**Complexity:** {summary.get('complexity_rating', 'unknown')}")
        formatted_output.append(f"**Simplicity:** {summary.get('simplicity_rating', 'unknown')}")
        formatted_output.append("")
        
        # Detailed feedback sections
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
                
                formatted_output.append(f"### {emoji} {section.replace('_', ' ').title()}")
                formatted_output.append(f"**Status:** {status} | **Score:** {score}/10")
                formatted_output.append(f"{comments}")
                formatted_output.append("")
        
        # Suggestions and improvements
        suggestions = feedback_data.get('intelligent_suggestions', [])
        if suggestions:
            formatted_output.append("## 💡 Intelligent Suggestions")
            for suggestion in suggestions:
                formatted_output.append(f"• {suggestion}")
            formatted_output.append("")
        
        positive_aspects = feedback_data.get('positive_aspects', [])
        if positive_aspects:
            formatted_output.append("## ✨ What You Did Well")
            for aspect in positive_aspects:
                formatted_output.append(f"• {aspect}")
            formatted_output.append("")
        
        improvements = feedback_data.get('areas_for_improvement', [])
        if improvements:
            formatted_output.append("## 🎯 Areas for Improvement")
            for improvement in improvements:
                formatted_output.append(f"• {improvement}")
            formatted_output.append("")
        
        # Final remarks
        remarks = summary.get('remarks', '')
        if remarks:
            formatted_output.append("## 📝 Final Remarks")
            formatted_output.append(remarks)
        
        return "\n".join(formatted_output)
        
    except Exception as e:
        return f"⚠️ **Error formatting feedback:** {str(e)}"



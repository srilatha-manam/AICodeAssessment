import random
from ..models.code_evaluation_model import CodeSubmission, EvaluationResult
from .question_loader_service import load_random_question 
from .question_loader_service import load_all_questions
from .solution_evaluation_service import evaluate_code
from ..logging_config import logger
from .feedback_generation_service import generate_feedback
import ast

# This module provides functionality to evaluate code submissions against predefined questions.

#Define a function called get_random_question that returns a random question from the questions list
async def get_random_question():
    return await load_random_question()

# Define an asynchronous function to evaluate a code submission
async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:      
    # Load all questions from the database
    print("inside evaluate submission")
    questions = await load_all_questions()
    # Find the question that matches the submission's question ID
    question = next((q for q in questions if q.id == submission.question_id), None)

    # If no question is found, raise an error
    if not question:
        logger.error(f"Invalid Question ID: {submission.question_id}")
        raise ValueError("Invalid Question ID")

    try:
        # Initialize a flag to check if all test cases passed
        all_passed = True
        # Initialize lists to store actual and expected outputs
        actual_outputs = []
        expected_outputs = []

        # Iterate through each example in the question
        for idx, example in enumerate(question.examples, start=1):
            # Get the input and expected output for the example                      
            test_input = example.input.strip()           
            expected_output = example.output.strip()          
            # Add the expected output to the list
            expected_outputs.append(expected_output)
            print(test_input)
            print("expected output:", expected_output)
            # Log the input for the example
            #logger.info(f"Running test case {idx}: input={test_input!r}")            
            # Evaluate the code with the input
            result = await evaluate_code(submission.code, submission.language_id, test_input)
            # Get the actual output from the result
            print(result)
            actual_output = (result.get("stdout") or "").strip()  
            print("actual output:", actual_output)     
            # Add the actual output to the list
            actual_outputs.append(actual_output)

            # If the actual output does not match the expected output, log an error and set the flag to False
            if actual_output != expected_output:
                logger.error(
                    f"Test case {idx} failed: expected={expected_output!r}, actual={actual_output!r}"
                )
                all_passed = False
                break
           

    except Exception as e:
        # Log a critical error if the code evaluation fails
        logger.critical(
            f"Code evaluation failed for Question ID {submission.question_id}: {e}",
            exc_info=True
        )
        # Raise a ValueError
        raise ValueError("Error evaluating code")    
    
    feedback = await generate_feedback(submission.code, question.description)
    #print(feedback)
    # Return an EvaluationResult object with the results of the evaluation
    return  EvaluationResult(
        correct=all_passed,
        expected="\n".join(expected_outputs),
        actual="\n".join(actual_outputs),
        status=result.get("status", {}).get("description", "Unknown"),
        feedback=feedback
    )

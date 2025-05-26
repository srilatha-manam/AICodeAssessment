from pydantic import BaseModel
# This module defines the data models used for code evaluation and submission.

class Question(BaseModel):
    # Define a class called Question that inherits from BaseModel
    id: int
    question: str
    test_input: str
    expected_output: str

class CodeSubmission(BaseModel):
    # The code submitted by the user
    code: str
    # The ID of the programming language used
    language_id: int
    # The ID of the question the code is submitted for
    question_id: int

class EvaluationResult(BaseModel):
    # This class represents the result of an evaluation
    correct: bool
    expected: str
    actual: str
    status: str

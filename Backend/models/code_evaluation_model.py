from pydantic import BaseModel
from typing import List
# This module defines the data models used for code evaluation and submission.

class Example(BaseModel):
    # This class represents an example input/output pair for a question
    input: str
    output: str

    def __str__(self):
        return f"Input: {self.input}, Output: {self.output}"

class Question(BaseModel):
    id: int
    problem_name: str
    description: str
    constraints: str
    examples: List[Example]
    difficulty_level: str
    

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

from pydantic import BaseModel
from typing import List, Optional

# This module defines the data models used for code evaluation and submission.
#
class Example(BaseModel):
    # This class represents an example input/output pair for a question
    input: str
    output: str
    explanation: Optional[str] = None

    def __str__(self):
        return f"Input: {self.input}, Output: {self.output},Explanation: {self.explanation}"

class Question(BaseModel):
    # This class represents a question
    id: int
    title: str
    description: str
    #constraints: str
    examples: List[Example]
    difficultylevel: str
    

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
    feedback: Optional[dict] = None
    full_judge_response: Optional[dict] = None

class DifficultyRequest(BaseModel):
    # This class represents a request to get questions by difficulty level
    difficulty: str

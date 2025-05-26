import csv
from pathlib import Path
from typing import List
from .models import Question
# This module loads questions from a CSV file and returns them as a list of Question objects.

# The CSV file is located in the 'data' directory, and it has the following columns:
# question_id, question, test_input, test_output
DATA_FILE = Path(__file__).resolve().parent.parent / "data.csv"

# Define a function to load questions from a CSV file
def load_questions() -> List[Question]:
    # Open the CSV file
    with open(DATA_FILE, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [
            # Create a Question object for each row in the CSV file
            Question(
                id=int(row['question_id']),
                question=row['question'],
                test_input=row['test_input'],
                expected_output=row['test_output']
            )
            for row in reader
        ]

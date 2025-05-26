import csv
from pathlib import Path
from typing import List
from .models import Question
from logging_config import logger

# This module loads questions from a CSV file and returns them as a list of Question objects.

# The CSV file is located in the 'data' directory, and it has the following columns:
# question_id, question, test_input, test_output
DATA_FILE = Path(__file__).resolve().parent.parent / "coding_questions.csv"

# Define a function to load questions from a CSV file
def load_questions() -> List[Question]:
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            questions = [
                Question(
                    id=int(row['question_id']),
                    question=row['question'],
                    test_input=row['test_input'],
                    expected_output=row['test_output']
                )
                for row in reader
            ]
            return questions
    except FileNotFoundError:
        logger.critical(f"CSV file not found: {DATA_FILE}", exc_info=True)
        raise
    except KeyError as e:
        logger.error(f"Missing expected column in CSV: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Unexpected error while loading questions: {e}", exc_info=True)
        raise

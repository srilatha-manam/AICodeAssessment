import csv
from pathlib import Path    
from typing import List
from ..models.code_evaluation_model import Question
from ..logging_config import logger
import random
import json
from ..models.code_evaluation_model import Example

# This module loads questions from a CSV file and returns them as a list of Question objects.

# path to the CSV file containing questions
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "questions.csv"

# Define a function to load questions from a CSV file
def load_random_question() -> Question:
    try:
        with open(DATA_FILE, newline='', encoding='cp1252') as file:
            reader = csv.DictReader(file)
            questions = []
            for row in reader:
                try:
                    # Parse JSON-like examples field
                    examples = json.loads(row['examples'])
                    # Convert each example dictionary to an Example model
                    parsed_examples = [Example(**ex) for ex in examples]
                    question = Question(
                        id=int(row['id']),
                        title=row['title'],
                        description=row['description'],
                        #constraints=row['constraints'],
                        examples=parsed_examples,
                        difficultylevel=row['difficultylevel']
                    )
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"Skipping row due to error: {e}")
                    continue

            # Pick one at random
            return random.choice(questions)

    except FileNotFoundError:
        logger.critical(f"CSV file not found: {DATA_FILE}", exc_info=True)
        raise
    except KeyError as e:
        logger.error(f"Missing expected column in CSV: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Unexpected error while loading questions: {e}", exc_info=True)
        raise
def load_all_questions() -> List[Question]:
    try:
        with open(DATA_FILE, newline='', encoding='cp1252') as file:
            reader = csv.DictReader(file)
            questions = []
            for row in reader:
                try:
                    examples = json.loads(row['examples'])
                    parsed_examples = [Example(**ex) for ex in examples]
                    question = Question(
                        id=int(row['id']),
                        title=row['title'],
                        description=row['description'],
                        #constraints=row['constraints'],
                        examples=parsed_examples,
                        difficultylevel=row['difficultylevel']
                    )
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"Skipping row due to error: {e}")
                    continue
            return questions
    except Exception as e:
        logger.critical(f"Error loading questions: {e}", exc_info=True)
        raise
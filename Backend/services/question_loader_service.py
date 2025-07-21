import pandas as pd
import json
import os
import re
import random
import time
from typing import List, Optional
from functools import wraps
from models.code_evaluation_model import Question, Example
from logging_config import logger

CSV_FILE_PATH = "data/cleaned_formatted_problems.csv"

# === Retry Decorator ===
def retry(max_attempts=3, delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logger.warning(f"Retry {attempts}/{max_attempts} for {func.__name__} due to error: {e}")
                    time.sleep(delay)
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2, exceptions=(Exception,))
def read_csv_with_retry(path):
    return pd.read_csv(path, on_bad_lines='skip', engine='python')

@retry(max_attempts=2, delay=0.5, exceptions=(json.JSONDecodeError,))
def safe_json_loads(data: str):
    return json.loads(data)

def repair_json_string(json_str: str) -> str:
    try:
        json_str = re.sub(r'"([^"]+)""', r'"\1"', json_str)
        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
        lines = json_str.split('\n')
        fixed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.endswith(',') and line.count('"') % 2 == 1:
                last_quote_idx = line.rfind('"')
                if last_quote_idx > 0:
                    line = line[:last_quote_idx+1] + '"' + line[last_quote_idx+1:]
            fixed_lines.append(line)
        json_str = '\n'.join(fixed_lines)
        json_str = re.sub(r'}\s*{', '}, {', json_str)
        if json_str.strip().endswith(','):
            json_str = json_str.strip()[:-1]
        if not json_str.strip().startswith('['):
            json_str = '[' + json_str
        if not json_str.strip().endswith(']'):
            json_str = json_str + ']'
        return json_str
    except Exception as e:
        logger.warning(f"JSON repair failed: {e}")
        return json_str

def extract_examples_safely(json_str: str) -> List[dict]:
    try:
        return safe_json_loads(json_str)
    except json.JSONDecodeError:
        pass

    try:
        repaired_json = repair_json_string(json_str)
        return safe_json_loads(repaired_json)
    except json.JSONDecodeError:
        pass

    try:
        examples = []
        input_pattern = r'"input":\s*"([^"]*(?:\\.[^"]*)*)"'
        output_pattern = r'"output":\s*"([^"]*(?:\\.[^"]*)*)"'
        explanation_pattern = r'"explanation":\s*"([^"]*(?:\\.[^"]*)*)"'
        inputs = re.findall(input_pattern, json_str)
        outputs = re.findall(output_pattern, json_str)
        explanations = re.findall(explanation_pattern, json_str)
        for i, input_val in enumerate(inputs):
            output_val = outputs[i] if i < len(outputs) else ""
            explanation_val = explanations[i] if i < len(explanations) else ""
            example = {
                "input": input_val.replace('\\"', '"'),
                "output": output_val.replace('\\"', '"'),
                "explanation": explanation_val.replace('\\"', '"')
            }
            examples.append(example)
        if examples:
            logger.info(f"Extracted {len(examples)} examples using regex fallback")
            return examples
    except Exception as e:
        logger.error(f"Regex extraction failed: {e}")
    
    logger.warning("All parsing strategies failed, creating minimal example")
    return [{
        "input": "No input available",
        "output": "No output available",
        "explanation": "Failed to parse examples from data"
    }]

async def load_questions_from_csv(file_path: str = CSV_FILE_PATH) -> List[Question]:
    try:
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found at: {file_path}")
            return []
        
        logger.info(f"Loading questions from CSV: {file_path}")
        try:
            df = read_csv_with_retry(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV after retries: {e}")
            return []
        
        logger.info(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")

        expected_columns = ['id', 'title', 'description', 'examples', 'difficultylevel']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {list(df.columns)}")
            return []

        questions = []
        for index, row in df.iterrows():
            try:
                if pd.isna(row['id']) or pd.isna(row['title']) or pd.isna(row['examples']):
                    logger.warning(f"Skipping row {index}: Missing critical data")
                    continue
                examples_str = str(row['examples']).strip()
                try:
                    examples_data = extract_examples_safely(examples_str)
                except Exception as e:
                    logger.error(f"Row {index}: All JSON parsing failed - {e}")
                    continue

                examples = []
                if isinstance(examples_data, list):
                    for example_data in examples_data:
                        if isinstance(example_data, dict):
                            example = Example(
                                input=str(example_data.get('input', '')),
                                output=str(example_data.get('output', '')),
                                explanation=example_data.get('explanation', '')
                            )
                            examples.append(example)
                else:
                    logger.warning(f"Row {index}: Examples is not a list")
                    continue

                if not examples:
                    logger.warning(f"Row {index}: No valid examples found")
                    continue

                question = Question(
                    id=int(float(row['id'])),
                    title=str(row['title']).strip(),
                    description=str(row['description']).strip(),
                    examples=examples,
                    difficultylevel=str(row['difficultylevel']).strip()
                )
                questions.append(question)
                logger.debug(f"Successfully loaded question {question.id}: {question.title}")
            except Exception as e:
                logger.error(f"Error processing row {index}: {e}")
                continue

        logger.info(f"Successfully loaded {len(questions)} questions from CSV")
        return questions

    except Exception as e:
        logger.error(f"Error loading questions from CSV: {e}", exc_info=True)
        return []

async def get_question_by_id(question_id: int) -> Optional[Question]:
    try:
        questions = await load_questions_from_csv()
        for question in questions:
            if question.id == question_id:
                logger.info(f"Found question {question_id}: {question.title}")
                return question
        logger.warning(f"Question with ID {question_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting question by ID {question_id}: {e}")
        return None

async def get_random_question(difficulty: Optional[str] = None) -> Optional[Question]:
    try:
        questions = await load_questions_from_csv()
        if not questions:
            logger.error("No questions available")
            return None
        if difficulty:
            filtered_questions = [q for q in questions if q.difficultylevel.lower() == difficulty.lower()]
            if not filtered_questions:
                logger.warning(f"No questions found for difficulty: {difficulty}")
                selected_question = random.choice(questions)
                logger.info(f"Returning random question as fallback: {selected_question.title}")
                return selected_question
            questions = filtered_questions
        selected_question = random.choice(questions)
        logger.info(f"Selected random question: {selected_question.title} (Difficulty: {selected_question.difficultylevel})")
        return selected_question
    except Exception as e:
        logger.error(f"Error getting random question: {e}")
        return None

async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
    try:
        questions = await load_questions_from_csv()
        filtered_questions = [q for q in questions if q.difficultylevel.lower() == difficulty.lower()]
        logger.info(f"Found {len(filtered_questions)} questions for difficulty: {difficulty}")
        return filtered_questions
    except Exception as e:
        logger.error(f"Error getting questions by difficulty: {e}")
        return []

async def get_all_questions() -> List[Question]:
    try:
        questions = await load_questions_from_csv()
        logger.info(f"Retrieved all {len(questions)} questions")
        return questions
    except Exception as e:
        logger.error(f"Error getting all questions: {e}")
        return []

def validate_csv_structure(file_path: str = CSV_FILE_PATH) -> bool:
    try:
        df = read_csv_with_retry(file_path)
        required_columns = ['id', 'title', 'description', 'examples', 'difficultylevel']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        for index, examples in df['examples'].head(5).items():
            try:
                extract_examples_safely(str(examples))
            except Exception:
                logger.error(f"Invalid JSON in examples column at row {index}")
                return False
        logger.info("CSV structure validation passed")
        return True
    except Exception as e:
        logger.error(f"Error validating CSV structure: {e}")
        return False

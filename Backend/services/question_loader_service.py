# question_loader_service.py - Complete version with all required functions

import pandas as pd
import json
import os
import csv
import re
import random
from typing import List, Optional
from ..models.code_evaluation_model import Question, Example
from ..logging_config import logger

CSV_FILE_PATH = "Backend/data/formatted_problems.csv"

def repair_json_string(json_str: str) -> str:
    """
    Attempt to repair common JSON formatting issues
    """
    try:
        # Remove extra quotes around field names
        json_str = re.sub(r'"([^"]+)""', r'"\1"', json_str)
        
        # Fix common escaping issues
        json_str = json_str.replace('\\"', '"')  # Fix escaped quotes
        json_str = json_str.replace('\\\\', '\\')  # Fix double escaping
        
        # Fix unterminated strings by adding missing quotes at line breaks
        lines = json_str.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If line ends with comma but no quote, might need quote
            if line.endswith(',') and line.count('"') % 2 == 1:
                # Find the last quote and add closing quote before comma
                last_quote_idx = line.rfind('"')
                if last_quote_idx > 0:
                    line = line[:last_quote_idx+1] + '"' + line[last_quote_idx+1:]
            
            fixed_lines.append(line)
        
        json_str = '\n'.join(fixed_lines)
        
        # Fix missing commas between objects
        json_str = re.sub(r'}\s*{', '}, {', json_str)
        
        # Fix incomplete JSON structures
        if json_str.strip().endswith(','):
            json_str = json_str.strip()[:-1]  # Remove trailing comma
        
        # Ensure proper array structure
        if not json_str.strip().startswith('['):
            json_str = '[' + json_str
        if not json_str.strip().endswith(']'):
            json_str = json_str + ']'
        
        return json_str
        
    except Exception as e:
        logger.warning(f"JSON repair failed: {e}")
        return json_str

def extract_examples_safely(json_str: str) -> List[dict]:
    """
    Extract examples with multiple fallback strategies
    """
    # Strategy 1: Try parsing as-is
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try repairing JSON
    try:
        repaired_json = repair_json_string(json_str)
        return json.loads(repaired_json)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Extract manually using regex
    try:
        examples = []
        
        # Find all input/output pairs using regex
        input_pattern = r'"input":\s*"([^"]*(?:\\.[^"]*)*)"'
        output_pattern = r'"output":\s*"([^"]*(?:\\.[^"]*)*)"'
        explanation_pattern = r'"explanation":\s*"([^"]*(?:\\.[^"]*)*)"'
        
        inputs = re.findall(input_pattern, json_str)
        outputs = re.findall(output_pattern, json_str)
        explanations = re.findall(explanation_pattern, json_str)
        
        # Match inputs with outputs
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
    
    # Strategy 4: Create minimal example
    logger.warning("All parsing strategies failed, creating minimal example")
    return [{
        "input": "No input available",
        "output": "No output available", 
        "explanation": "Failed to parse examples from data"
    }]

async def load_questions_from_csv(file_path: str = CSV_FILE_PATH) -> List[Question]:
    """
    Load questions from CSV file and convert to Question objects with robust error handling
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found at: {file_path}")
            return []
        
        # Read CSV file with robust parsing options
        logger.info(f"Loading questions from CSV: {file_path}")
        
        try:
            # Try standard pandas read
            df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
        except Exception as e:
            logger.error(f"Failed to read CSV with pandas: {e}")
            return []
        
        logger.info(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
        
        # Validate required columns exist
        expected_columns = ['id', 'title', 'description', 'examples', 'difficultylevel']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            logger.info(f"Available columns: {list(df.columns)}")
            return []
        
        questions = []
        
        for index, row in df.iterrows():
            try:
                # Skip rows with missing critical data
                if pd.isna(row['id']) or pd.isna(row['title']) or pd.isna(row['examples']):
                    logger.warning(f"Skipping row {index}: Missing critical data")
                    continue
                
                # Clean and parse the examples JSON string
                examples_str = str(row['examples']).strip()
                
                # Parse examples JSON with safety measures
                try:
                    examples_data = extract_examples_safely(examples_str)
                except Exception as e:
                    logger.error(f"Row {index}: All JSON parsing failed - {e}")
                    logger.error(f"Problematic JSON: {examples_str[:200]}...")
                    continue
                
                # Convert to Example objects
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
                
                # Create Question object with safe type conversion
                question = Question(
                    id=int(float(row['id'])),  # Handle potential float IDs
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
        
        if not questions:
            logger.error("No valid questions were loaded from CSV")
        
        return questions
        
    except Exception as e:
        logger.error(f"Error loading questions from CSV: {e}", exc_info=True)
        return []

async def get_question_by_id(question_id: int) -> Optional[Question]:
    """
    Get a specific question by its ID from CSV
    """
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
    """
    Get a random question, optionally filtered by difficulty
    """
    try:
        questions = await load_questions_from_csv()
        
        if not questions:
            logger.error("No questions available")
            return None
        
        if difficulty:
            # Filter by difficulty (case-insensitive)
            filtered_questions = [
                q for q in questions 
                if q.difficultylevel.lower() == difficulty.lower()
            ]
            
            if not filtered_questions:
                logger.warning(f"No questions found for difficulty: {difficulty}")
                logger.info(f"Available difficulties: {list(set(q.difficultylevel for q in questions))}")
                # Return a random question from any difficulty as fallback
                selected_question = random.choice(questions)
                logger.info(f"Returning random question as fallback: {selected_question.title}")
                return selected_question
            
            questions = filtered_questions
        
        # Select random question
        selected_question = random.choice(questions)
        logger.info(f"Selected random question: {selected_question.title} (Difficulty: {selected_question.difficultylevel})")
        
        return selected_question
        
    except Exception as e:
        logger.error(f"Error getting random question: {e}")
        return None

async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
    """
    Get all questions filtered by difficulty level
    """
    try:
        questions = await load_questions_from_csv()
        filtered_questions = [
            q for q in questions 
            if q.difficultylevel.lower() == difficulty.lower()
        ]
        
        logger.info(f"Found {len(filtered_questions)} questions for difficulty: {difficulty}")
        return filtered_questions
        
    except Exception as e:
        logger.error(f"Error getting questions by difficulty: {e}")
        return []

async def get_all_questions() -> List[Question]:
    """
    Get all available questions
    """
    try:
        questions = await load_questions_from_csv()
        logger.info(f"Retrieved all {len(questions)} questions")
        return questions
    except Exception as e:
        logger.error(f"Error getting all questions: {e}")
        return []

def validate_csv_structure(file_path: str = CSV_FILE_PATH) -> bool:
    """
    Validate that the CSV has the required columns and proper structure
    """
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip', engine='python')
        
        required_columns = ['id', 'title', 'description', 'examples', 'difficultylevel']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Check if examples column contains valid JSON
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
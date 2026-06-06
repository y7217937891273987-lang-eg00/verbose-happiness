"""Input validation utilities"""

import re
from typing import Tuple


def validate_prompt(prompt: str, min_length: int = 5, max_length: int = 5000) -> Tuple[bool, str]:
    """
    Validate user prompt.
    
    Returns:
        (is_valid, error_message)
    """
    if not prompt or not isinstance(prompt, str):
        return False, "Prompt must be a non-empty string"
    
    prompt = prompt.strip()
    
    if len(prompt) < min_length:
        return False, f"Prompt must be at least {min_length} characters"
    
    if len(prompt) > max_length:
        return False, f"Prompt cannot exceed {max_length} characters"
    
    return True, ""


def validate_task(task_description: str) -> Tuple[bool, str]:
    """
    Validate task description.
    
    Returns:
        (is_valid, error_message)
    """
    is_valid, msg = validate_prompt(task_description, min_length=10, max_length=10000)
    return is_valid, msg

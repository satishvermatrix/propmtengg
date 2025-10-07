"""
Utility functions for token counting and text processing.
"""
import tiktoken


def count_tokens(text, model="gpt-3.5-turbo"):
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4


def truncate_text_to_token_limit(text, max_tokens=15000, model="gpt-3.5-turbo"):
    """Truncate text to fit within token limit, leaving room for prompts"""
    token_count = count_tokens(text, model)
    
    if token_count <= max_tokens:
        return text, token_count
    
    # If text is too long, truncate it
    # We'll use a simple character-based truncation as a fallback
    # A rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    truncated_text = text[:max_chars]
    
    # Try to end at a sentence boundary if possible
    last_period = truncated_text.rfind('.')
    last_newline = truncated_text.rfind('\n')
    last_space = truncated_text.rfind(' ')
    
    # Find the best break point
    break_point = max(last_period, last_newline, last_space)
    if break_point > max_chars * 0.8:  # Only use break point if it's not too far back
        truncated_text = truncated_text[:break_point + 1]
    
    final_token_count = count_tokens(truncated_text, model)
    return truncated_text, final_token_count

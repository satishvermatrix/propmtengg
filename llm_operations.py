"""
LLM operations for prompt generation and document summarization.
"""
import os
from openai import OpenAI
from utils import count_tokens, truncate_text_to_token_limit


class LLMOperations:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_summarization_prompt(self, document_content):
        """Generate a summarization prompt using LLM based on document content"""
        try:
            # Truncate document content to fit within token limits
            # Leave room for system prompt and user prompt (about 1000 tokens)
            truncated_content, token_count = truncate_text_to_token_limit(
                document_content, max_tokens=12000
            )
            
            # Create a prompt to generate a summarization prompt
            system_prompt = """You are an expert at creating effective summarization prompts. 
            Based on the document content provided, generate a comprehensive prompt that will help an LLM 
            create a high-quality summary. The prompt should include:
            1. Clear instructions for summarization
            2. Key points to focus on
            3. Desired output format
            4. Length requirements
            5. Any specific aspects to emphasize or avoid"""
            
            user_prompt = f"""Please create a detailed summarization prompt for the following document content:

            Document Content ({token_count} tokens):
            {truncated_content}

            Generate a comprehensive prompt that will help an LLM create an effective summary of this document."""
            
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating summarization prompt: {str(e)}"
    
    def summarize_document_with_prompt(self, document_content, summarization_prompt):
        """Summarize the document using the generated prompt"""
        try:
            # Truncate document content to fit within token limits
            # Leave room for system prompt, user prompt, and response (about 2000 tokens)
            truncated_content, token_count = truncate_text_to_token_limit(
                document_content, max_tokens=10000
            )
            
            # Check if document was truncated
            truncation_warning = ""
            if token_count < count_tokens(document_content):
                truncation_warning = f"\n\n[Note: Document was truncated from {count_tokens(document_content)} to {token_count} tokens to fit context limits]"
            
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are an expert document summarizer. Follow the provided prompt carefully to create a comprehensive summary."},
                    {"role": "user", "content": f"{summarization_prompt}\n\nDocument to summarize ({token_count} tokens):\n{truncated_content}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content
            return summary + truncation_warning
            
        except Exception as e:
            return f"Error summarizing document: {str(e)}"
    
    def generate_with_llm(self, role, task, instruction, context, examples, reasoning_steps, delimiters):
        """Generate a response using OpenAI LLM based on the combined prompt"""
        try:
            # Combine all inputs into a structured prompt
            combined_prompt = self.combine_inputs(role, task, instruction, context, examples, reasoning_steps, delimiters)
            
            if not combined_prompt.strip():
                return "Please fill in at least one field to generate a prompt.", combined_prompt
            
            # Make OpenAI API call
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates well-structured prompts based on the given components."},
                    {"role": "user", "content": f"Please generate an improved and well-structured prompt based on these components:\n\n{combined_prompt}"}
                ],
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
            )
            
            llm_response = response.choices[0].message.content
            return llm_response, combined_prompt
            
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            return error_msg, self.combine_inputs(role, task, instruction, context, examples, reasoning_steps, delimiters)
    
    def combine_inputs(self, role, task, instruction, context, examples, reasoning_steps, delimiters):
        """Combine all input components into a structured prompt"""
        prompt_parts = []
        
        if role.strip():
            prompt_parts.append(f"Role/Objective: {role}")
        
        if task.strip():
            prompt_parts.append(f"Task: {task}")
        
        if instruction.strip():
            prompt_parts.append(f"Instruction: {instruction}")
        
        if context.strip():
            prompt_parts.append(f"Context: {context}")
        
        if examples.strip():
            prompt_parts.append(f"Examples: {examples}")
        
        if reasoning_steps.strip():
            prompt_parts.append(f"Reasoning Steps: {reasoning_steps}")
        
        if delimiters.strip():
            prompt_parts.append(f"Delimiters/Structured Output: {delimiters}")
        
        return "\n\n".join(prompt_parts)

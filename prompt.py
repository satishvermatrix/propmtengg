import gradio as gr
import os
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import PyPDF2
import docx
import pandas as pd
from io import StringIO
import tiktoken

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def extract_text_from_file(file_path):
    """Extract text content from various file formats"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        elif file_extension in ['.csv']:
            df = pd.read_csv(file_path)
            return df.to_string()
        
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return df.to_string()
        
        else:
            return f"Unsupported file format: {file_extension}"
    
    except Exception as e:
        return f"Error reading file: {str(e)}"

def generate_summarization_prompt(document_content):
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
        
        response = client.chat.completions.create(
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

def summarize_document_with_prompt(document_content, summarization_prompt):
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
        
        response = client.chat.completions.create(
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

def process_uploaded_document(file):
    """Process uploaded document and return extracted text"""
    if file is None:
        return "No file uploaded", "", ""
    
    try:
        # Extract text from the uploaded file
        document_content = extract_text_from_file(file.name)
        
        if document_content.startswith("Error") or document_content.startswith("Unsupported"):
            return document_content, "", ""
        
        # Add token count information to the document content display
        token_count = count_tokens(document_content)
        document_with_info = f"Document Content ({token_count} tokens):\n\n{document_content}"
        
        # Generate summarization prompt
        summarization_prompt = generate_summarization_prompt(document_content)
        
        # Generate summary using the prompt
        summary = summarize_document_with_prompt(document_content, summarization_prompt)
        
        return document_with_info, summarization_prompt, summary
        
    except Exception as e:
        return f"Error processing document: {str(e)}", "", ""

def combine_inputs(role, task, instruction, context, examples, reasoning_steps, delimiters):
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

def generate_with_llm(role, task, instruction, context, examples, reasoning_steps, delimiters):
    """Generate a response using OpenAI LLM based on the combined prompt"""
    try:
        # Combine all inputs into a structured prompt
        combined_prompt = combine_inputs(role, task, instruction, context, examples, reasoning_steps, delimiters)
        
        if not combined_prompt.strip():
            return "Please fill in at least one field to generate a prompt.", combined_prompt
        
        # Make OpenAI API call
        response = client.chat.completions.create(
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
        return error_msg, combine_inputs(role, task, instruction, context, examples, reasoning_steps, delimiters)

with gr.Blocks() as prompt_generator:
    gr.Markdown("# Prompt Generator & Document Summarizer")
    gr.Markdown("This is a prompt generator for the LLM and a document summarization tool.")
    gr.Markdown("Use the options below to generate prompts or upload documents for summarization.")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Role/Objective")
            gr.Markdown("*Clearly define the persona or role the LLM should adopt and its overall goal. This helps set the stage for the desired behavior.*")
            role = gr.Textbox(label="Role_Objective", placeholder="You are an expert technical writer...")
            
            gr.Markdown("### Task")
            gr.Markdown("*Describe the specific task or problem the AI needs to solve.*")
            gr.Markdown("*Use '###' to set tone/style and what to exclude.*")
            task = gr.Textbox(label="Task", placeholder="Explain complex AI concepts...")
            
            gr.Markdown("### Instruction")
            gr.Markdown("*Provide detailed instructions on how the AI should approach the task.*")
            instruction = gr.Textbox(label="Instruction", placeholder="Provide clear, step-by-step explanations...")
            
            gr.Markdown("### Context")
            gr.Markdown("*Add relevant background information, constraints, or situational details.*")
            context = gr.Textbox(label="Context", placeholder="The audience consists of...")
        
        with gr.Column():
            gr.Markdown("### Few-Shot Prompting")
            gr.Markdown("*Provide examples to guide the AI's response format and style.*")
            examples = gr.Textbox(label="FewShotPrompting", placeholder="Example 1: ...")
            
            gr.Markdown("### Chain of Thought (CoT)")
            gr.Markdown("*Specify reasoning steps or thought process the AI should follow.*")
            reasoning_steps = gr.Textbox(label="COT", placeholder="Step 1: ...")
            
            gr.Markdown("### Delimiters & Structured Output")
            gr.Markdown("*Define output format, delimiters, and structure requirements.*")
            delimiters = gr.Textbox(label="Delimiters_StructuredOutput", placeholder="Use ### to separate sections...")
    
    # Output textboxes
    gr.Markdown("## Output")
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Combined Prompt")
            gr.Markdown("*Shows the raw combination of all your inputs. Updates in real-time as you type.*")
            output = gr.Textbox(label="Combined Prompt", lines=8, interactive=False)
            
            gr.Markdown("### LLM Generated Response")
            gr.Markdown("*AI-enhanced version of your prompt, optimized for better results.*")
            llm_output = gr.Textbox(label="LLM Generated Response", lines=8, interactive=False)
        
        with gr.Column():
            gr.Markdown("### Actions")
            gr.Markdown("*Use these buttons to generate your prompts.*")
            # Buttons
            generate_btn = gr.Button("Generate Prompt", variant="primary")
            llm_btn = gr.Button("Generate with LLM", variant="secondary")
            
            # Status indicator
            status = gr.Textbox(label="Status", interactive=False, visible=False)
    
    # Connect the generate button to show combined prompt
    generate_btn.click(
        fn=combine_inputs,
        inputs=[role, task, instruction, context, examples, reasoning_steps, delimiters],
        outputs=output
    )
    
    # Connect the LLM button to generate with OpenAI
    llm_btn.click(
        fn=generate_with_llm,
        inputs=[role, task, instruction, context, examples, reasoning_steps, delimiters],
        outputs=[llm_output, output]
    )
    
    # Also update the output when any input changes (for real-time preview)
    for input_component in [role, task, instruction, context, examples, reasoning_steps, delimiters]:
        input_component.change(
            fn=combine_inputs,
            inputs=[role, task, instruction, context, examples, reasoning_steps, delimiters],
            outputs=output
        )
    
    # Document Upload and Summarization Section
    gr.Markdown("---")
    gr.Markdown("## Document Upload & Summarization")
    gr.Markdown("Upload a document to extract text and generate an AI-powered summary.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Upload Document")
            gr.Markdown("*Supported formats: PDF, DOCX, TXT, CSV, XLSX*")
            file_upload = gr.File(
                label="Upload Document",
                file_types=[".pdf", ".docx", ".txt", ".csv", ".xlsx", ".xls"]
            )
            process_btn = gr.Button("Process Document", variant="primary")
        
        with gr.Column():
            gr.Markdown("### Document Processing Results")
            gr.Markdown("*Results will appear here after processing*")
            document_content = gr.Textbox(
                label="Extracted Document Content",
                lines=8,
                interactive=False,
                placeholder="Document content will appear here..."
            )
            summarization_prompt = gr.Textbox(
                label="Generated Summarization Prompt",
                lines=6,
                interactive=False,
                placeholder="AI-generated summarization prompt will appear here..."
            )
            document_summary = gr.Textbox(
                label="Document Summary",
                lines=8,
                interactive=False,
                placeholder="AI-generated summary will appear here..."
            )
    
    # Connect the process button to the document processing function
    process_btn.click(
        fn=process_uploaded_document,
        inputs=[file_upload],
        outputs=[document_content, summarization_prompt, document_summary]
    )

prompt_generator.launch(server_port=7860)

    
    
"""
Gradio interface components for the prompt generator and document summarizer.
"""
import gradio as gr
from llm_operations import LLMOperations
from document_processor import extract_text_from_file
from utils import count_tokens


class GradioInterface:
    def __init__(self):
        self.llm_ops = LLMOperations()
    
    def process_uploaded_document(self, file):
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
            summarization_prompt = self.llm_ops.generate_summarization_prompt(document_content)
            
            # Generate summary using the prompt
            summary = self.llm_ops.summarize_document_with_prompt(document_content, summarization_prompt)
            
            return document_with_info, summarization_prompt, summary
            
        except Exception as e:
            return f"Error processing document: {str(e)}", "", ""
    
    def create_interface(self):
        """Create and return the Gradio interface"""
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
                fn=self.llm_ops.combine_inputs,
                inputs=[role, task, instruction, context, examples, reasoning_steps, delimiters],
                outputs=output
            )
            
            # Connect the LLM button to generate with OpenAI
            llm_btn.click(
                fn=self.llm_ops.generate_with_llm,
                inputs=[role, task, instruction, context, examples, reasoning_steps, delimiters],
                outputs=[llm_output, output]
            )
            
            # Also update the output when any input changes (for real-time preview)
            for input_component in [role, task, instruction, context, examples, reasoning_steps, delimiters]:
                input_component.change(
                    fn=self.llm_ops.combine_inputs,
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
                fn=self.process_uploaded_document,
                inputs=[file_upload],
                outputs=[document_content, summarization_prompt, document_summary]
            )

        return prompt_generator

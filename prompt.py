import gradio as gr
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    gr.Markdown("# Prompt Generator")
    gr.Markdown("This is a prompt generator for the LLM.")
    gr.Markdown("Use the options below to generate a prompt for the LLM.")

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

prompt_generator.launch(server_port=7860)

    
    
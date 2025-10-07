"""
Main application file for the Prompt Generator & Document Summarizer.
This file imports and orchestrates the modular components.
"""
import os
from dotenv import load_dotenv
from gradio_interface import GradioInterface

# Load environment variables
load_dotenv()

def main():
    """Main function to run the application"""
    # Create the Gradio interface
    interface = GradioInterface()
    prompt_generator = interface.create_interface()
    
    # Launch the application
    prompt_generator.launch(server_port=7860)

if __name__ == "__main__":
    main()
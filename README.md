# Prompt Generator & Document Summarizer

A comprehensive Gradio-based application that combines prompt engineering tools with AI-powered document summarization capabilities. This tool helps you create effective prompts for LLMs and automatically summarize documents using AI-generated prompts.

## Features

### 🎯 Prompt Generator
- **Interactive Prompt Builder**: Create structured prompts using multiple components
- **Real-time Preview**: See your combined prompt as you type
- **AI Enhancement**: Generate improved prompts using OpenAI's LLM
- **Component-based Design**: Build prompts using:
  - Role/Objective definition
  - Task specification
  - Detailed instructions
  - Context information
  - Few-shot examples
  - Chain of thought reasoning
  - Output formatting and delimiters

### 📄 Document Summarizer
- **Multi-format Support**: Upload PDF, DOCX, TXT, CSV, and Excel files
- **Intelligent Text Extraction**: Automatically extract text from various document formats
- **AI-Generated Summarization Prompts**: The system creates custom prompts based on document content
- **Token-Aware Processing**: Automatically handles documents within 16,385 token context limits
- **Smart Truncation**: Preserves document quality by breaking at natural boundaries

## Installation

### Prerequisites
- Python 3.11 or higher
- UV package manager

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd prompt_engg
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
Create a `.env` file in the project root with your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
```

## Usage

### Running the Application
```bash
uv run python prompt.py
```

The application will start on `http://localhost:7860`

### Using the Prompt Generator

1. **Fill in the Components**:
   - **Role/Objective**: Define the AI's persona and goal
   - **Task**: Describe what the AI needs to accomplish
   - **Instruction**: Provide detailed step-by-step guidance
   - **Context**: Add background information and constraints
   - **Few-Shot Examples**: Include examples to guide the AI's response
   - **Chain of Thought**: Specify reasoning steps
   - **Delimiters**: Define output format and structure

2. **Generate Prompts**:
   - Click "Generate Prompt" to see the combined prompt
   - Click "Generate with LLM" to get an AI-enhanced version

### Using the Document Summarizer

1. **Upload a Document**:
   - Supported formats: PDF, DOCX, TXT, CSV, XLSX, XLS
   - Click "Process Document" to analyze the file

2. **Review Results**:
   - **Extracted Content**: See the document text with token count
   - **Generated Prompt**: AI-created summarization prompt
   - **Summary**: AI-generated document summary

## Technical Details

### Token Management
- **Context Limit**: Respects 16,385 token context limit
- **Smart Truncation**: Documents are truncated to fit within limits while preserving content quality
- **Token Counting**: Uses tiktoken for accurate token estimation
- **Warning System**: Users are notified when documents are truncated

### Supported File Formats
- **PDF**: Extracts text using PyPDF2
- **DOCX**: Processes Word documents using python-docx
- **TXT**: Plain text files
- **CSV**: Comma-separated values using pandas
- **Excel**: XLSX and XLS files using pandas and openpyxl

### Dependencies
- `gradio>=4.0.0` - Web interface
- `openai>=1.0.0` - OpenAI API integration
- `tiktoken>=0.5.0` - Token counting
- `PyPDF2>=3.0.0` - PDF processing
- `python-docx>=1.1.0` - Word document processing
- `pandas>=2.0.0` - Data processing
- `openpyxl>=3.1.0` - Excel file support
- `python-dotenv>=1.0.0` - Environment variable management

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Response creativity (default: 0.7)
- `OPENAI_MAX_TOKENS`: Maximum response length (default: 1000)

### Token Limits
- **Prompt Generation**: 12,000 tokens for document content
- **Summarization**: 10,000 tokens for document content
- **Total Context**: 16,385 tokens (OpenAI limit)

## Architecture

### Modular Structure
The application is organized into focused modules for better maintainability:

- **`prompt.py`**: Main application orchestrator
- **`utils.py`**: Token counting and text processing utilities
- **`document_processor.py`**: Document text extraction from various formats
- **`llm_operations.py`**: LLM API calls and prompt generation
- **`gradio_interface.py`**: UI components and user interactions

### Core Functions
- `extract_text_from_file()`: Multi-format text extraction
- `count_tokens()`: Accurate token counting with tiktoken
- `truncate_text_to_token_limit()`: Smart document truncation
- `generate_summarization_prompt()`: AI-powered prompt generation
- `summarize_document_with_prompt()`: Document summarization
- `process_uploaded_document()`: End-to-end document processing

### UI Components
- **Prompt Generator Interface**: Interactive form with real-time preview
- **Document Upload Section**: File upload with processing controls
- **Results Display**: Three-panel output showing content, prompt, and summary

### Benefits of Modular Design
- **Separation of Concerns**: Each module has a single responsibility
- **Reusability**: Utility functions shared across modules
- **Testability**: Independent testing of each component
- **Scalability**: Easy to extend with new features
- **Maintainability**: Clear boundaries and logical organization

## Error Handling

The application includes comprehensive error handling for:
- Unsupported file formats
- API connection issues
- Token limit exceeded
- File processing errors
- Invalid document content

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the error messages in the application
2. Verify your OpenAI API key is valid
3. Ensure your documents are in supported formats
4. Check that documents are not corrupted

## Future Enhancements

- Support for additional file formats
- Batch document processing
- Custom summarization templates
- Export functionality for generated prompts
- Integration with other LLM providers
